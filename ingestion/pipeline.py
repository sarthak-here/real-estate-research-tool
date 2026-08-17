"""Turn article URLs into a searchable vector store.

Scrape -> split into chunks -> embed -> store in Chroma.

Fetching is done with requests plus unstructured's HTML partitioner rather than
UnstructuredURLLoader. The loader routes through unstructured's auto-detect
partitioner, which segfaults the interpreter on this stack; partitioning the
HTML directly is both stable and faster, and lets us send a real User-Agent so
news sites do not reject the request.
"""

from uuid import uuid4

import requests
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from unstructured.partition.html import partition_html

from config import CHUNK_SIZE, REQUEST_TIMEOUT, USER_AGENT, get_llm, get_vector_store


def load_urls(urls):
    """Fetch each url and return one Document per url, tagged with its source.

    A url that fails is skipped rather than killing the whole batch; the caller
    is told how many succeeded.
    """
    documents, failures = [], []

    for url in urls:
        try:
            response = requests.get(
                url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT}
            )
            response.raise_for_status()
            elements = partition_html(text=response.text)
            text = "\n\n".join(
                element.text for element in elements
                if getattr(element, "text", "") and element.text.strip()
            )
            if not text.strip():
                failures.append((url, "no text extracted"))
                continue
            documents.append(Document(page_content=text, metadata={"source": url}))
        except Exception as exc:  # noqa: BLE001
            failures.append((url, f"{type(exc).__name__}: {exc}"))

    return documents, failures


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
    data, failures = load_urls(urls)
    for url, reason in failures:
        yield f"Skipped {url} ({reason})"
    if not data:
        yield "No content could be loaded from the given url(s)."
        return

    yield "Splitting text into chunks...✅"
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=CHUNK_SIZE,
    )
    docs = splitter.split_documents(data)

    yield "Adding chunks to vector database...✅"
    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs, ids=uuids)

    yield f"Done. Indexed {len(docs)} chunks from {len(data)} url(s).✅"
