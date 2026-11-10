# NU Policy Assistant

NU Policy Assistant is a local search app for Nazarbayev University policies. Ask a question in English or Russian to find relevant passages across **960 chunks from 12 documents**. Each result shows the original text, document ID, and source pages.

The Streamlit app lets you compare semantic search with cross-encoder reranking. The project currently returns source passages. Answer generation with citations is planned.

## Results at a glance

- **BGE-M3 found a labeled passage in the top 20 for all 18 test questions in both languages.**
- Reranking improved test **Hit@1 from 50.0% to 77.8% in English** and **from 44.4% to 72.2% in Russian**.
- English Hit@5 fell from 100.0% to 88.9%. Russian Hit@5 stayed at 77.8%. Median retrieval and reranking latency after warm-up was about **1.2 seconds**.

## Quick start

Run from the repository root in a Python environment with a compatible PyTorch installation.

```bash
python -m pip install torch sentence-transformers
python -m pip install -r requirements.txt
```

The app uses prepared passages in `data/chunks/`, the embedding cache at `data/embeddings/chunks/bge-m3_chunks.json`, and local weights for `BAAI/bge-m3` and `BAAI/bge-reranker-v2-m3`. On a fresh setup, run the command-line check with network access to download the model weights:

```bash
python src/check_retriever.py
```

Then start the local app:

```bash
python -m streamlit run src/app.py
```

Enter a question and select **Search policies**. By default, the app retrieves 20 candidates and displays the five highest-ranked passages after reranking. Use **Advanced** to change either count or turn reranking off and inspect the original BGE-M3 order. Scores are relative ranking signals. For cached results, the timing line shows how long the original search took.

The app runs on localhost with Streamlit 1.56.0 and usage statistics disabled. Once the weights and embeddings are available locally, the app runs offline.

## How search works

```text
PDFs → extraction and cleaning → chunks with source pages
Question → BGE-M3 embedding → top 20 candidates → cross-encoder → top 5 passages
```

The corpus covers academic policies, student status, housing, mobility, conduct, and campus services. `data/sources.json` records source URLs, access levels, and extraction notes. Text was extracted using pypdf and PyMuPDF. The scanned Sports Complex rules were processed with Tesseract OCR. The pipeline generated 960 chunks from 231 pages using windows of up to 100 words with a 20-word overlap.

The retriever ranks normalized embeddings by dot product in PyTorch and joins results to source text and page metadata by `chunk_id`. The cross-encoder `BAAI/bge-reranker-v2-m3` scores each question–passage pair. The app keeps both scores and shows where each passage ranked before reranking.

To rebuild the corpus, put the PDFs in `data/raw/` and register them in `data/sources.json`. The extraction and cleaning scripts produce page-level JSON in `data/processed/`, and `src/chunk.py` builds the chunks. Rebuild the chunk embedding cache when the corpus changes.

## Evaluation

The dataset contains **65 questions**, including 60 collected from students. The corpus supports a complete answer for 26 questions and a partial answer for 22. The remaining 17 have no confirmed answer in the corpus. The 26 answerable questions have paired EN and RU versions with shared relevance labels. Eight pairs are used for development and 18 for testing.

### Embedding baseline

Each cell reports the number of hits at ranks 1, 5, and 20. The denominator is 8 on dev and 18 on test, per language.

| Model | EN dev @1 / @5 / @20 | RU dev @1 / @5 / @20 | EN test @1 / @5 / @20 | RU test @1 / @5 / @20 |
| --- | ---: | ---: | ---: | ---: |
| multilingual-e5-small | 4 / 5 / 6 | 1 / 2 / 4 | 7 / 14 / 16 | 4 / 12 / 14 |
| BGE-M3 | 3 / 7 / 7 | 4 / 7 / 8 | 9 / 18 / 18 | 8 / 14 / 18 |
| Qwen3-Embedding-0.6B | 5 / 7 / 7 | 5 / 5 / 7 | 10 / 17 / 18 | 10 / 14 / 16 |

Qwen3 led the embedding-only test comparison at Hit@1 with 10/18 in each language. BGE-M3 had the highest candidate coverage across both languages at the top-20 cutoff, so it was used for the reranking experiment.

### BGE-M3 with cross-encoder reranking

| Split | Language | Candidate Hit@20 | Hit@1 before → after | Hit@5 before → after | Median retrieval | Median reranking | Median total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dev | EN | 7/8 | 3/8 → 5/8 | 7/8 → 7/8 | 71.9 ms | 1,057.0 ms | 1,118.4 ms |
| Dev | RU | 8/8 | 4/8 → 6/8 | 7/8 → 8/8 | 40.6 ms | 1,023.9 ms | 1,064.6 ms |
| Test | EN | 18/18 | 9/18 → 14/18 | 18/18 → 16/18 | 51.1 ms | 1,138.2 ms | 1,180.0 ms |
| Test | RU | 18/18 | 8/18 → 13/18 | 14/18 → 14/18 | 56.1 ms | 1,133.2 ms | 1,199.1 ms |

Median total uses the combined retrieval and reranking time for each query after warm-up. In a separate single-query check, the first BGE-M3 search took 8.69 seconds including model loading. Repeated searches on the same retriever took 30–31 ms.

### What failed

- **Broken gym equipment (`real-013`).** Reranking moved the Russian reporting instruction from rank 18 to rank 1. The English counterpart started at rank 21 and fell outside the candidate pool.
- **Probation (`real-041`, EN).** The first labeled academic probation passage fell from rank 4 to rank 10. The top five included passages about disciplinary probation and sanctions. The query did not specify which kind of probation it meant.
- **Applying for academic leave (`real-051`, EN).** The first labeled passage fell from rank 3 to rank 11. All five leading passages came from the correct policy, but they covered topics such as returning from leave or withdrawing from the university. One passage included “Leave of Absence” in the repeated policy title. The effect of repeated titles on ranking has yet to be isolated.

The [retrieval diagnostics](data/model_evaluation_results/retrieval-diagnostics.json) cover the original 35-question set. They include per-question results for other cases of overlap, such as campus access versus dormitory guest rules.

### How to interpret the metrics

**Hit@k** measures whether at least one labeled passage appears in the top *k*. A hit can still have incomplete evidence if the question requires multiple passages. **Recall@k** measures the fraction of labeled passages retrieved, averaged across questions. **MRR** averages the reciprocal rank of the first labeled passage, with zero for a missing match.

One question changes Hit@k by 12.5 percentage points on dev and 5.6 points on test. The test question about the overload form (`real-060`) overlaps with the dev question about exceeding 36 credits (`001`).

### Reproduce the checks

```bash
python src/check_retriever.py
python src/main.py
```

`check_retriever.py` shows the passages, page ranges, scores, and rank changes for one question. `main.py` evaluates reranking on the 18 test pairs from the EN and RU sets in `data/eval/`.

## Optional PostgreSQL connection check

`src/db.py` opens a PostgreSQL connection and runs `SELECT 1`. The search app currently reads passages and embeddings from local files, so it can run without a database.

With PostgreSQL running and an existing database, install the driver and set `DATABASE_URL` in your environment:

```bash
python -m pip install "psycopg[binary]"
export DATABASE_URL='postgresql://USER:PASSWORD@localhost:5432/DB_NAME'
python src/db.py
```

Replace the placeholders with your local connection details. Keep credentials out of version control. If you store the URL in `.env`, load it into the environment before running the check.

## Next steps

1. Generate answers in English and Russian with citations to documents and pages.
2. Evaluate cases with complete, partial, and missing evidence. Check whether each citation supports the claim it accompanies.

## Source scope

Some source materials have restricted access and are used for local evaluation. The corpus reflects specific document versions, which may be outdated. This is an independent project. Consult Nazarbayev University for official policy guidance.