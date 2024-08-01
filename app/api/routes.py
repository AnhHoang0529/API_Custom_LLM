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
    db = request.args.get('db_name')

    # Construct the full file path
    file_path = os.path.join(PROJECT_PATH, file_path)

    # Read and classify documents
    try:
        documents = read_file(file_path)
        classified_docs = classify_documents(documents)
    except Exception as e:
        logging.exception("Error reading and classifying documents")
        return jsonify({"success": False, "error": str(e)})

    # Map of constructors and their corresponding document types
    constructor_map = {
        'LlamaIndex_img_index': ('image', ImageConstructor),
        'LlamaIndex_au_index': ('audio', AudioVideoNodeConstructor),
        'LlamaIndex_vid_index': ('video', AudioVideoNodeConstructor),
        'LlamaIndex_doc_index': ('document', DocumentConstructor)
    }

    # Check if the provided db name is valid
    if db not in constructor_map:
        return jsonify({"success": False, "error": "Invalid db_name provided"})

    doc_type, Constructor = constructor_map[db]

    # Get the appropriate documents and construct nodes
    try:
        constructor = Constructor(classified_docs.get(doc_type))
        nodes = constructor.construct_nodes()
        define_vector_store_index(db, nodes, llm, embed_model)
        return jsonify({"success": True})
    except Exception as e:
        logging.exception(f"Error processing documents for {db}")
        return jsonify({"success": False, "error": str(e)})