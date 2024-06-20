from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.huggingface import HuggingFaceLLM
import os
from app import PROJECT_PATH
import torch

def get_embed_model(model_path="local:finetuned-bge-m3"):
    embed_model = resolve_embed_model(model_path)
    return embed_model


def get_llm(model_name="mistralai/Mistral-7B-Instruct-v0.2",
            temperature=0.1,
            max_new_tokens=512,
            context_window=8000,
            HF_TOKEN = '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'):
    os.environ["HF_TOKEN"] = HF_TOKEN
    llm = HuggingFaceLLM(
    context_window=8000,
    max_new_tokens=4096,
    generate_kwargs={"temperature": 0.7, "do_sample": True},
    model_name="mistralai/Mistral-7B-Instruct-v0.2",
    tokenizer_name="mistralai/Mistral-7B-Instruct-v0.2",
    device_map="cuda",
    tokenizer_kwargs={"max_length": 1024},
    model_kwargs={"torch_dtype": torch.float16}
)
    return llm

embed_model = get_embed_model(model_path="local:finetuned-bge-m3")
llm = get_llm()
