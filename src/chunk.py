import json
from pathlib import Path


def chunking(document):
    document_id = document["document_id"]
    path = Path("data/processed") / f"{document_id}.json"

    with open(path, "r", encoding="utf-8") as json_file:
        book = json.load(json_file)

    all_words = []
    for page in book:
        for word in page["clean_text"].split():
            all_words.append((word, page["page_number"]))

    chunks = []
    chunk_size = 100
    overlap = 20
    start = 0

    while start < len(all_words):
        chunk_words = all_words[start:start + chunk_size]

        chunk = {
            "chunk_id": f"{document_id}-{len(chunks) + 1:04d}",
            "document_id": document_id,
            "page_start": chunk_words[0][1],
            "page_end": chunk_words[-1][1],
            "text": " ".join(word for word, page_number in chunk_words),
        }
        chunks.append(chunk)

        if start + len(chunk_words) >= len(all_words):
            break

        start += chunk_size - overlap

    return chunks


with open("data/sources.json", "r", encoding="utf-8") as json_file:
    documents = json.load(json_file)

Path("data/chunks").mkdir(parents=True, exist_ok=True)

for document in documents:
    chunks = chunking(document)
    path_save = (
        Path("data/chunks") / f"{document['document_id']}-chunks.json"
    )

    with open(path_save, "w", encoding="utf-8") as json_file:
        json.dump(chunks, json_file, ensure_ascii=False, indent=2)

    print(f"{document['document_id']}: {len(chunks)} chunks")