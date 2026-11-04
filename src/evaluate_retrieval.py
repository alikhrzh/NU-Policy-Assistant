import json

with open("data/model_evaluation_results/multilingual-e5-small-full-corpus-results.json", "r", encoding="utf-8") as json_file:
    multilingual_e5_small_full_corpus_results = json.load(json_file)

with open("data/eval/questions.json", "r", encoding="utf-8") as json_file:
    questions = json.load(json_file)

results_by_id = {
    result["question_id"]: result
    for result in multilingual_e5_small_full_corpus_results
}

hit_at_1 = 0
hit_at_5 = 0

for question in questions:
    question_id = question["question_id"]
    chunk_ids = results_by_id[question_id]["chunk_ids"]
    relevant_ids = set(question["relevant_chunk_ids"])

    if chunk_ids and chunk_ids[0] in relevant_ids:
        hit_at_1 += 1

    if any(chunk_id in relevant_ids for chunk_id in chunk_ids[:5]):
        hit_at_5 += 1

total = len(questions)
print("results")
print(f"Hit@1: {hit_at_1}/{total} ({hit_at_1 / total:.0%})")
print(f"Hit@5: {hit_at_5}/{total} ({hit_at_5 / total:.0%})")