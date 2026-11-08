from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name="BAAI/bge-reranker-v2-m3", top_n=5):
        self.top_n = top_n
        self.model = CrossEncoder(model_name)

    def rerank(self, question, chunks):
        if not chunks:
            return []

        pairs = [(question, chunk["text"]) for chunk in chunks]
        scores = self.model.predict(pairs)

        reranked_chunks = []
        for chunk, score in zip(chunks, scores):
            reranked_chunk = chunk.copy()
            reranked_chunk["rerank_score"] = float(score)
            reranked_chunks.append(reranked_chunk)

        reranked_chunks.sort(
            key=lambda chunk: chunk["rerank_score"],
            reverse=True,
        )
        return reranked_chunks[:self.top_n]