from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core.schema import MetadataMode, NodeRelationship, RelatedNodeInfo, TextNode, IndexNode
from llama_index.core.node_parser import SentenceSplitter, SentenceWindowNodeParser
from llama_index.core.readers.base import BaseReader
import re
import os
import json
import uuid
import pandas as pd
import numpy as np
from typing import List
from collections import defaultdict
from app import PROJECT_PATH

DATA_PATH = os.path.join(PROJECT_PATH, "data/llm_analyze_data")

def get_value(dictionary, key):
    # Get the value associated with the key, default to '' if key is not found
    value = dictionary.get(key)

    # Return '' if value is None, otherwise return the value
    return '' if value is None else value

def del_key(dictionary, key):
    # Check if the key exists in the dictionary
    dictionary.pop(key, None)
    return dictionary

def classify_documents(documents):
    """
    Classifies a list of documents into categories based on their file type.

    Args:
        documents (list): List of Document objects with metadata.

    Returns:
        dict: Dictionary with categorized documents.
    """
    # Initialize a defaultdict to store categorized documents
    categorized_docs = defaultdict(list)

    # Iterate through the documents and classify them by file type
    for document in documents:
        file_type = document.metadata.get("file_type", "unknown")
        categorized_docs[file_type].append(document)

    # Convert defaultdict to regular dictionary for output
    return dict(categorized_docs)

class MyFileReader(BaseReader):
    def __init__(self):
        super().__init__()

    def load_data(self, file, extra_info=None):
        with open(file, "r") as f:
            text = f.read()

        json_data = json.loads(text)
        file_type = self._get_file_type(file.name)
        metadata = self._extract_metadata(json_data, file_type)

        if extra_info:
            extra_info.update(metadata)

        text = self._get_text_content(json_data, file_type)
        return [Document(text=text, metadata=extra_info or {})]

    def _get_file_type(self, file_name):
        if file_name.startswith("image"):
            return "image"
        elif file_name.startswith("document"):
            return "document"
        elif file_name.startswith("audio"):
            return "audio"
        elif file_name.startswith("video"):
            return "video"
        else:
            raise ValueError("Unsupported file type")

    def _extract_metadata(self, json_data, file_type):
        metadata = {
            "file_id": json_data.get("id"),
            "md5": json_data.get("md5"),
            "file_name": json_data.get("originalName"),
            "file_extension": json_data.get("extension"),
            "file_type": file_type,
            "file_size": json_data.get("size"),
            "height": json_data.get("height"),
            "width": json_data.get("width"),
            "duration": json_data.get("duration"),
            "density": json_data.get("density"),
            "channels": json_data.get("channels"),
            "category": json_data.get("category"),
            #"people": json_data.get("people"),
            #"organizations": json_data.get("organizations"),
            "narrationStt": self.processing_narrationStt(json_data.get("narrationStt"))
        }

        if file_type in ["audio", "video"]:
            metadata["stt_summary"] = json_data.get("stt", {}).get("sttSummary")
        if file_type == "document":
            metadata["description"] = json_data.get("desc")

        return metadata

    def _get_text_content(self, json_data, file_type):
        if file_type == "image":
            return json_data.get("desc") or ""
        elif file_type == "document":
            return json_data.get("textData") or ""
        elif file_type in ["audio", "video"]:
            return json_data.get("stt", {}).get("sttData") or ""
        else:
            return ""

    def processing_narrationStt(self, lst):
        if lst is None:
            return ""
        else:
            narrationStt = {}
            for item in lst:
                text = []
                narration = json.loads(item["sttData"])
                for entry in narration:
                    text.append(entry["content"])
                narrationStt["user_" + str(item["id"])] = text
            return str(narrationStt)

def read_file(path):
    reader = SimpleDirectoryReader(input_dir=path, file_extractor={".json": MyFileReader()})
    documents = reader.load_data()
    for doc in documents:
        doc.excluded_embed_metadata_keys = []
        doc.excluded_llm_metadata_keys = []
        #doc.id_ = doc.metadata["id"]
    return documents

class ImageConstructor:
    def __init__(self, documents):
        self.documents = documents
        self.chunk_size = 512
        self.chunk_overlap = 10
        self.separator = "\n\n"

    def construct_nodes(self):
        text_parser = SentenceSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap, separator=self.separator)
        img_nodes = text_parser.get_nodes_from_documents(self.documents)
        #for node in img_nodes:
            #node.id_ = node.metadata["id"]
        return img_nodes
    
class AudioVideoNodeConstructor:
    def __init__(self, documents):
        self.documents = documents
        self.document_map = {}
        self.parrent_chunk = {}
        self.child_chunk = {}
        self.nodes_map = {}
        self.parrent_nodes = {}

    def process_stt(self, json_string):
        # Parse the JSON string
        data = json.loads(json_string)

        # Initialize the list to store the formatted data
        formatted_data = []

        # Iterate through each item in the data
        for item in data:
            # Split the "time" field into "start_time" and "end_time"
            times = item["time"].split(" --> ")
            start_time = times[0]
            end_time = times[1]

            # Extract the "content"
            content = item["content"]

            # Extract the "speaker"
            speaker = item["speaker"]

            # Create a dictionary with the formatted data
            formatted_item = {
                "start_time": start_time,
                "end_time": end_time,
                "content": content,
                "speaker": speaker
            }

            # Append the formatted item to the list
            formatted_data.append(formatted_item)

        return formatted_data

    def process_and_construct_chunks(self):
        for doc_idx, page in enumerate(self.documents):
            text = page.text
            metadata = page.metadata

            # Add document to document_map
            #doc_id = metadata.get("id")
            doc_id = page.id_
            self.document_map[doc_id] = page

            desc = get_value(metadata, "description")
            del_key(metadata, "description")

            self.parrent_chunk[doc_idx] = {
                "text": desc,
                "metadata": metadata,
                "id": doc_id
            }

            del_key(metadata, "stt_summary")
            stt = self.process_stt(text)

            if len(stt) == 0:
                self.child_chunk[doc_idx] = {}
                continue
            else:
                self.child_chunk[doc_idx] = []
                for i in range(len(stt)):
                    chunk_metadata = metadata.copy()
                    chunk_metadata["start_time"] = stt[i].get("start_time")
                    chunk_metadata["end_time"] = stt[i].get("end_time")
                    chunk_metadata["speaker"] = stt[i].get("speaker")
                    cur_text_chunks = stt[i].get("content")

                    self.child_chunk[doc_idx].append({
                        "text": cur_text_chunks,
                        "metadata": chunk_metadata,
                        #"id": doc_id + '-' + str(i + 1)
                    })

    def create_nodes_from_chunks(self):
        for idx in self.parrent_chunk.keys():
            parrent_node = TextNode(
                text=self.parrent_chunk[idx]["text"],
                metadata=self.parrent_chunk[idx]["metadata"],
                id_=str(self.parrent_chunk[idx]["id"])
            )
            self.parrent_nodes[parrent_node.id_] = parrent_node

            if idx not in self.child_chunk or len(self.child_chunk[idx]) == 0:
                self.nodes_map[parrent_node.id_] = []
            else:
                child_nodes = []
                for i, chunk in enumerate(self.child_chunk[idx]):
                    child_node = TextNode(
                        text=chunk["text"],
                        metadata=chunk["metadata"],
                        #id_=chunk["id"]
                    )
                    child_nodes.append(child_node)
                self.nodes_map[parrent_node.id_] = child_nodes

    def index_nodes(self):
        nodes = []

        for node_id in self.nodes_map.keys():
            parrent = self.parrent_nodes[node_id]
            child = self.nodes_map[node_id]
            child_lst = []

            # Add SOURCE relationship
            document = self.document_map.get(parrent.id_)
            if document:
                document.id_ = str(uuid.uuid4())
                parrent.relationships[NodeRelationship.SOURCE] = document.as_related_node_info()

            for i in range(len(child)):
                #child[i].id_ = str(uuid.uuid4())
                child[i].relationships[NodeRelationship.PARENT] = parrent.as_related_node_info()

                if i == 0:
                    #if len(child) > 1:
                    child[i].relationships[NodeRelationship.NEXT] = child[0].as_related_node_info()
                elif i == len(child) - 1:
                    child[i].relationships[NodeRelationship.PREVIOUS] = child[i - 1].as_related_node_info()
                else:
                    child[i].relationships[NodeRelationship.NEXT] = child[i + 1].as_related_node_info()
                    child[i].relationships[NodeRelationship.PREVIOUS] = child[i - 1].as_related_node_info()

                child_lst.append(child[i].as_related_node_info())

            parrent.relationships[NodeRelationship.CHILD] = child_lst
            nodes.append(parrent)
            nodes.extend(child)

        return nodes

    def construct_nodes(self):
        self.process_and_construct_chunks()
        self.create_nodes_from_chunks()
        return self.index_nodes()
    
class DocumentConstructor:
    def __init__(self, documents):
        self.documents = documents
        self.chunk_size = 1024
        self.chunk_overlap = 10
        self.separator = "\n\n"
        self.document_map = {}
        self.nodes_map = {}
        self.parrent_nodes = {}
        self.id_map = {}

    def process_and_construct_chunks(self):
        """Processes documents into chunks and constructs nodes from them."""
        text_parser = SentenceSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap, separator=self.separator)
        doc_nodes = text_parser.get_nodes_from_documents(self.documents)
        for doc in self.documents:
            self.id_map[doc.metadata["file_id"]] = doc.id_

        for node in doc_nodes:
            node.id_ = self.id_map[node.metadata["file_id"]]
            node.relationships = {}
            if node.id_ in self.nodes_map:
                self.nodes_map[node.id_].append(node)
            else:
                self.nodes_map[node.id_] = [node]

    def create_parrent_node(self):
        """Creates parent nodes from the documents."""
        for page in self.documents:
            self.document_map[page.id_] = page
            metadata = page.metadata
            desc = get_value(metadata, "description")
            del_key(metadata, "description")

            parrent_node = TextNode(
                text=desc,
                metadata=metadata,
                id_=page.id_
            )
            self.parrent_nodes[parrent_node.id_] = parrent_node

    def index_nodes(self):
        """Indexes nodes and sets relationships between them."""
        nodes = []

        for node_id in self.nodes_map.keys():
            parrent = self.parrent_nodes[node_id]
            children = self.nodes_map[node_id]

            child_lst = []

            # Add SOURCE relationship
            document = self.document_map.get(parrent.id_)
            if document:
                parrent.id_ = str(uuid.uuid4())
                parrent.relationships[NodeRelationship.SOURCE] = document.as_related_node_info()

            for i, child in enumerate(children):
                child.id_ = str(uuid.uuid4())
                child.relationships[NodeRelationship.PARENT] = parrent.as_related_node_info()

                if i == 0:
                    if len(children) > 1:
                        child.relationships[NodeRelationship.NEXT] = children[i + 1].as_related_node_info()
                elif i == len(children) - 1:
                    child.relationships[NodeRelationship.PREVIOUS] = children[i - 1].as_related_node_info()
                else:
                    child.relationships[NodeRelationship.NEXT] = children[i + 1].as_related_node_info()
                    child.relationships[NodeRelationship.PREVIOUS] = children[i - 1].as_related_node_info()

                child_lst.append(child.as_related_node_info())

            parrent.relationships[NodeRelationship.CHILD] = child_lst
            nodes.append(parrent)
            nodes.extend(children)

        return nodes

    def construct_nodes(self):
        """Constructs the full set of nodes from the documents."""
        self.process_and_construct_chunks()
        self.create_parrent_node()
        return self.index_nodes()