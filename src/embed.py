from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
import torch

class EmbeddingStore:
    def __init__(self, model_name="multilingual-e5-small", questions_filename="questions"):
        self.model = model_name
        self.questions_filename = questions_filename

    def get_or_create_question_embeddings(self, ):
        path_embedding_question = Path("data/embeddings/questions") / f"{model_name}_{questions_filename}_question.json"
        if path_embedding_question.cache_path.is_file():
            return path_embedding_question
        else:
            match model_name:
                case "multilingual-e5-small":
                    return multilingual_e_5_small_question()
                case "multilingual-e5-small":
                    return multilingual_e_5_small_question()
                case "multilingual-e5-small":
                    return multilingual_e_5_small_question()
                case _:
                    raise SystemExit(f"Нет такой модели. Перезапусти поиск на новом наборе." )


    def get_or_create_chunk_embeddings(self, ):
        path_embedding_chunks = Path("data/embeddings/chunks") / f"{model_name}_{questions_filename}_chunks.json"
        if path_embedding_chunks.cache_path.is_file():
            return path_embedding_chunks
        else:
            match model_name:
                case "multilingual-e5-small":
                    return multilingual_small_chunks()
                case "bge-m3":
                    return bge_small_chunks()
                case "Qwen3-Embedding-0.6B":
                    return qwene_small_chunks()
                case _:
                    raise SystemExit(f"Нет такой модели. Перезапусти поиск на новом наборе.")
    def multilingual_small_question(self,):
    def bge_small_question(self, ):
    def qwene_small_question(self, ):
    def multilingual_small_chunks(self, ):
    def bge_small_chunks(self, ):
    def qwene_small_chunks(self, ):

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