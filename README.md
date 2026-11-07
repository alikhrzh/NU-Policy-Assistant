# NU Policy Assistant

NU Policy Assistant is a RAG prototype for Nazarbayev University policies. It searches 960 passages from 12 documents, tracks their source pages, and evaluates retrieval in English and Russian. Answer generation and a user interface are planned.

## Key findings

- On 18 test pairs, Qwen3 had the highest Hit@1 at 10/18 in each language.
- BGE-M3 found at least one labeled chunk in the top 20 for all 18 test questions in each language. The test set includes one question that overlaps with a dev question about course overload.
- Fixed-length chunks can split policy clauses or combine unrelated sections. In the diagnostic baseline, both BGE-M3 and Qwen3 found the Sports Complex rules but ranked other passages above the instruction for reporting broken equipment.

## Pipeline

```text
PDFs → extraction and cleaning → chunks → cached embeddings → ranked search → evaluation
```

- **Hit@k** is the share of questions with at least one labeled relevant chunk in the top k.
- **MRR** is the mean reciprocal rank of the first labeled relevant chunk. A missing match contributes zero.
- **Recall@k** is the share of labeled relevant chunks retrieved in the top k, averaged across questions.

## Quick start

Run from the repository root with Python 3.10 or newer and a compatible PyTorch installation.

```bash
python -m pip install torch sentence-transformers
mkdir -p data/embeddings/questions data/embeddings/chunks
python src/main.py
```

- Put prepared corpus files in `data/chunks/*-chunks.json` and the paired question sets in `data/eval/questions_answerable_en.json` and `data/eval/questions_answerable_ru.json`. The repository tracks these inputs for the baseline.
- The script compares three models and reports Hit@1, Hit@5, Hit@20, and the first relevant rank for the 18 test pairs. The eight development IDs are defined in `src/main.py`. It reuses matching embedding files in `data/embeddings/`. On a cache miss, the model may need to download weights from Hugging Face. Regenerate the affected question cache when you add or edit questions or change query formatting.
- To prepare the corpus from scratch, put source PDFs in `data/raw/` and record them in `data/sources.json`. PDF extraction uses `pypdf` and `pymupdf`. Scanned pages also need local Tesseract OCR. The preparation scripts write page-level JSON to `data/processed/`, then `src/chunk.py` builds the search inputs.

## Document Processing

- Processed 12 documents covering academic policies, student status, housing, mobility, conduct, and campus services.
- Recorded source URLs, document dates, access levels, verification status, and extraction notes.
- Extracted PDF text with pypdf and PyMuPDF and used local Tesseract OCR for the scanned Sports Complex rules.
- Generated 960 chunks from 231 pages using windows of up to 100 words with a 20-word overlap. Each chunk retains its document ID and source-page range.

## Semantic Retrieval

The prototype uses Sentence Transformers to encode queries and chunks with multilingual E5-small, BGE-M3, or Qwen3-Embedding-0.6B. It caches normalized embeddings and ranks chunks with PyTorch dot products. E5-small inference has been tested on Apple Metal (`mps`).

An initial token-length check on 110 undergraduate policy chunks found a maximum of 186 tokens within the model’s 512-token limit.

### Single-query retrieval

`Retriever` accepts a question in English or Russian and returns ranked chunks with their text, document IDs, page ranges, and similarity scores. It loads cached chunk embeddings once per instance and uses each chunk ID to look up the source text and metadata.

In a local BGE-M3 check, the relevant policy clause for a Russian question about taking more than 36 credits ranked first. Creating the retriever took 168 ms. The first search took 8.69 seconds, including model loading, and three subsequent searches on the same instance took 30–31 ms each. These measurements cover retrieval for one repeated question.

### Planned reranking experiment

BGE-M3 will retrieve 20 candidates. The multilingual `BAAI/bge-reranker-v2-m3` cross-encoder will score each question–chunk pair and keep the five highest-ranked chunks for answer generation.

The experiment will compare Hit@1, Hit@5, and warm retrieval latency before and after reranking on the eight English–Russian dev pairs. The 20-candidate pool sets the ceiling for the experiment. For the question about broken gym equipment (`real-013`), BGE-M3 ranked the relevant chunk 18th in Russian and 21st in English, so the reranker will see it only for the Russian query at this cutoff.
## Evaluation

The evaluation set contains **65 questions**, including **60 real student questions**. The current corpus supports a complete answer for 26, a partial answer for 22, and no confirmed answer for 17. The 26 answerable questions have paired English and Russian versions with shared IDs and relevance labels. The split uses eight pairs for development and 18 for testing.

The earlier mixed-language E5-small run scored 4/8 for both Hit@1 and Hit@5.

### Development set

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

### Test set

The test set contains 18 questions, each available in English and Russian. Both versions share the same question ID and relevance labels. The 8 development pairs are reported separately. All three models searched the same corpus of 960 chunks.

| Model | EN Hit@1 | EN Hit@5 | EN Hit@20 | RU Hit@1 | RU Hit@5 | RU Hit@20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| multilingual-e5-small | 7/18 | 14/18 | 16/18 | 4/18 | 12/18 | 14/18 |
| BGE-M3 | 9/18 | **18/18** | **18/18** | 8/18 | **14/18** | **18/18** |
| Qwen3-Embedding-0.6B | **10/18** | 17/18 | **18/18** | **10/18** | **14/18** | 16/18 |

Qwen3 achieved the highest Hit@1 in both languages. BGE-M3 retrieved at least one relevant chunk within the top 20 for every test question in both languages. The two Russian queries Qwen3 missed at that cutoff concerned academic leave. Their first relevant chunks ranked 143rd and 22nd with Qwen3, compared with 7th and 14th with BGE-M3.

Each question accounts for 5.6 percentage points per language. The test question about the course overload form (`real-060`) overlaps with a development question about exceeding 36 credits (`001`). Hit@k measures whether at least one labeled chunk appears in the top *k*. Questions that require evidence from multiple chunks may still have incomplete evidence even when counted as hits.

### Retrieval Diagnostic Baseline

BGE-M3 and Qwen3 searched the same 960 chunks using all 35 original questions. Retrieval metrics cover the 8 answerable and 13 partial questions separately. The 14 unanswerable questions are retained for later testing of how the assistant responds when evidence is missing.

| Group | Model | Hit@1 | Hit@5 | Hit@20 | MRR | Recall@20 | Recall@50 |
|---|---|---:|---:|---:|---:|---:|---:|
| Answerable | BGE-M3 | 3/8 | 7/8 | 8/8 | 0.590 | 95.0% | 100% |
| Answerable | Qwen3 | 5/8 | 6/8 | 7/8 | 0.710 | 82.5% | 85.0% |
| Partial | BGE-M3 | 5/13 | 8/13 | 10/13 | 0.501 | 71.8% | 83.3% |
| Partial | Qwen3 | 5/13 | 7/13 | 10/13 | 0.472 | 64.1% | 85.9% |

Recall is averaged across questions and measures coverage of labeled chunks. For partial questions, the labels support only part of the requested answer. Per-question results and language breakdowns are stored in [retrieval-diagnostics.json](data/model_evaluation_results/retrieval-diagnostics.json).

**Observed failure modes**

- **Wrong passage within the right document.** On answerable questions, BGE-M3 and Qwen3 ranked a chunk from the correct document first in 7/8 and 8/8 cases. The relevant chunk was first in 3/8 and 5/8 cases. For `real-013`, both found the Sports Complex rules but ranked the reporting instruction 18th and 64th.
- **Overlap between topics.** For `real-023`, both models ranked housing and mobility passages above campus access rules. For `real-008`, academic leave and missed assessments competed with attendance rules.
- **Colloquial mixed-language queries.** For `real-021`, BGE-M3 ranked the credit-load rule first, while Qwen3 ranked it 20th and returned dormitory passages first. Whether wording contributed to the miss remains a hypothesis.
- **Labels that need review.** The labeled passage for `real-026` describes attendance disclosures. It gives limited support for a question about where to find general syllabus rules.

Keep this run as the baseline. Test splitting Sports Complex clause 96 into its own chunk and normalizing the wording of `real-021` in separate experiments. Review the label for `real-026` before comparing updated metrics.

## Technologies

Python, PyTorch, Sentence Transformers, pypdf, PyMuPDF, and Tesseract OCR.

## Next Steps

1. Compare reranking against the retrieval baseline on the dev set. Track Hit@k and coverage of labeled chunks.
2. Generate answers with document and page citations. Check partial and unanswerable cases separately.
3. Add a small interface and a reproducible demo.

## Source Scope

Some source materials have restricted access and are used in the local evaluation. Several document versions still require verification. This is an independent learning project, and official university guidance should come from NU
