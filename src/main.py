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

top_k = 20
reports = {}

for model_name in models:
    reports[model_name] = {}

    for language, filename in question_sets.items():
        evaluator = RetrievalEvaluator(
            questions_filename=filename,
            model_name=model_name,
            top_k=top_k,
        )

        report = evaluator.evaluate()
        reports[model_name][language] = report

        print(f"\n{model_name} | {language}")

        metrics = report["metrics"]
        print(f"Questions: {metrics['total_questions']}")

        for k in (1, 5, 20):
            hits = sum(
                result["first_relevant_rank"] is not None
                and result["first_relevant_rank"] <= k
                for result in report["results"]
            )
            print(
                f"Hit@{k}: {hits}/{metrics['total_questions']} "
                f"({hits / metrics['total_questions']:.1%})"
            )

    print("\nRanks by question")
    english_results = {
        result["question_id"]: result
        for result in reports[model_name]["EN"]["results"]
    }
    russian_results = {
        result["question_id"]: result
        for result in reports[model_name]["RU"]["results"]
    }

    for question_id, english_result in english_results.items():
        english_rank = english_result["first_relevant_rank"]
        russian_rank = russian_results[question_id]["first_relevant_rank"]
        print(f"{question_id}: EN={english_rank}, RU={russian_rank}")