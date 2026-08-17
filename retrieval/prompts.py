"""Prompts for source-cited question answering."""

from langchain_core.prompts import PromptTemplate

_BASE = """Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES").
If you don't know the answer, just say that you don't know. Don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.

QUESTION: {question}
=========
{summaries}
=========
FINAL ANSWER:"""

ANSWER_PROMPT = PromptTemplate(
    template="You are a helpful assistant for RealEstate research.\n\n" + _BASE,
    input_variables=["summaries", "question"],
)

DOCUMENT_PROMPT = PromptTemplate(
    template="Content: {page_content}\nSource: {source}",
    input_variables=["page_content", "source"],
)
