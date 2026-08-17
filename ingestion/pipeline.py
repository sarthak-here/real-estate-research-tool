"""Turn article URLs into an searchable vector store.

Scrape -> split into chunks -> embed -> store in Chroma.
"""

from uuid import uuid4

from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE, get_llm, get_vector_store


def process_urls(urls):
    """Scrape the given urls and load them into the vector store.

    Yields progress strings so the caller can show status as it goes.
    """
    yield "Initializing components..."
    get_llm()
    vector_store = get_vector_store()

    yield "Resetting vector store...✅"
    vector_store.reset_collection()

    yield "Loading data...✅"
    loader = UnstructuredURLLoader(urls=urls)
    data = loader.load()

    yield "Splitting text into chunks...✅"
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=CHUNK_SIZE,
    )
    docs = splitter.split_documents(data)

    yield "Adding chunks to vector database...✅"
    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs, ids=uuids)

    yield f"Done. Indexed {len(docs)} chunks from {len(urls)} url(s).✅"
