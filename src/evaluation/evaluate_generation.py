import argparse
import json
from dataclasses import replace
from pathlib import Path

from src.evaluation.evaluate_reranking import DEV_IDS, QUESTION_SETS
from src.generation.config import GenerationConfig
from src.generation.generate import generate_answer
from src.retrieval.reranker import Reranker
from src.retrieval.retriever import Retriever


def main():
    parser = argparse.ArgumentParser(description="Generate dev answers for manual review.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--language", choices=QUESTION_SETS, action="append")
    parser.add_argument("--question-id", choices=DEV_IDS, action="append")
    parser.add_argument("--neighbors", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    config = GenerationConfig.from_env()
    if args.neighbors is not None:
        config = replace(config, neighbors=args.neighbors)
    retriever = Retriever(model_name="bge-m3", top_k=20)
    reranker = Reranker(top_n=5)
    with args.output.open("x", encoding="utf-8") as output:
        for language in args.language or QUESTION_SETS:
            path = Path("data/eval") / QUESTION_SETS[language]
            questions = json.loads(path.read_text(encoding="utf-8"))
            for question in questions:
                question_id = question["question_id"]
                if question_id not in (args.question_id or DEV_IDS):
                    continue
                query = question["question"]
                candidates = retriever.search(query)
                chunks = reranker.rerank(query, candidates)
                result = generate_answer(query, chunks, config)
                record = {
                    "question_id": question_id,
                    "language": language,
                    "question": query,
                    "relevant_chunk_ids": question["relevant_chunk_ids"],
                    "candidate_chunk_ids": [chunk["chunk_id"] for chunk in candidates],
                    "reranked_chunk_ids": [chunk["chunk_id"] for chunk in chunks],
                    "retrieval_model": retriever.model_name,
                    "reranker_model": "BAAI/bge-reranker-v2-m3",
                    **result,
                }
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                output.flush()
                print(f"{language} {question_id}: {result['status']}", flush=True)


if __name__ == "__main__":
    main()
