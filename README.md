# NU Policy Assistant

A retrieval-augmented generation (RAG) project for answering questions about Nazarbayev University undergraduate policies and campus life with references to source documents and pages.

**Status.** Document processing, semantic retrieval, and an initial evaluation are implemented. Answer generation and the interface are planned.

## Document Processing

- Processed 12 documents covering academic policies, student status, housing, mobility, conduct, and campus services.
- Recorded source URLs, document dates, access levels, verification status, and extraction notes.
- Extracted PDF text with pypdf and PyMuPDF and used local Tesseract OCR for the scanned Sports Complex rules.
- Generated 960 chunks from 231 pages using windows of up to 100 words with a 20-word overlap. Each chunk retains its document ID and source-page range.

## Semantic Retrieval

The prototype uses Sentence Transformers to encode queries and chunks with multilingual E5-small, BGE-M3, or Qwen3-Embedding-0.6B. It caches normalized embeddings and ranks chunks with PyTorch dot products. E5-small inference has been tested on Apple Metal (`mps`).

An initial token-length check on 110 undergraduate policy chunks found a maximum of 186 tokens within the model’s 512-token limit.

## Evaluation

The evaluation set contains **35 questions**, including **30 collected from student chats**. Based on the current local corpus, 8 have a complete answer, 13 have a partial answer, and 14 have no confirmed answer. The last two groups are retained for evaluating partial answers and responses when evidence is missing.

The earlier mixed-language E5-small run scored 4/8 for both Hit@1 and Hit@5.

### Preliminary English and Russian Comparison

Each model searched the same 960 chunks using eight paired questions. Both languages use the same relevance labels. Five questions originated in English and three came from Russian student chats.

| Model | EN Hit@1 | EN Hit@5 | EN Hit@20 | RU Hit@1 | RU Hit@5 | RU Hit@20 |
|---|---:|---:|---:|---:|---:|---:|
| multilingual-e5-small | 50% | 62.5% | 75% | 12.5% | 25% | 50% |
| BGE-M3 | 37.5% | 87.5% | 87.5% | 50% | 87.5% | 100% |
| Qwen3-Embedding-0.6B | 62.5% | 87.5% | 87.5% | 62.5% | 62.5% | 87.5% |

| Question | E5-small EN / RU | BGE-M3 EN / RU | Qwen3 EN / RU |
|---|---:|---:|---:|
| 001 — credit overload | 1 / 2 | 1 / 1 | 1 / 1 |
| 002 — course retake | 1 / 11 | 2 / 5 | 2 / 1 |
| 003 — withdrawal and GPA | 1 / 7 | 2 / 1 | 1 / 1 |
| 004 — missed classes | 6 / 161 | 1 / 1 | 1 / 9 |
| 005 — academic probation | 1 / 1 | 1 / 1 | 1 / 1 |
| real-010 — dormitory rates | 29 / 27 | 4 / 3 | 2 / 6 |
| real-013 — broken gym equipment | 34 / 21 | 21 / 18 | 34 / 64 |
| real-022 — incorrect grade | 3 / 136 | 3 / 3 | 1 / 1 |

Ranks identify the first labeled relevant chunk. BGE-M3 achieved 7/8 Hit@5 in both languages. Qwen had the highest Hit@1 at 5/8 in both languages. The broken-equipment question missed the top five in all six runs.

These results are preliminary. Each question accounts for 12.5 percentage points. The Qwen query instruction and embedding cache provenance still need verification.

The evaluator uses cached embeddings, returns the requested top-k results, and records the first relevant rank across the corpus. The comparison script reports Hit@1, Hit@5, and Hit@20 from those ranks.

## Technologies

Python, PyTorch, Sentence Transformers, pypdf, PyMuPDF, and Tesseract OCR.

## Next Steps

1. Verify cache provenance and model-specific query formatting, then rerun affected comparisons.
2. Expand and review evaluation labels, then compare quality and runtime across the three models.
3. Generate answers with source citations and build a simple Streamlit interface.
4. Document setup and evaluation steps for reproducible runs.

## Source Scope

Some source materials have restricted access and are used in the local evaluation. Several document versions still require verification. This is an independent learning project, and official university guidance should come from NU
