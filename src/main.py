import json

with open("data/model_evaluation_results/multilingual-e5-small-full-corpus-results.json", "r", encoding="utf-8") as json_file:
    multilingual_e5_small_full_corpus_results = json.load(json_file)

with open("data/eval/questions.json", "r", encoding="utf-8") as json_file:
    questions = json.load(json_file)

results_by_id = {
    result["question_id"]: result
    for result in multilingual_e5_small_full_corpus_results
}

answerable_questions = [
    question for question in questions
    if question["group"] == "answerable" and question["relevant_chunk_ids"]
]

total = len(answerable_questions)
if total == 0:
    raise SystemExit("Нет отвечаемых вопросов с размеченными фрагментами.")

hit_at_1 = 0
hit_at_5 = 0

for question in answerable_questions:
    question_id = question["question_id"]

    if question_id not in results_by_id:
        raise SystemExit(
            f"Нет выдачи для {question_id}. Перезапусти поиск на новом наборе."
        )

    chunk_ids = results_by_id[question_id]["chunk_ids"]
    relevant_ids = set(question["relevant_chunk_ids"])

    found_at_1 = bool(relevant_ids.intersection(chunk_ids[:1]))
    found_at_5 = bool(relevant_ids.intersection(chunk_ids[:5]))

    hit_at_1 += int(found_at_1)
    hit_at_5 += int(found_at_5)

    if not found_at_1:
        print(f"{question_id}: промах в топ-1 — {question['question']}")
    if not found_at_5:
        print(f"{question_id}: промах и в топ-5")

print(f"Hit@1: {hit_at_1}/{total} ({hit_at_1 / total:.1%})")
print(f"Hit@5: {hit_at_5}/{total} ({hit_at_5 / total:.1%})")