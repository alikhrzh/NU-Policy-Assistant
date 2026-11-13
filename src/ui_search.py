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


MODEL_LABELS = {
    "bge-m3": "BGE-M3",
    "Qwen3-Embedding-0.6B": "Qwen3-Embedding-0.6B",
    "multilingual-e5-small": "Multilingual E5-small",
}


@st.cache_resource
def load_retriever(model_name):
    if model_name not in MODEL_LABELS:
        raise ValueError(f"Unknown embedding model: {model_name}.")
    if Path.cwd() != Path(__file__).resolve().parents[1]:
        raise ValueError("Run Streamlit from the repository root.")
    cache = Path("data/embeddings/chunks") / f"{model_name}_chunks.json"
    if not cache.is_file():
        raise FileNotFoundError(f"Restore the prepared embedding file at {cache}.")
    if not any(Path("data/chunks").glob("*-chunks.json")):
        raise FileNotFoundError("Restore the prepared passage files under data/chunks/.")

    return Retriever(model_name=model_name, top_k=20), Lock()


@st.cache_resource
def load_reranker():
    return Reranker(top_n=10), Lock()


@st.cache_data(max_entries=128, show_spinner=False)
def search(question, top_k, pool_size, use_reranker, model_name="bge-m3"):
    retriever, retrieval_lock = load_retriever(model_name)
    # Only the request's copy changes its candidate limit.
    request_retriever = copy(retriever)
    request_retriever.top_k = pool_size
    reranking_ms = 0
    with retrieval_lock:
        start = perf_counter()
        candidates = request_retriever.search(question)
        retrieval_ms = (perf_counter() - start) * 1000

    ranked = candidates
    if use_reranker:
        reranker, reranking_lock = load_reranker()
        with reranking_lock:
            start = perf_counter()
            ranked = reranker.rerank(question, candidates)
            reranking_ms = (perf_counter() - start) * 1000

    original_ranks = {
        chunk["chunk_id"]: rank
        for rank, chunk in enumerate(candidates, start=1)
    }
    timing = {
        "retrieval": retrieval_ms,
        "reranking": reranking_ms,
        "total": retrieval_ms + reranking_ms,
    }
    return [
        dict(chunk, original_rank=original_ranks[chunk["chunk_id"]], timing_ms=timing)
        for chunk in ranked[:top_k]
    ]
