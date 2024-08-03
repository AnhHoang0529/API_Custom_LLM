from . import api_blueprint
from flask import Flask, jsonify, request, render_template
from flask_restful import Resource, Api
import logging
import os
from llama_index.core import Settings
from app.database.index import define_vector_store_index
from app.utils.data_reader import *
from app.services.retrieve_assets import construct_router_query_engine, retrieve_files
from app.services.generate_content import generate_content, query_engine_generate
from app import PROJECT_PATH
from app.models.model import llm, embed_model

@api_blueprint.route('/ai/v1/llm/assets/<query>', methods=['GET'])
def get_response_by_query(query):
 query_engine = construct_router_query_engine()
 output = retrieve_files(query_engine, query)
 if output is None:
   return jsonify({ 'error': 'FACE_DESCRIPTOR_FAIL'}), 404
 else:
   print(output)
   return jsonify(output)

@api_blueprint.route('/ai/v1/llm/articles/<query>', methods=['GET'])
def generate_content_by_query(query):
 response = generate_content(query_engine_generate, query)
 if response is None:
   return jsonify({ 'error': 'FACE_DESCRIPTOR_FAIL'}), 404
 else:
   print(response)
   return jsonify(response)


@api_blueprint.route('/ai/v1/llm/data')
def upload():
    # Extract parameters from the request
    file_path = request.args.get('file_path')

    if not file_path:
        return jsonify({"success": False, "error": "Missing file_path parameter"})

    # Construct the full file path
    file_path = os.path.join(PROJECT_PATH, file_path)

    # Read and classify documents
    try:
        documents = read_file(file_path)
        classified_docs = classify_documents(documents)
    except Exception as e:
        logging.exception("Error reading and classifying documents")
        return jsonify({"success": False, "error": str(e)})

    # Map of constructors and their corresponding document types and index names
    constructor_map = {
        'image': (ImageConstructor, "img-index"),
        'audio': (AudioVideoNodeConstructor, "au-index"),
        'video': (AudioVideoNodeConstructor, "vid-index"),
        'document': (DocumentConstructor, "doc-index")
    }

    processed_indices = []

    # Process each document type
    for doc_type, (Constructor, index_name) in constructor_map.items():
        if classified_docs.get(doc_type):
            try:
                constructor = Constructor(classified_docs.get(doc_type))
                nodes = constructor.construct_nodes()
                define_vector_store_index(index_name, nodes, llm, embed_model)
                print(f'Node constructed for {index_name}')
                processed_indices.append(index_name)
            except Exception as e:
                logging.exception(f"Error processing documents for {index_name}")
                return jsonify({"success": False, "error": str(e)})

    if processed_indices:
        return jsonify({"success": True, "processed_indices": processed_indices})

    return jsonify({"success": False, "error": "No valid document types found"})