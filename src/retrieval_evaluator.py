from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
import torch

class RetrievalEvaluator:
    model = SentenceTransformer("intfloat/multilingual-e5-small")

    #print(model.max_seq_length)
    #print(model.get_sentence_embedding_dimension())
    #print(model.device)
    all_chunks = []

    for path in sorted(Path("data/chunks").glob("*-chunks.json")):
        with path.open(encoding="utf-8") as json_file:
            all_chunks.extend(json.load(json_file))


    passages = []
    for chunk in all_chunks:
        passage = "passage: " + chunk["text"]
        passages.append(passage)

    embeddings = model.encode(passages, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=True)

    with open("data/eval/questions.json", "r", encoding="utf-8") as json_file:
        questions = json.load(json_file)

    results = []

    for question in questions:
        result = {}
        result["question_id"] = question["question_id"]
        result["model"] = "multilingual-e5-small"
        query = "query: " + question["question"]
        query_embedding = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
        similarity = embeddings @ query_embedding
        top_scores, top_indices = torch.topk(similarity, k=5)
        find_chunks = []
        scores = []
        for score, index in zip(top_scores.tolist(), top_indices.tolist()):
            chunk = all_chunks[index]
            find_chunks.append(chunk["chunk_id"])
            scores.append(score)
        result["chunk_ids"] = find_chunks
        result["scores"] = scores
        results.append(result)

    with open("data/model_evaluation_results/multilingual-e5-small-full-corpus-results.json", "w", encoding="utf-8") as json_file:
        json.dump(results , json_file, ensure_ascii=False, indent=2)