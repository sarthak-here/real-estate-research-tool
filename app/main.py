"""Streamlit UI for the real estate research tool."""

import sys
from pathlib import Path

# Streamlit puts this file's directory on sys.path, not the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from ingestion import process_urls  # noqa: E402
from retrieval import generate_answer  # noqa: E402

st.title("Real Estate Research Tool")

url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")
url3 = st.sidebar.text_input("URL 3")

placeholder = st.empty()

if st.sidebar.button("Process URLs"):
    urls = [url for url in (url1, url2, url3) if url != ""]
    if len(urls) == 0:
        placeholder.text("You must provide at least one valid url")
    else:
        for status in process_urls(urls):
            placeholder.text(status)

query = placeholder.text_input("Question")
if query:
    try:
        answer, sources = generate_answer(query)
        st.header("Answer:")
        st.write(answer)

        if sources:
            st.subheader("Sources:")
            for source in sources:
                st.write(source)
    except RuntimeError:
        placeholder.text("You must process urls first")
