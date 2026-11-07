import json
from embed import EmbeddingStore
import torch
from pathlib import Path

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
        self.chunks_by_id = {}

        for path in Path("data/chunks").glob("*-chunks.json"):
            with path.open(encoding="utf-8") as json_file:
                for chunk in json.load(json_file):
                    self.chunks_by_id[chunk["chunk_id"]] = chunk

    def search(self, question: str):
        query_embedding = self.embedding_store.encode_query(question)
        query_embedding = query_embedding.to(self.chunks_tensor.device)

        scores = self.chunks_tensor @ query_embedding
        k = min(self.top_k, len(self.chunks))
        top_scores, top_indices = torch.topk(scores, k=k)

        results = []
        for score, index in zip(top_scores.tolist(), top_indices.tolist()):
            chunk_id = self.chunks[index]["chunk_id"]
            chunk = self.chunks_by_id[chunk_id]
            results.append({
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
                "text": chunk["text"],
                "score": score,
            })

        return results

