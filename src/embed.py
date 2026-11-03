from sentence_transformers import SentenceTransformer
import json
import torch

model = SentenceTransformer("intfloat/multilingual-e5-small")

#print(model.max_seq_length)
#print(model.get_sentence_embedding_dimension())
#print(model.device)

with open("data/chunks/undergraduate-academic-policies-chunks.json", "r", encoding="utf-8") as json_file:
    undergraduate_academic_policies_chunks = json.load(json_file)

passages = []
for chunk in undergraduate_academic_policies_chunks:
    passage = "passage: " + chunk["text"]
    passages.append(passage)

embeddings = model.encode(passages, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=True)

with open("data/eval/questions.json", "r", encoding="utf-8") as json_file:
    questions = json.load(json_file)

