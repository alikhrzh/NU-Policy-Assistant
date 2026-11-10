import os

import psycopg


def connect_db():
    return psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5)


if __name__ == "__main__":
    with connect_db() as connection:
        result = connection.execute("SELECT 1").fetchone()
        print(f"PostgreSQL connected. SELECT 1 returned {result[0]}.")