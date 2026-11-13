import json
from pathlib import Path

from psycopg.types.json import Jsonb

from src.db.postgres import connect_db


def main():
    documents = json.loads(Path("data/sources.json").read_text(encoding="utf-8"))
    chunk_paths = sorted(Path("data/chunks").glob("*-chunks.json"))
    if not chunk_paths:
        raise FileNotFoundError("No *-chunks.json files found in data/chunks/")

    document_rows = [
        (
            document["document_id"],
            document["filename"],
            Jsonb({
                key: value
                for key, value in document.items()
                if key not in {"document_id", "filename"}
            }),
        )
        for document in documents
    ]

    chunk_rows = []
    for path in chunk_paths:
        for chunk in json.loads(path.read_text(encoding="utf-8")):
            chunk_rows.append((
                chunk["chunk_id"],
                chunk["document_id"],
                chunk["page_start"],
                chunk["page_end"],
                chunk["text"],
            ))

    with connect_db() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO public.documents (document_id, filename, metadata)
                VALUES (%s, %s, %s)
                ON CONFLICT (document_id) DO UPDATE SET
                    filename = EXCLUDED.filename,
                    metadata = EXCLUDED.metadata
                """,
                document_rows,
            )
            cursor.executemany(
                """
                INSERT INTO public.chunks
                    (chunk_id, document_id, page_start, page_end, text)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    document_id = EXCLUDED.document_id,
                    page_start = EXCLUDED.page_start,
                    page_end = EXCLUDED.page_end,
                    text = EXCLUDED.text
                """,
                chunk_rows,
            )

    print(f"Imported {len(document_rows)} documents and {len(chunk_rows)} chunks.")


if __name__ == "__main__":
    main()