from retrieval_evaluator import RetrievalEvaluator
print("results for multilingual-e5-small")
evaluator = RetrievalEvaluator(
    questions_filename="questions_answerable_en",
    model_name="multilingual-e5-small",
    top_k=20,
)

report = evaluator.evaluate()
metrics = report["metrics"]

print(f"Questions: {metrics['total_questions']}")
print(f"Hit@1: {metrics['hit_at_1']:.1%}")
print(f"Hit@{evaluator.top_k}: {metrics[f'hit_at_{evaluator.top_k}']:.1%}")

for result in report["results"]:
    print(
        result["question_id"],
        "first relevant rank:",
        result["first_relevant_rank"],
    )
print("results for bge-m3")
evaluator = RetrievalEvaluator(
    questions_filename="questions_answerable_en",
    model_name="bge-m3",
    top_k=20,
)

report = evaluator.evaluate()
metrics = report["metrics"]

print(f"Questions: {metrics['total_questions']}")
print(f"Hit@1: {metrics['hit_at_1']:.1%}")
print(f"Hit@{evaluator.top_k}: {metrics[f'hit_at_{evaluator.top_k}']:.1%}")

for result in report["results"]:
    print(
        result["question_id"],
        "first relevant rank:",
        result["first_relevant_rank"],
    )

print("results for Qwen3-Embedding-0.6B")
evaluator = RetrievalEvaluator(
    questions_filename="questions_answerable_en",
    model_name="Qwen3-Embedding-0.6B",
    top_k=20,
)

report = evaluator.evaluate()
metrics = report["metrics"]

print(f"Questions: {metrics['total_questions']}")
print(f"Hit@1: {metrics['hit_at_1']:.1%}")
print(f"Hit@{evaluator.top_k}: {metrics[f'hit_at_{evaluator.top_k}']:.1%}")

for result in report["results"]:
    print(
        result["question_id"],
        "first relevant rank:",
        result["first_relevant_rank"],
    )

