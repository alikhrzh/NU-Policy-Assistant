import os

import psycopg


def connect_db():
    return psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5)
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