from pathlib import Path
from embed import EmbeddingStore
import json
import torch

class RetrievalEvaluator:
    def __init__(self, questions_filename="questions",model_name = "multilingual-e5-small", top_k = 5):
        self.questions_filename = questions_filename
        self.model_name = model_name
        self.top_k = top_k
        self.embedding_store = EmbeddingStore(model_name=model_name, questions_filename=questions_filename)
    def evaluate(self, ):

        question_embedding = self.embedding_store.get_or_create_question_embeddings()
        with question_embedding.open("r", encoding="utf-8") as json_file:
            questions_embeddings = json.load(json_file)
        chunks_embedding = self.embedding_store.get_or_create_chunk_embeddings()
        with chunks_embedding.open("r", encoding="utf-8") as json_file:
            chunks = json.load(json_file)
        path_questions = Path("data/eval") / f"{self.questions_filename}.json"
        with path_questions.open("r", encoding="utf-8") as json_file:
            questions = json.load(json_file)
        questions_by_id = {
            question["question_id"]: question
            for question in questions
        }
        if not 1 <= self.top_k <= len(chunks):
            raise ValueError(
                f"top_k должен быть от 1 до {len(chunks)}."
            )
        chunks_tensor = torch.tensor([chunk["embedding"] for chunk in chunks], dtype=torch.float32,)
        results = []
        for question_record in questions_embeddings:
            question_id = question_record["question_id"]
            question = questions_by_id[question_id]
            query_tensor = torch.tensor(
                question_record["embedding"],
                dtype=torch.float32,
            )
            similarity = chunks_tensor @ query_tensor
            top_scores, top_indices = torch.topk(similarity, k=self.top_k)
            chunk_ids = [chunks[index]["chunk_id"] for index in top_indices.tolist()]
            relevant_ids = set(question["relevant_chunk_ids"])
            ranked_indices = torch.argsort(similarity,descending=True,)
            first_relevant_rank = None
            for rank, index in enumerate(
                    ranked_indices.tolist(),
                    start=1,
            ):
                if chunks[index]["chunk_id"] in relevant_ids:
                    first_relevant_rank = rank
                    break
            results.append({
                "question_id": question_id,
                "chunk_ids": chunk_ids,
                "scores": top_scores.tolist(),
                "first_relevant_rank": first_relevant_rank,
            })

        answerable_questions = [
            question for question in questions
            if question["group"] == "answerable"
               and question["relevant_chunk_ids"]
        ]

        results_by_id = {
            result["question_id"]: result
            for result in results
        }

        hit_at_1 = 0
        hit_at_k = 0

        for question in answerable_questions:
            question_id = question["question_id"]
            rank = results_by_id[question_id]["first_relevant_rank"]

            if rank == 1:
                hit_at_1 += 1

            if rank is not None and rank <= self.top_k:
                hit_at_k += 1

        total = len(answerable_questions)

        return {
            "results": results,
            "metrics": {
                "total_questions": total,
                "top_k": self.top_k,
                "hit_at_1": hit_at_1 / total if total else None,
                f"hit_at_{self.top_k}": hit_at_k / total if total else None,
            },
        }


