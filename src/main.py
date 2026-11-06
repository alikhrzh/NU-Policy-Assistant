from retrieval_evaluator import RetrievalEvaluator


models = [
    "multilingual-e5-small",
    "bge-m3",
    "Qwen3-Embedding-0.6B",
]

question_sets = {
    "EN": "questions_answerable_en",
    "RU": "questions_answerable_ru",
}

dev_ids = (
    "001",
    "002",
    "003",
    "004",
    "005",
    "real-010",
    "real-013",
    "real-022",
)

top_k = 20

for model_name in models:
    test_results_by_language = {}

    for language, filename in question_sets.items():
        evaluator = RetrievalEvaluator(
            questions_filename=filename,
            model_name=model_name,
            top_k=top_k,
        )
        report = evaluator.evaluate()

        results_by_id = {
            result["question_id"]: result
            for result in report["results"]
        }

        missing_ids = set(dev_ids) - results_by_id.keys()
        if missing_ids:
            raise ValueError(f"{language}: missing dev IDs {sorted(missing_ids)}")

        test_results = [
            result
            for question_id, result in results_by_id.items()
            if question_id not in dev_ids
        ]
        test_results_by_language[language] = test_results

        total = len(test_results)
        if total == 0:
            raise ValueError(f"{language}: test set is empty")

        print(f"\n{model_name} | {language} | TEST")
        print(f"Questions: {total}")

        for k in (1, 5, 20):
            hits = sum(
                result["first_relevant_rank"] is not None
                and result["first_relevant_rank"] <= k
                for result in test_results
            )
            print(f"Hit@{k}: {hits}/{total} ({hits / total:.1%})")

    print("\nTEST ranks by question")
    ru_ranks = {
        result["question_id"]: result["first_relevant_rank"]
        for result in test_results_by_language["RU"]
    }

    for result in test_results_by_language["EN"]:
        question_id = result["question_id"]
        print(
            f"{question_id}: EN={result['first_relevant_rank']}, "
            f"RU={ru_ranks[question_id]}"
        )