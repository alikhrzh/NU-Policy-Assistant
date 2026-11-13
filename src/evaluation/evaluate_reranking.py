import json
from pathlib import Path
from statistics import median
from time import perf_counter

from src.retrieval.reranker import Reranker
from src.retrieval.retriever import Retriever


QUESTION_SETS = {
    "EN": "questions_answerable_en.json",
    "RU": "questions_answerable_ru.json",
}

DEV_IDS = (
    "001",
    "002",
    "003",
    "004",
    "005",
    "real-010",
    "real-013",
    "real-022",
)


def first_relevant_rank(chunks, relevant_ids):
    for rank, chunk in enumerate(chunks, start=1):
        if chunk["chunk_id"] in relevant_ids:
            return rank
    return None


def format_hit_rate(ranks, k):
    hits = sum(rank is not None and rank <= k for rank in ranks)
    return f"{hits}/{len(ranks)} ({hits / len(ranks):.1%})"


def main():
    retriever = Retriever(model_name="bge-m3", top_k=20)
    reranker = Reranker(top_n=5)

    # Warm up both models before measuring latency.
    warmup_question = "Can I take more than 36 credits in one semester?"
    warmup_candidates = retriever.search(warmup_question)
    reranker.rerank(warmup_question, warmup_candidates)

    for language, filename in QUESTION_SETS.items():
        path = Path("data/eval") / filename
        with path.open(encoding="utf-8") as json_file:
            questions_by_id = {
                question["question_id"]: question
                for question in json.load(json_file)
            }

        test_ids = [question_id for question_id in questions_by_id if question_id not in DEV_IDS]

        before_ranks = []
        after_ranks = []
        retrieval_times = []
        reranking_times = []
        total_times = []

        print(f"\nBGE-M3 | {language} | TEST")
        print("First relevant rank: retrieval top 20 → reranked top 5")

        for question_id in test_ids:
            question = questions_by_id[question_id]
            query = question["question"]
            relevant_ids = set(question["relevant_chunk_ids"])

            start = perf_counter()
            candidates = retriever.search(query)
            retrieved_at = perf_counter()
            reranked = reranker.rerank(query, candidates)
            finished_at = perf_counter()

            retrieval_times.append(retrieved_at - start)
            reranking_times.append(finished_at - retrieved_at)
            total_times.append(finished_at - start)

            before = first_relevant_rank(candidates, relevant_ids)
            after = first_relevant_rank(reranked, relevant_ids)
            before_ranks.append(before)
            after_ranks.append(after)

            print(f"  {question_id}: {before or 'miss'} → {after or 'miss'}")

        print(f"\nQuestions: {len(before_ranks)}")
        for k in (1, 5):
            before = format_hit_rate(before_ranks, k)
            after = format_hit_rate(after_ranks, k)
            print(f"Hit@{k}: {before} → {after}")

        print(f"Candidate Hit@20: {format_hit_rate(before_ranks, 20)}")
        print(f"Median retrieval: {median(retrieval_times) * 1000:.1f} ms")
        print(f"Median reranking: {median(reranking_times) * 1000:.1f} ms")
        print(f"Median retrieval + reranking: {median(total_times) * 1000:.1f} ms")


if __name__ == "__main__":
    main()