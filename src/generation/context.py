import re
from collections import defaultdict

from psycopg.rows import dict_row

from src.db.postgres import connect_db


def load_neighbors(chunk_ids):
    if not chunk_ids:
        return {}
    with connect_db() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT chunk_id, document_id, page_start, page_end, text
                FROM public.chunks WHERE chunk_id = ANY(%s)
                """,
                (sorted(chunk_ids),),
            )
            return {row["chunk_id"]: row for row in cursor}


def neighbor_ids(chunk_id, count):
    prefix, _, suffix = chunk_id.rpartition("-")
    if not prefix or not suffix.isdecimal():
        return []
    number = int(suffix)
    return [
        f"{prefix}-{index:0{len(suffix)}d}"
        for index in range(max(1, number - count), number + count + 1)
        if index != number
    ]


def merge_passages(passages):
    words = []
    previous = None
    for passage in passages:
        current = passage["text"].split()
        overlap = 0
        if previous is not None:
            for size in range(min(20, len(previous), len(current)), 0, -1):
                if previous[-size:] == current[:size]:
                    overlap = size
                    break
        words.extend(current[overlap:])
        previous = current
    return " ".join(words)


def continuation_id(chunk):
    ending = chunk["text"].rstrip().rstrip("\"'”’»)]}").rstrip()
    if not ending or ending.endswith((".", "!", "?", ";")):
        return None
    next_id = neighbor_ids(chunk["chunk_id"], 1)
    return next_id[-1] if next_id else None


def build_sources(chunks, config, *, question=""):
    attendance = re.search(
        r"\battendance\b|\babsences?\b|\bmiss(?:ed|ing)?\b.*\b(?:class(?:es)?|lectures?|lessons?)\b"
        r"|посещаем|пропуск|пропущ|пропуст|отсутств",
        question,
        re.IGNORECASE,
    )
    academic_leave = re.search(
        r"\b(?:academic leave|leave of absence|loa)\b|академическ\w* отпуск|академотпуск|академ\s+отпуск",
        question,
        re.IGNORECASE,
    )
    skip_leave_continuations = attendance and not academic_leave

    ranked = {}
    for chunk in chunks:
        ranked.setdefault(chunk["chunk_id"], chunk)
    originals = set(ranked)
    ranked = list(ranked.values())
    wanted = defaultdict(list)
    if config.neighbors and config.continuation_only:
        for chunk in ranked:
            if skip_leave_continuations and chunk["document_id"] == "leave-dismissal-withdrawal":
                continue
            candidate = continuation_id(chunk)
            if candidate is not None and candidate not in originals:
                wanted[chunk["chunk_id"]].append(candidate)
    elif config.neighbors:
        for chunk in ranked[:config.expand_top]:
            wanted[chunk["chunk_id"]] = [
                candidate for candidate in neighbor_ids(chunk["chunk_id"], config.neighbor_count)
                if candidate not in originals
            ]

    requested_ids = {candidate for ids in wanted.values() for candidate in ids}
    neighbors = load_neighbors(requested_ids) if requested_ids else {}
    seen = set(originals)
    sources = {}
    for rank, chunk in enumerate(ranked, start=1):
        adjacent = []
        for chunk_id in wanted[chunk["chunk_id"]]:
            neighbor = neighbors.get(chunk_id)
            if chunk_id not in seen and neighbor and neighbor["document_id"] == chunk["document_id"]:
                adjacent.append(neighbor)
                seen.add(chunk_id)
        passages = [chunk, *adjacent]
        if adjacent:
            passages.sort(key=lambda item: int(item["chunk_id"].rsplit("-", 1)[-1]))
        sources[rank] = {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "page_start": min(item["page_start"] for item in passages),
            "page_end": max(item["page_end"] for item in passages),
            "neighbor_ids": [item["chunk_id"] for item in adjacent],
            "text": merge_passages(passages) if adjacent else chunk["text"],
        }
    return sources
