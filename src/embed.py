from sentence_transformers import SentenceTransformer
import json
import torch

model = SentenceTransformer("intfloat/multilingual-e5-small")

#print(model.max_seq_length)
#print(model.get_sentence_embedding_dimension())
#print(model.device)

with open("data/chunks/undergraduate-academic-policies-chunks.json", encoding="utf-8") as json_file:
    undergraduate_academic_policies_chunks = json.load(json_file)

passages = []
for chunk in undergraduate_academic_policies_chunks:
    passage = "passage: " + chunk["text"]
    passages.append(passage)

embeddings = model.encode(passages, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=True)

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




results = []
for question in questions:
    query_embedding = model.encode(query, convert_to_tensor=True, normalize_embeddings=True,
                                        show_progress_bar=True)
    score = embeddings @ query_embedding
    top_scores, top_indices = torch.topk(score, k=5)
    expected_sections = []
    expected_pages = []
    for score, index in zip(top_scores.tolist(), top_indices.tolist()):
        chunk = undergraduate_academic_policies_chunks[index]
        expected_sections.append(chunk["text"])
        expected_pages.append(f"{chunk['page_start']}–{chunk['page_end']}")
    question["expected_sections"] = expected_sections
    question["expected_pages"] = expected_pages
    questions.append(question)

with open("data/eval/questions.json", "w", encoding="utf-8") as json_file:
    json.dump(questions , json_file, ensure_ascii=False, indent=2)