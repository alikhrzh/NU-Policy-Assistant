from time import perf_counter

from reranker import Reranker
from retriever import Retriever


question = "Можно ли взять больше 36 кредитов за семестр?"

retriever = Retriever(model_name="bge-m3", top_k=20)
reranker = Reranker(top_n=5)

start = perf_counter()
candidates = retriever.search(question)
retrieval_time = perf_counter() - start

start = perf_counter()
results = reranker.rerank(question, candidates)
reranking_time = perf_counter() - start

print(f"Вопрос: {question}")
print(f"Кандидатов: {len(candidates)}, после реранжирования: {len(results)}")
print(f"Первый поиск: {retrieval_time:.3f} с")
print(f"Первое реранжирование: {reranking_time:.3f} с")

original_ranks = {
    chunk["chunk_id"]: rank
    for rank, chunk in enumerate(candidates, start=1)
}

for rank, chunk in enumerate(results, start=1):
    chunk_id = chunk["chunk_id"]
    print(f"\n#{original_ranks[chunk_id]} → #{rank} | {chunk_id}")
    print(f"Retrieval score: {chunk['score']:.4f}")
    print(f"Rerank score: {chunk['rerank_score']:.4f}")
    print(
        f"Источник: {chunk['document_id']}, "
        f"стр. {chunk['page_start']}–{chunk['page_end']}"
    )
    print(chunk["text"])