from sentence_transformers import SentenceTransformer
from pathlib import Path
import json

class EmbeddingStore:
    def __init__(self, model_name="multilingual-e5-small", questions_filename="questions"):
        self.model_name = model_name
        self.questions_filename = questions_filename
        self.model = None
    def get_or_create_question_embeddings(self, ):
        path_embedding_question = Path("data/embeddings/questions") / f"{self.model_name}_{self.questions_filename}_question.json"
        if path_embedding_question.is_file():
            return path_embedding_question
        else:
            match self.model_name:
                case "multilingual-e5-small":
                    return self.multilingual_small_question()
                case "bge-m3":
                    return self.bge_question()
                case "Qwen3-Embedding-0.6B":
                    return self.qwene_question()
                case _:
                    raise SystemExit(f"Нет такой модели. Перезапусти поиск на новом наборе." )


    def get_or_create_chunk_embeddings(self, ):
        path_embedding_chunks = (
                Path("data/embeddings/chunks") / f"{self.model_name}_chunks.json"
        )
        if path_embedding_chunks.is_file():
            return path_embedding_chunks
        else:
            match self.model_name:
                case "multilingual-e5-small":
                    return self.multilingual_small_chunks()
                case "bge-m3":
                    return self.bge_chunks()
                case "Qwen3-Embedding-0.6B":
                    return self.qwene_chunks()
                case _:
                    raise SystemExit(f"Нет такой модели. Перезапусти поиск на новом наборе.")
    def multilingual_small_question(self,):
        model_multilingual = SentenceTransformer("intfloat/multilingual-e5-small")
        path_question = Path("data/eval") / f"{self.questions_filename}.json"
        with open(path_question, "r", encoding="utf-8") as json_file:
            questions = json.load(json_file)
        results = []
        for question in questions:
            result = {}
            result["question_id"] = question["question_id"]
            result["model"] = "multilingual-e5-small"
            query = "query: " + question["question"]
            embedding = model_multilingual.encode(query, convert_to_tensor=True, normalize_embeddings=True)
            result["embedding"] = embedding.tolist()
            results.append(result)
        path_embedding_question = Path("data/embeddings/questions") / f"{self.model_name}_{self.questions_filename}_question.json"
        with open(path_embedding_question, "w", encoding="utf-8") as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=2)
        return path_embedding_question
    def bge_question(self, ):
        model_bge = SentenceTransformer("BAAI/bge-m3")
        path_question = Path("data/eval") / f"{self.questions_filename}.json"
        with open(path_question, "r", encoding="utf-8") as json_file:
            questions = json.load(json_file)
        results = []
        for question in questions:
            result = {}
            result["question_id"] = question["question_id"]
            result["model"] = "bge-m3"
            query = question["question"]
            embedding = model_bge.encode(query, convert_to_tensor=True, normalize_embeddings=True,
                                                  show_progress_bar=True)
            result["embedding"] = embedding.tolist()
            results.append(result)
        path_embedding_question = Path("data/embeddings/questions") / f"{self.model_name}_{self.questions_filename}_question.json"
        with open(path_embedding_question, "w", encoding="utf-8") as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=2)
        return path_embedding_question
    def qwene_question(self, ):
        model_qwene = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
        path_question = Path("data/eval") / f"{self.questions_filename}.json"
        with open(path_question, "r", encoding="utf-8") as json_file:
            questions = json.load(json_file)
        results = []
        for question in questions:
            result = {}
            result["question_id"] = question["question_id"]
            result["model"] = "Qwen3-Embedding-0.6B"
            query = question["question"]
            embedding = model_qwene.encode(query, convert_to_tensor=True, normalize_embeddings=True,
                                         show_progress_bar=True)
            result["embedding"] = embedding.tolist()
            results.append(result)
        path_embedding_question = Path("data/embeddings/questions") / f"{self.model_name}_{self.questions_filename}_question.json"
        with open(path_embedding_question, "w", encoding="utf-8") as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=2)
        return path_embedding_question
    def multilingual_small_chunks(self, ):
        model_multilingual = SentenceTransformer("intfloat/multilingual-e5-small")
        all_chunks = []

        for path in sorted(Path("data/chunks").glob("*-chunks.json")):
            with path.open(encoding="utf-8") as json_file:
                all_chunks.extend(json.load(json_file))

        passages = []
        for chunk in all_chunks:
            passage = "passage: " + chunk["text"]
            passages.append(passage)

        embeddings = model_multilingual.encode(passages, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=True)
        records = []
        for chunk, embedding in zip(all_chunks, embeddings.tolist(), strict=True):
            records.append({
                "chunk_id": chunk["chunk_id"],
                "embedding": embedding,
            })

        path_embedding_chunks = (
                Path("data/embeddings/chunks") / f"{self.model_name}_chunks.json"
        )
        path_embedding_chunks.parent.mkdir(parents=True, exist_ok=True)

        with path_embedding_chunks.open("w", encoding="utf-8") as json_file:
            json.dump(records, json_file, ensure_ascii=False)

        return path_embedding_chunks
    def bge_chunks(self, ):
        model_bge = SentenceTransformer("BAAI/bge-m3")
        all_chunks = []
        for path in sorted(Path("data/chunks").glob("*-chunks.json")):
            with path.open(encoding="utf-8") as json_file:
                all_chunks.extend(json.load(json_file))

        passages = []
        for chunk in all_chunks:
            passage = chunk["text"]
            passages.append(passage)

        embeddings = model_bge.encode(passages, convert_to_tensor=True, normalize_embeddings=True,
                                               show_progress_bar=True)
        records = []
        for chunk, embedding in zip(all_chunks, embeddings.tolist(), strict=True):
            records.append({
                "chunk_id": chunk["chunk_id"],
                "embedding": embedding,
            })

        path_embedding_chunks = (
                Path("data/embeddings/chunks") / f"{self.model_name}_chunks.json"
        )
        path_embedding_chunks.parent.mkdir(parents=True, exist_ok=True)

        with path_embedding_chunks.open("w", encoding="utf-8") as json_file:
            json.dump(records, json_file, ensure_ascii=False)

        return path_embedding_chunks
    def qwene_chunks(self, ):
        model_qwene = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
        all_chunks = []
        for path in sorted(Path("data/chunks").glob("*-chunks.json")):
            with path.open(encoding="utf-8") as json_file:
                all_chunks.extend(json.load(json_file))

        passages = []
        for chunk in all_chunks:
            passage = chunk["text"]
            passages.append(passage)

        embeddings = model_qwene.encode(passages, convert_to_tensor=True, normalize_embeddings=True,
                                      show_progress_bar=True)
        records = []
        for chunk, embedding in zip(all_chunks, embeddings.tolist(), strict=True):
            records.append({
                "chunk_id": chunk["chunk_id"],
                "embedding": embedding,
            })

        path_embedding_chunks = (
                Path("data/embeddings/chunks") / f"{self.model_name}_chunks.json"
        )
        path_embedding_chunks.parent.mkdir(parents=True, exist_ok=True)

        with path_embedding_chunks.open("w", encoding="utf-8") as json_file:
            json.dump(records, json_file, ensure_ascii=False)

        return path_embedding_chunks
    def encode_query(self, question):
        if self.model is None:
            match self.model_name:
                case "multilingual-e5-small":
                    self.model = SentenceTransformer("intfloat/multilingual-e5-small")
                case "bge-m3":
                    self.model = SentenceTransformer("BAAI/bge-m3")
                case "Qwen3-Embedding-0.6B":
                    self.model= SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
                case _:
                    raise SystemExit(f"Нет такой модели. Перезапусти поиск на новом наборе.")
        if self.model_name == "multilingual-e5-small":
            query = "query: " + question
        else:
            query = question
        embedding = self.model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
        return embedding