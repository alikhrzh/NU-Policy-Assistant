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

query1_eng = "query: How many credits student should take in one semester"
query1_rus = "query: Сколько кредитов нужно брать за семестр?"

query1_eng_embedding = model.encode(query1_eng, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=True)
query1_rus_embedding = model.encode(query1_rus, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=True)

scores_eng = embeddings @ query1_eng_embedding
scores_rus = embeddings @ query1_rus_embedding

print(scores_eng.shape)
print(scores_rus.shape)

print("for english query")
top_scores, top_indices = torch.topk(scores_eng, k=5)

for score, index in zip(top_scores.tolist(), top_indices.tolist()):
    chunk = undergraduate_academic_policies_chunks[index]
    print(f"\nScore: {score:.4f}")
    print(f"Pages: {chunk['page_start']}–{chunk['page_end']}")
    print(chunk["text"])

print("for russian query")
top_scores, top_indices = torch.topk(scores_rus, k=5)

for score, index in zip(top_scores.tolist(), top_indices.tolist()):
    chunk = undergraduate_academic_policies_chunks[index]
    print(f"\nScore: {score:.4f}")
    print(f"Pages: {chunk['page_start']}–{chunk['page_end']}")
    print(chunk["text"])