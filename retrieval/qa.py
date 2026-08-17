"""Answer questions against the indexed articles, with sources.

Sources are read from the metadata of the chunks actually used, not parsed out
of the model's text, so citations reflect what was really retrieved.
"""

from config import (
    MAX_CONTEXT_CHARS,
    RETRIEVE_K,
    get_llm,
    get_vector_store,
    vector_store_ready,
)
from retrieval.prompts import ANSWER_PROMPT, DOCUMENT_PROMPT


def build_summaries(docs):
    """Format retrieved docs for the prompt, staying inside the context budget.

    Returns the formatted text and how many docs fit.
    """
    blocks, used = [], 0
    for doc in docs:
        block = DOCUMENT_PROMPT.format(
            page_content=doc.page_content,
            source=doc.metadata.get("source", "unknown"),
        )
        if used + len(block) > MAX_CONTEXT_CHARS:
            break
        blocks.append(block)
        used += len(block)
    return "\n\n".join(blocks), len(blocks)


def generate_answer(query):
    """Return (answer, sources) for a question. Requires process_urls first."""
    if not vector_store_ready():
        raise RuntimeError("Vector database is not initialized")

    retriever = get_vector_store().as_retriever(search_kwargs={"k": RETRIEVE_K})
    docs = retriever.invoke(query)

    summaries, used_count = build_summaries(docs)
    result = (ANSWER_PROMPT | get_llm()).invoke(
        {"summaries": summaries, "question": query}
    )

    # De-duplicate while preserving retrieval order.
    sources = list(dict.fromkeys(
        doc.metadata.get("source", "") for doc in docs[:used_count]
    ))

    return result.content, [source for source in sources if source]
