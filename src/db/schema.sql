BEGIN;

CREATE TABLE IF NOT EXISTS public.documents (
    document_id text PRIMARY KEY,
    filename text NOT NULL,
    metadata jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS public.chunks (
    chunk_id text PRIMARY KEY,
    document_id text NOT NULL REFERENCES public.documents (document_id),
    page_start integer NOT NULL CHECK (page_start > 0),
    page_end integer NOT NULL CHECK (page_end >= page_start),
    text text NOT NULL
);

CREATE INDEX IF NOT EXISTS chunks_document_id_idx
    ON public.chunks (document_id);

CREATE TABLE IF NOT EXISTS public.search_history (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    result_count integer NOT NULL CHECK (result_count >= 0),
    chunk_ids text[] NOT NULL DEFAULT '{}',
    model_name text,
    rerank_enabled boolean
);

COMMIT;
