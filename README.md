# NU Policy Assistant

NU Policy Assistant is a retrieval prototype for Nazarbayev University policies. It searches **960 chunks from 12 documents** using English or Russian questions and returns passages with document IDs and source pages. The local Streamlit app displays ranked passages and lets users compare semantic retrieval with cross-encoder reranking. Answer generation with citations is the next step.

## Key findings

- BGE-M3 retrieved at least one labeled relevant chunk in the top 20 for all 18 test questions in both languages.
- Reranking increased test Hit@1 from **50.0% to 77.8% in English** and from **44.4% to 72.2% in Russian**.
- English test Hit@5 dropped from **100.0% to 88.9%**. Russian test Hit@5 stayed at **77.8%**. Median latency for warmed-up retrieval and reranking was about **1.2 seconds**.
- Manual review of two English misses found that the reranker promoted passages about a different kind of probation or a different stage of academic leave.

## Pipeline

```text
PDFs → text extraction and cleaning → chunks with page metadata
     → cached chunk embeddings → BGE-M3 top 20
     → cross-encoder reranking → top 5 passages
```

## Quick start

Run from the repository root in a Python environment with PyTorch and Sentence Transformers installed.

```bash
python -m pip install -r requirements.txt
streamlit run src/app.py
```

The app binds to localhost and uses Streamlit 1.56.0 with usage statistics disabled. It requires prepared passages in `data/chunks/`, the BGE-M3 embedding cache at `data/embeddings/chunks/bge-m3_chunks.json`, and locally cached weights for `BAAI/bge-m3` and `BAAI/bge-reranker-v2-m3`. On a fresh setup, run `python src/check_retriever.py` with network access to prepare the model caches before starting the offline app.

Enter an English or Russian question and select **Search policies**. The default search retrieves 20 candidates, reranks them, and shows five passages. **Advanced** lets you change both counts or turn reranking off to see the original BGE-M3 order. Each result shows its document, page range, passage text, and relative ranking scores. The timing line reports the original search duration for cached results.

### Command-line checks

- `python src/check_retriever.py` checks one question and shows source pages, scores, and rank changes.
- `python src/main.py` compares retrieval before and after reranking on 18 test pairs. It reads the English and Russian sets in `data/eval/` and reports Hit@1, Hit@5, candidate Hit@20, and median latency after warm-up.

Rebuild the affected chunk embedding cache after changing the corpus. For evaluation scripts that use cached question embeddings, rebuild the affected question cache after changing questions or query formatting.

## Document processing

The corpus covers academic policies, student status, housing, mobility, conduct, and campus services. `data/sources.json` tracks document metadata, source URLs, access levels, and extraction notes.

PDF text was extracted with pypdf and PyMuPDF. Scanned Sports Complex rules were processed with local Tesseract OCR. The processing pipeline generated 960 chunks from 231 pages using windows of up to 100 words with a 20-word overlap. Each chunk retains its document ID and page range.

To prepare the corpus from PDFs, put the source files in `data/raw/` and record them in `data/sources.json`. The extraction and cleaning scripts produce page-level JSON in `data/processed/`. `src/chunk.py` builds the search inputs.

## Retrieval and reranking

The embedding baseline compares multilingual E5-small, BGE-M3, and Qwen3-Embedding-0.6B. The retriever ranks normalized query and chunk embeddings by dot product using PyTorch. It loads the chunk embeddings once per instance and joins ranked results to their source text and page metadata by `chunk_id`.

The current reranking pipeline uses **BGE-M3** to retrieve 20 candidates. A separate multilingual cross-encoder, `BAAI/bge-reranker-v2-m3`, scores each question–passage pair and keeps the five highest-ranked passages. Each result retains its original retrieval score and its reranker score.

In a local BGE-M3 smoke test, the relevant clause for a Russian question about taking more than 36 credits ranked first. Creating the retriever took 168 ms. The first search took 8.69 seconds, including model loading. Three repeated searches on the same instance took 30–31 ms each. These timings cover retrieval for one repeated question.

## Evaluation

The evaluation dataset contains **65 questions**, including 60 collected from students. The current corpus supports a complete answer for 26 questions and a partial answer for 22. The remaining 17 have no confirmed answer in the corpus.

The 26 answerable questions have paired English and Russian versions with shared IDs and relevance labels. Eight pairs form the development set and 18 form the test set. All runs search the same corpus.

- **Hit@k** is the share of questions with at least one labeled relevant chunk in the top *k*.
- **MRR** is the mean reciprocal rank of the first labeled relevant chunk. A missing match contributes zero.
- **Recall@k** is the share of labeled relevant chunks retrieved in the top *k*, averaged across questions.

### Embedding baseline

| Model | EN dev Hit@1 / @5 / @20 | RU dev Hit@1 / @5 / @20 | EN test Hit@1 / @5 / @20 | RU test Hit@1 / @5 / @20 |
| --- | ---: | ---: | ---: | ---: |
| multilingual-e5-small | 4 / 5 / 6 | 1 / 2 / 4 | 7 / 14 / 16 | 4 / 12 / 14 |
| BGE-M3 | 3 / 7 / 7 | 4 / 7 / 8 | 9 / 18 / 18 | 8 / 14 / 18 |
| Qwen3-Embedding-0.6B | 5 / 7 / 7 | 5 / 5 / 7 | 10 / 17 / 18 | 10 / 14 / 16 |

Each cell shows the number of hits at the three cutoffs. The denominator is 8 per language on dev and 18 per language on test. Qwen3 led the embedding-only test comparison at Hit@1 with 10/18 in both languages. BGE-M3 had the strongest candidate coverage across both languages at the top-20 cutoff and was used for the reranking experiment.

### Reranking results

| Split | Language | Candidate Hit@20 | Hit@1 before → after | Hit@5 before → after | Median retrieval | Median reranking | Median total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dev | EN | 7/8 | 3/8 → 5/8 | 7/8 → 7/8 | 71.9 ms | 1,057.0 ms | 1,118.4 ms |
| Dev | RU | 8/8 | 4/8 → 6/8 | 7/8 → 8/8 | 40.6 ms | 1,023.9 ms | 1,064.6 ms |
| Test | EN | 18/18 | 9/18 → 14/18 | 18/18 → 16/18 | 51.1 ms | 1,138.2 ms | 1,180.0 ms |
| Test | RU | 18/18 | 8/18 → 13/18 | 14/18 → 14/18 | 56.1 ms | 1,133.2 ms | 1,199.1 ms |

Median total is calculated from the combined time for each question. Timing excludes model startup and answer generation.

On dev, reranking moved the relevant passage for the Russian gym equipment question (`real-013`) from rank 18 to rank 1. The English version's relevant passage ranked 21st in the embedding baseline and fell outside the candidate pool.

### Error analysis

- **Academic and disciplinary probation (`real-041`, EN).** The first relevant rank went from 4 to 10. The reranker put an academic status notification passage first. The rest of the top five discussed disciplinary probation or sanctions. The question says “probation” without naming which kind. The relevance labels assume academic probation based on grades.
- **Applying for academic leave (`real-051`, EN).** The first relevant rank went from 3 to 11. All five leading passages came from the correct policy. They covered a definition, a return-date form, withdrawal and dismissal material, the return-from-leave procedure, and the document scope. The application instructions fell outside the top five.
- **Repeated policy titles.** One high-ranked passage for `real-051` mentions leave of absence in the repeated document title while its surrounding text covers withdrawal and dismissal. Whether repeated titles affect ranking more broadly remains an open question. These two cases did not establish a preference for terms near the start of a chunk.

The earlier [retrieval diagnostics](data/model_evaluation_results/retrieval-diagnostics.json) cover the original 35-question dataset. That run identified other sources of confusion, including campus access versus dormitory guest rules, and excused class absences versus academic leave. Fixed-length chunks can also split policy clauses or combine text from different sections.

### Evaluation limits

A single question changes a hit rate by 12.5 percentage points on dev and 5.6 points on test. The test question about the course overload form (`real-060`) overlaps with the dev question about exceeding 36 credits (`001`).

Hit@k records the presence of at least one labeled passage. Questions that require multiple passages can count as hits with incomplete evidence.

Answer quality and citation accuracy still need separate evaluation.

## Next steps

1. Generate answers in English and Russian with document and page citations.
2. Evaluate complete, partial, and unsupported answers and verify that the cited passages support each claim.

## Source scope

Some source materials have restricted access and are used in local evaluation. Several document versions still require verification. This is an independent project. Consult Nazarbayev University for official policy guidance.
