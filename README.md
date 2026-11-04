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

The expanded E5-small run searched all 960 chunks and scored the eight questions with a complete answer.

| Metric | Result |
|---|---:|
| Hit@1 | 4/8 (50%) |
| Hit@5 | 4/8 (50%) |

For the question about reporting broken gym equipment, the model retrieved gym safety rules but missed the clause directing visitors to the Sports Complex administration.

Two additional JSON files contain the same eight questions in English and Russian, with matching question IDs and relevant chunk IDs. These paired sets are ready for a language comparison. The table above reports the earlier mixed-language run.

## Technologies

Python, PyTorch, Sentence Transformers, pypdf, PyMuPDF, and Tesseract OCR.

## Next Steps

1. Cache corpus embeddings and run the paired English and Russian evaluations with E5-small.
2. Compare E5-small, BGE-M3, and Qwen3-Embedding-0.6B on the same corpus and question pairs using Hit@1, Hit@5, and the rank of the first relevant chunk.
3. Generate answers with source citations and build a simple Streamlit interface.
4. Document setup and evaluation steps for reproducible runs.

## Source Scope

Some source materials have restricted access and are used in the local evaluation. Several document versions still require verification. This is an independent learning project, and official university guidance should come from NU