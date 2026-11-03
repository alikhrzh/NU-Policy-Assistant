import json


query1_eng = "query: Can I take more than 36 credits in one semester"
query2_eng = "query: If I fail a course, can I retake it?"
query3_eng = "query: Will withdrawing from a course affect my GPA?"
query4_eng = "query: What happens if I miss too many classes?"
query5_eng = "query: How many semesters can I stay on academic probation??"

queries = [query1_eng, query2_eng, query3_eng, query4_eng, query5_eng]

expected_sources = {
    "001": {
        "expected_sections": ["3.3.7"],
        "expected_pages": [5],
    },
    "002": {
        "expected_sections": ["3.20.1"],
        "expected_pages": [15, 16],
    },
    "003": {
        "expected_sections": ["3.3.12"],
        "expected_pages": [5],
    },
    "004": {
        "expected_sections": ["3.4.2", "3.4.3", "3.4.4", "3.4.5"],
        "expected_pages": [6],
    },
    "005": {
        "expected_sections": ["3.16.4", "3.16.5"],
        "expected_pages": [14],
    },
}

questions = []
for query in queries:
    question = {}
    question["question_id"] = f"{len(questions) + 1:03d}"
    question["language"] = "en"
    question["question"] = query[7:]
    question["document_id"] = "undergraduate-academic-policies"
    source = expected_sources[question["question_id"]]
    question["expected_sections"] = source["expected_sections"]
    question["expected_pages"] = source["expected_pages"]
    questions.append(question)

with open("data/eval/questions.json", "w", encoding="utf-8") as json_file:
    json.dump(questions , json_file, ensure_ascii=False, indent=2)