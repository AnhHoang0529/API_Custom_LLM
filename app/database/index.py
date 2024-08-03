from app.models.model import *
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
)
from pinecone import Pinecone, ServerlessSpec, PodSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
import os
import logging
from app import PROJECT_PATH


pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

def define_vector_store_index(index_name, nodes, llm, embed_model):
    try:
        # Check if the index already exists
        existing_indexes = pc.list_indexes().names()
        if index_name not in existing_indexes:
            # Create the index if it doesn't exist
            pc.create_index(
                name=index_name,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        
        # Define the index regardless of whether it was newly created or already existed
        pc_index = pc.Index(index_name)
        pinecone_vector_store = PineconeVectorStore(pinecone_index=pc_index)
        pinecone_storage_context = StorageContext.from_defaults(vector_store=pinecone_vector_store)
        pinecone_index = VectorStoreIndex(nodes, storage_context=pinecone_storage_context, llm=llm, embed_model=embed_model)

        return {"success": True, "index_name": index_name}

    except Exception as e:
        logging.exception(f"Error defining or creating index {index_name}")
        return {"success": False, "error": str(e)}