"""Shared settings and lazily-built components.

Ingestion and retrieval both need the same LLM and vector store, so they are
built once here and reused rather than re-instantiated per call.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent

CHUNK_SIZE = 1000
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = PROJECT_ROOT / "resources/vectorstore"
COLLECTION_NAME = "real_estate"
RETRIEVE_K = 6
# Rough character budget for retrieved context sent to the model.
MAX_CONTEXT_CHARS = 32000
TEMPERATURE = 0.2
MAX_ANSWER_TOKENS = 1500

REQUEST_TIMEOUT = 30
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)

_llm = None
_vector_store = None


def get_llm():
    global _llm
    if _llm is None:
        # Low temperature: this is factual retrieval, not creative writing.
        # 500 tokens truncated multi-point answers mid-sentence.
        _llm = ChatGroq(model=GROQ_MODEL, temperature=TEMPERATURE, max_tokens=MAX_ANSWER_TOKENS)
    return _llm


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True},
        )
        _vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(VECTORSTORE_DIR),
        )
    return _vector_store


def vector_store_ready() -> bool:
    """True once a vector store has been built in this process."""
    return _vector_store is not None
