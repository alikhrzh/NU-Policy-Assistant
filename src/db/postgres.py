import os

import psycopg
from psycopg.rows import dict_row


class ChunkCorpusError(RuntimeError):
    pass


def connect_db():
    return psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5)

def load_chunks(chunk_ids: list[str]) -> dict:
    if not chunk_ids:
        return {}

    with connect_db() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT chunk_id, document_id, page_start, page_end, text
                FROM public.chunks
                WHERE chunk_id = ANY(%s)
                """,
                (chunk_ids,),
            )
            chunks = {chunk["chunk_id"]: chunk for chunk in cursor}

    missing_ids = [chunk_id for chunk_id in chunk_ids if chunk_id not in chunks]
    if missing_ids:
        raise ChunkCorpusError(
            "PostgreSQL is missing chunks from the embedding cache: "
            + ", ".join(missing_ids)
        )
    return chunks


def save_search(
    question: str,
    chunk_ids: list[str],
    model_name: str,
    rerank_enabled: bool,
) -> None:
    result_count = len(chunk_ids)

    with connect_db() as connection:
        connection.execute(
            """
            INSERT INTO public.search_history (
                question,
                result_count,
                chunk_ids,
                model_name,
                rerank_enabled
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (question, result_count, chunk_ids, model_name, rerank_enabled),
        )


if __name__ == "__main__":
    with connect_db() as connection:
        result = connection.execute("SELECT 1").fetchone()
        print(f"PostgreSQL connected. SELECT 1 returned {result[0]}.")