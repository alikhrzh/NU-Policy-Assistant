import json
from pathlib import Path

from retrieval_evaluator import RetrievalEvaluator


MODELS = ("bge-m3", "Qwen3-Embedding-0.6B")
QUESTIONS_PATH = Path("data/eval/questions.json")
REPORT_PATH = Path("data/model_evaluation_results/retrieval-diagnostics.json")
TOP_K = 50


def summarize(rows):
    total = len(rows)
    if total == 0:
        return {"questions": 0}

    metrics = {"questions": total}

    for k in (1, 5, 20):
        hits = sum(
            row["first_relevant_rank"] is not None
            and row["first_relevant_rank"] <= k
            for row in rows
        )
        metrics[f"hit_at_{k}"] = {"hits": hits, "rate": hits / total}

    metrics["mrr"] = sum(
        1 / row["first_relevant_rank"]
        if row["first_relevant_rank"] is not None
        else 0.0
        for row in rows
    ) / total

    for k in (20, 50):
        metrics[f"recall_at_{k}"] = sum(
            sum(rank <= k for rank in row["relevant_ranks_in_top_50"].values())
            / len(row["relevant_chunk_ids"])
            for row in rows
        ) / total

    return metrics


def main():
    with QUESTIONS_PATH.open(encoding="utf-8") as file:
        questions = json.load(file)

    diagnostics = {}

    for model_name in MODELS:
        evaluator = RetrievalEvaluator(
            questions_filename=QUESTIONS_PATH.stem,
            model_name=model_name,
            top_k=TOP_K,
        )
        report = evaluator.evaluate()
        results_by_id = {
            result["question_id"]: result for result in report["results"]
        }

        rows = []
        for question in questions:
            question_id = question["question_id"]
            result = results_by_id[question_id]
            relevant_ids = set(question["relevant_chunk_ids"])

            rows.append({
                "question_id": question_id,
                "question": question["question"],
                "group": question["group"],
                "language": question["language"],
                "relevant_chunk_ids": question["relevant_chunk_ids"],
                "first_relevant_rank": result["first_relevant_rank"],
                "relevant_ranks_in_top_50": {
                    chunk_id: rank
                    for rank, chunk_id in enumerate(result["chunk_ids"], start=1)
                    if chunk_id in relevant_ids
                },
                "top_chunk_ids": result["chunk_ids"],
                "top_scores": result["scores"],
            })

        metrics = {}
        print(f"\n{model_name} | {len(rows)} questions")

        for group in ("answerable", "partial"):
            for language in ("all", "en", "ru"):
                subset = [
                    row for row in rows
                    if row["group"] == group
                    and row["relevant_chunk_ids"]
                    and (language == "all" or row["language"] == language)
                ]

                summary = summarize(subset)
                metrics[f"{group}/{language}"] = summary

                total = summary["questions"]
                if total == 0:
                    print(f"{group}/{language} | no labeled questions")
                    continue

                hits = " | ".join(
                    f"Hit@{k} {summary[f'hit_at_{k}']['hits']}/{total}"
                    for k in (1, 5, 20)
                )
                print(
                    f"{group}/{language} | {hits}"
                    f" | MRR {summary['mrr']:.3f}"
                    f" | Recall@20 {summary['recall_at_20']:.1%}"
                    f" | Recall@50 {summary['recall_at_50']:.1%}"
                )

        diagnostics[model_name] = {"metrics": metrics, "results": rows}

    print("\nQuestions missed at top 5 by both models")
    bge_results = diagnostics[MODELS[0]]["results"]
    qwen_by_id = {
        row["question_id"]: row for row in diagnostics[MODELS[1]]["results"]
    }

    for row in bge_results:
        if row["group"] not in ("answerable", "partial") or not row["relevant_chunk_ids"]:
            continue

        bge_rank = row["first_relevant_rank"]
        qwen_rank = qwen_by_id[row["question_id"]]["first_relevant_rank"]

        if (bge_rank is None or bge_rank > 5) and (qwen_rank is None or qwen_rank > 5):
            print(
                f"{row['question_id']} [{row['group']}/{row['language']}] "
                f"BGE={bge_rank}, Qwen={qwen_rank} | {row['question']}"
            )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(diagnostics, file, ensure_ascii=False, indent=2)

    print(f"\nSaved {REPORT_PATH}")


if __name__ == "__main__":
    main()