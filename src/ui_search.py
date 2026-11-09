import os
from copy import copy
from pathlib import Path
from threading import Lock
from time import perf_counter

import streamlit as st

# The web interface uses locally prepared weights and embeddings.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

from reranker import Reranker
from retriever import Retriever


@st.cache_resource
def load_pipeline():
    if Path.cwd() != Path(__file__).resolve().parents[1]:
        raise ValueError("Run Streamlit from the repository root.")
    cache = Path("data/embeddings/chunks/bge-m3_chunks.json")
    if not cache.is_file():
        raise FileNotFoundError(f"Restore the prepared embedding file at {cache}.")
    if not any(Path("data/chunks").glob("*-chunks.json")):
        raise FileNotFoundError("Restore the prepared passage files under data/chunks/.")

    retriever = Retriever(model_name="bge-m3", top_k=20)
    reranker = Reranker(top_n=10)
    question = "Can I take more than 36 credits in one semester?"
    reranker.rerank(question, retriever.search(question))
    return retriever, reranker, Lock()


@st.cache_data(max_entries=128, show_spinner=False)
def search(question, top_k, pool_size, use_reranker):
    retriever, reranker, lock = load_pipeline()
    # Only the request's copy changes its candidate limit.
    request_retriever = copy(retriever)
    request_retriever.top_k = pool_size
    with lock:
        start = perf_counter()
        candidates = request_retriever.search(question)
        retrieved = perf_counter()
        ranked = reranker.rerank(question, candidates) if use_reranker else candidates
        finished = perf_counter()

    original_ranks = {
        chunk["chunk_id"]: rank
        for rank, chunk in enumerate(candidates, start=1)
    }
    timing = {
        "retrieval": (retrieved - start) * 1000,
        "reranking": (finished - retrieved) * 1000 if use_reranker else 0,
        "total": (finished - start) * 1000,
    }
    return [
        dict(chunk, original_rank=original_ranks[chunk["chunk_id"]], timing_ms=timing)
        for chunk in ranked[:top_k]
    ]
