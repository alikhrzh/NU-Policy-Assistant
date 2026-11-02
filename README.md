# NU Policy Assistant

A retrieval-augmented generation (RAG) project for answering questions about Nazarbayev University undergraduate policies and campus life, with references to source documents and pages.

**Status: in development.** Document extraction, initial cleaning, and chunking are implemented. Embedding-based retrieval, answer generation, and the interface are planned.

## Current Progress

- Collected 12 documents covering academic policies, student status, housing, mobility, conduct, and campus services.
- Created a metadata registry with document dates, access levels, verification status, and extraction notes.
- Extracted text using pypdf and PyMuPDF.
- Applied local Tesseract OCR to the scanned Sports Complex rules.
- Added configurable removal of page numbers and recurring headers and footers.
- Preserved original text alongside cleaned text.
- Generated 960 chunks from 231 pages using 100-word windows with a 20-word overlap.
- Verified chunk coverage, unique identifiers, and source-page ranges.

## Pipeline

```text
PDF documents
    ↓
Text extraction / OCR
    ↓
Page-level JSON
    ↓
Text cleaning
    ↓
Chunks with source-page ranges
    ↓
Embeddings and retrieval — planned
    ↓
Answer generation with citations — planned
```

Chunking runs across pages within each document. Every chunk retains its document identifier and starting and ending PDF pages.

## Project Structure

```text
data/
├── raw/                 # Local source PDFs
├── processed/           # Extracted and cleaned page-level JSON
├── chunks/              # Generated chunk files
├── sources.csv          # Document metadata
├── sources.json         # Document metadata in JSON
└── cleaning_rules.json  # Document-specific cleaning settings

src/
├── extract.py
├── extract_guidebook.py
├── extract_sports_complex_rules.py
└── clean.py
```

## Technologies

- Python
- pypdf
- PyMuPDF
- Tesseract OCR

## Current Limitations

- Some document versions still require confirmation of their current status.
- OCR output contains recognition errors, particularly in stamps, handwritten dates, and the table of contents.
- Some recurring headers and layout artifacts remain.
- Fixed-size chunks may split sentences, lists, and tables.
- Retrieval and answer quality have not yet been evaluated.

## Next Steps

- Select an embedding model and check chunk token lengths.
- Implement semantic retrieval and inspect top results.
- Build an evaluation set of questions and supporting sources.
- Add LLM-generated answers with document and page citations.
- Build a Streamlit interface.
- Document setup and dependencies.

## Source Documents

Source PDFs and generated text are maintained locally. Some materials have restricted access; inclusion in the local corpus does not establish permission to redistribute them.

This is an independent learning project, not an official NU service. It is not yet ready to provide authoritative guidance on current university policies.