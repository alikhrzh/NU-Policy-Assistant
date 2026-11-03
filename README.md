# NU Policy Assistant

A retrieval-augmented generation (RAG) project for answering questions about Nazarbayev University undergraduate policies and campus life, with references to source documents and pages.

**Status: in development.** Document processing and an initial semantic search prototype are implemented. Answer generation and the user interface are planned.

## Implemented

### Document Processing

- Collected 12 documents covering academic policies, student status, housing, mobility, conduct, and campus services.
- Created a metadata registry with document dates, access levels, verification status, and extraction notes.
- Extracted text using pypdf and PyMuPDF.
- Applied local Tesseract OCR to scanned Sports Complex rules.
- Added document-specific cleaning rules for page numbers, headers, and footers.
- Preserved original text alongside cleaned text.
- Generated 960 chunks from 231 pages using 100-word windows with a 20-word overlap.
- Verified chunk coverage, unique identifiers, and source-page ranges.

### Semantic Search Prototype

- Loaded `intfloat/multilingual-e5-small` through Sentence Transformers.
- Checked token lengths for 110 undergraduate policy chunks: the maximum was 186 tokens, within the model’s 512-token limit.
- Generated normalized 384-dimensional embeddings.
- Implemented similarity search using PyTorch matrix multiplication and `torch.topk`.
- Tested English and Russian questions against English source text.
- Ran inference using the Apple Metal (`mps`) backend.

## Preliminary Observations

An initial bilingual question retrieved the relevant minimum-credit-load rule at rank 1 in both languages.

In a separate exploratory check of five English questions, manual inspection found a directly relevant source at rank 1 for four questions. For the attendance question, a relevant source appeared at rank 3.

These are preliminary observations on one document, not a formal benchmark. A fixed evaluation set is being prepared.

## Pipeline

```text
PDF documents
    ↓
Text extraction / OCR
    ↓
Page-level JSON
    ↓
Document-specific cleaning
    ↓
Chunks with source-page ranges
    ↓
Multilingual embeddings
    ↓
Top-k semantic retrieval
    ↓
Answer generation with citations — planned
```

Chunks can span multiple pages within a document. Each chunk retains its document identifier and starting and ending PDF pages.

## Data Layout

```text
data/
├── raw/                 # Local source PDFs
├── processed/           # Original and cleaned page-level text
├── chunks/              # Generated chunk files
├── eval/                # Evaluation questions and results
├── sources.csv          # Document metadata
├── sources.json         # Document metadata in JSON
└── cleaning_rules.json  # Document-specific cleaning settings
```

Source PDFs and derived text are maintained locally and excluded from version control.

## Technologies

- Python
- PyTorch
- Sentence Transformers
- pypdf
- PyMuPDF
- Tesseract OCR

## Current Limitations

- Semantic search has been tested on undergraduate academic policies, not yet the full corpus.
- Some document versions still require confirmation of their current status.
- Some headers, extraction artifacts, and OCR errors remain.
- Fixed-size chunks can split rules, exceptions, lists, and tables.
- Similarity scores are not probabilities of correctness.
- Retrieval quality has not yet been measured on a finalized evaluation set.
- No LLM answer generation or user interface is implemented yet.

## Next Steps

- Finalize questions and independently verified supporting sources.
- Save embeddings with their corresponding chunk identifiers.
- Extend retrieval to the eligible document corpus.
- Evaluate English and Russian retrieval separately.
- Compare multilingual E5-small with an English MiniLM baseline and multilingual E5-base.
- Add LLM-generated answers with source citations.
- Build a Streamlit interface.
- Document installation, dependencies, and reproducible evaluation.

## Source Documents

Some source materials have restricted access. Inclusion in the local corpus does not establish permission to redistribute them or use them with external services.

This is an independent learning project, not an official NU service. It is not yet ready to provide authoritative guidance on current university policies.