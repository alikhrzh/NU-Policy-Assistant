# NU Policy Assistant

A retrieval-augmented generation (RAG) project for answering questions about Nazarbayev University undergraduate policies and campus life with references to source documents and pages.

**Status.** Document processing, semantic retrieval, and an initial evaluation are implemented. Answer generation and the interface are planned.

## Document Processing

- Processed 12 documents covering academic policies, student status, housing, mobility, conduct, and campus services.
- Recorded source URLs, document dates, access levels, verification status, and extraction notes.
- Extracted PDF text with pypdf and PyMuPDF and used local Tesseract OCR for the scanned Sports Complex rules.
- Generated 960 chunks from 231 pages using windows of up to 100 words with a 20-word overlap. Each chunk retains its document ID and source-page range.

## Semantic Retrieval

The prototype uses `intfloat/multilingual-e5-small` through Sentence Transformers. It computes normalized 384-dimensional embeddings and ranks chunks with PyTorch dot products and `torch.topk`. Inference has been tested on Apple Metal (`mps`).

An initial token-length check on 110 undergraduate policy chunks found a maximum of 186 tokens within the model’s 512-token limit.

## Evaluation

The evaluation set contains **35 questions**, including **30 collected from student chats**. Based on the current local corpus, 8 have a complete answer, 13 have a partial answer, and 14 have no confirmed answer. The last two groups are retained for evaluating partial answers and responses when evidence is missing.

The earlier mixed-language E5-small run scored 4/8 for both Hit@1 and Hit@5.

### Intermediate English Comparison

All three models were evaluated against the same 960 chunks and eight answerable English questions. Five questions were generated in English and three were translated from real Russian student questions. The corresponding Russian question set is prepared for a separate run.

| Model | Hit@1 | Hit@5 |
|---|---:|---:|
| multilingual-e5-small | 4/8 (50%) | 5/8 (62.5%) |
| BGE-M3 | 3/8 (37.5%) | 7/8 (87.5%) |
| Qwen3-Embedding-0.6B | 5/8 (62.5%) | 7/8 (87.5%) |

| Question | E5-small rank | BGE-M3 rank | Qwen3 rank |
|---|---:|---:|---:|
| 001 — credit overload | 1 | 1 | 1 |
| 002 — course retake | 1 | 2 | 2 |
| 003 — withdrawal and GPA | 1 | 2 | 1 |
| 004 — missed classes | 6 | 1 | 1 |
| 005 — academic probation | 1 | 1 | 1 |
| real-010 — dormitory rates | 29 | 4 | 2 |
| real-013 — broken gym equipment | 34 | 21 | 34 |
| real-022 — incorrect grade | 3 | 3 | 1 |

Ranks identify the first manually labeled relevant chunk in the full ranking. These are exploratory results on eight questions. Query formatting and cache provenance, particularly the Qwen instruction, still need verification before treating the comparison as finalized.

The evaluator returns top-k results and calculates Hit@1, Hit@5, and Hit@k for the requested k from full relevance ranks. Changing k reuses cached embeddings.

## Technologies

Python, PyTorch, Sentence Transformers, pypdf, PyMuPDF, and Tesseract OCR.

## Next Steps

1. Verify cache provenance and model-specific query formatting, then run the paired Russian evaluation.
2. Expand and review evaluation labels, then compare quality and runtime across the three models.
3. Generate answers with source citations and build a simple Streamlit interface.
4. Document setup and evaluation steps for reproducible runs.

## Source Scope

Some source materials have restricted access and are used in the local evaluation. Several document versions still require verification. This is an independent learning project, and official university guidance should come from NU