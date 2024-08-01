from app.models.model import *
import weaviate
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
)
from llama_index.vector_stores.weaviate import WeaviateVectorStore
import os
from app import PROJECT_PATH

print(os.environ.get('WEAVIATE_API_KEY'))
print(os.environ.get('WEAVIATE_URL'))
auth_config = weaviate.AuthApiKey(
    api_key=os.environ.get('WEAVIATE_API_KEY')
)
client = weaviate.Client(
    os.environ.get('WEAVIATE_URL'),
    auth_client_secret=auth_config,
)

def define_vector_store_index(index_name, nodes, llm, embed_model):
    vector_store = WeaviateVectorStore(weaviate_client=client, index_name=index_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        llm=llm,
        embed_model=embed_model
    )