import json
import torch

from src.db.postgres import load_chunks
from src.retrieval.embed import EmbeddingStore


class Retriever:
    def __init__(self, model_name="multilingual-e5-small", top_k=5):
        self.model_name = model_name
        self.top_k = top_k
        self.embedding_store = EmbeddingStore(self.model_name)
        path_to_chunks = self.embedding_store.get_or_create_chunk_embeddings()
        with path_to_chunks.open("r", encoding="utf-8") as json_file:
            self.chunks = json.load(json_file)
        if not 1 <= self.top_k <= len(self.chunks ):
            raise ValueError(
                f"top_k должен быть от 1 до {len(self.chunks)}."
            )
        self.chunks_tensor = torch.tensor([chunk["embedding"] for chunk in self.chunks ], dtype=torch.float32)

    def search(self, question: str):
        query_embedding = self.embedding_store.encode_query(question)
        query_embedding = query_embedding.to(
            device=self.chunks_tensor.device,
            dtype=self.chunks_tensor.dtype,
        )

        scores = self.chunks_tensor @ query_embedding
        k = min(self.top_k, len(self.chunks))
        top_scores, top_indices = torch.topk(scores, k=k)

        chunk_ids = [self.chunks[index]["chunk_id"] for index in top_indices.tolist()]
        chunks_by_id = load_chunks(chunk_ids)
        return [
            dict(chunks_by_id[chunk_id], score=score)
            for chunk_id, score in zip(chunk_ids, top_scores.tolist(), strict=True)
        ]
