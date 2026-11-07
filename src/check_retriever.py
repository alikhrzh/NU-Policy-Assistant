from time import perf_counter

from retriever import Retriever


question = "Можно ли взять больше 36 кредитов за семестр?"

start = perf_counter()
retriever = Retriever(model_name="bge-m3", top_k=5)
print(f"Создание Retriever: {perf_counter() - start:.3f} с")

start = perf_counter()
results = retriever.search(question)
print(f"Первый поиск: {perf_counter() - start:.3f} с")

for attempt in range(2, 5):
    start = perf_counter()
    retriever.search(question)
    print(f"Поиск {attempt}: {perf_counter() - start:.3f} с")

print(f"Вопрос: {question}")
print(f"Найдено чанков: {len(results)}")

for rank, chunk in enumerate(results, start=1):
    print(f"\n#{rank} | score={chunk['score']:.4f}")
    print(f"Чанк: {chunk['chunk_id']}")
    print(
        f"Источник: {chunk['document_id']}, "
        f"стр. {chunk['page_start']}–{chunk['page_end']}"
    )
    print(chunk["text"])