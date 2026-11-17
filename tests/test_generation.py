from dataclasses import replace
from unittest.mock import patch

import pytest
import requests

from src.generation.config import GenerationConfig
from src.generation.context import build_sources
from src.generation.generate import generate_answer
from src.generation.validate import validate_citations


def chunk(number, text="A policy sentence.", document_id="policy"):
    return {
        "chunk_id": f"policy-{number:04d}",
        "document_id": document_id,
        "page_start": number,
        "page_end": number,
        "text": text,
    }


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("A rule [1]. Another [1][2]. Third [1, 2].", ([1, 2], [], 0)),
        ("A rule [0, 7].", ([], [0, 7], 0)),
        ("There is no information.", ([], [], 1)),
    ],
)
def test_citations(answer, expected):
    result = validate_citations(answer, 2)
    assert (result["citations"], result["invalid_citations"], result["uncited_sentences"]) == expected


def test_neighbor_overlap_boundaries_and_deduplication():
    overlap = " ".join(f"word{index}" for index in range(20))
    first = chunk(1, f"Start {overlap}")
    second = chunk(2, f"{overlap} end")
    third = chunk(3)
    wrong_document = chunk(4, document_id="another-policy")
    with patch("src.generation.context.load_neighbors", return_value={
        second["chunk_id"]: second, wrong_document["chunk_id"]: wrong_document,
    }) as load:
        sources = build_sources([first, third, first], replace(GenerationConfig(), continuation_only=False))
    load.assert_called_once_with({"policy-0002", "policy-0004"})
    assert list(sources) == [1, 2]
    assert sources[1]["text"] == f"Start {overlap} end"
    assert sources[1]["page_end"] == 2
    assert sources[2]["neighbor_ids"] == []


@pytest.mark.parametrize(
    ("status_code", "payload", "failure", "expected"),
    [
        (200, {}, requests.ConnectionError(), "model_unavailable"),
        (200, {}, requests.Timeout(), "timeout"),
        (404, {}, None, "model_missing"),
        (200, {"message": {"content": "<think>hidden</think>"}}, None, "empty_answer"),
        (200, {"message": {"content": "Answer [1]."}, "done_reason": "length"}, None, "truncated_output"),
    ],
)
def test_client_statuses(status_code, payload, failure, expected):
    config = replace(GenerationConfig(), neighbors=False)
    with patch("src.generation.client.requests.post", side_effect=failure) as post:
        post.return_value.status_code = status_code
        post.return_value.json.return_value = payload
        result = generate_answer("Question?", [chunk(1)], config)
    assert result["status"] == expected
    assert result["answer"] == ("Answer [1]." if expected == "truncated_output" else None)
    post.assert_called_once()


def test_no_sources_skips_ollama():
    with patch("src.generation.client.requests.post") as post:
        assert generate_answer("Question?", [], GenerationConfig())["status"] == "no_sources"
    post.assert_not_called()


def test_continuation_expands_fifth_result_only_if_cut_off():
    chunks = [chunk(number) for number in range(1, 5)]
    overlap = " ".join(f"word{index}" for index in range(20))
    chunks.append(chunk(5, f"Start {overlap}"))
    continuation = chunk(6, f"{overlap} ends here.")
    with patch("src.generation.context.load_neighbors", return_value={"policy-0006": continuation}) as load:
        sources = build_sources(chunks, GenerationConfig())
    load.assert_called_once_with({"policy-0006"})
    assert sources[5]["neighbor_ids"] == ["policy-0006"]
    assert sources[5]["text"] == f"Start {overlap} ends here."
    assert sources[5]["page_end"] == 6


def test_continuation_already_ranked_keeps_its_own_citation():
    with patch("src.generation.context.load_neighbors") as load:
        sources = build_sources([chunk(1, "A cut off"), chunk(2)], GenerationConfig())
    load.assert_not_called()
    assert sources[1]["neighbor_ids"] == []
    assert sources[2]["chunk_id"] == "policy-0002"


@pytest.mark.parametrize(
    "question",
    ["What happens if I miss too many classes?", "Что будет, если я пропущу занятия?"],
)
def test_attendance_skips_leave_continuation(question):
    attendance = chunk(1, "Attendance rules continue")
    leave = {
        **chunk(1, "Leave rules continue", document_id="leave-dismissal-withdrawal"),
        "chunk_id": "leave-dismissal-withdrawal-0001",
    }
    with patch("src.generation.context.load_neighbors", return_value={}) as load:
        sources = build_sources([attendance, leave], GenerationConfig(), question=question)
    load.assert_called_once_with({"policy-0002"})
    assert sources[2]["chunk_id"] == leave["chunk_id"]


def test_explicit_attendance_and_leave_question_can_expand_leave():
    leave = {
        **chunk(1, "Leave rules continue", document_id="leave-dismissal-withdrawal"),
        "chunk_id": "leave-dismissal-withdrawal-0001",
    }
    with patch("src.generation.context.load_neighbors", return_value={}) as load:
        build_sources([leave], GenerationConfig(), question="How does academic leave affect attendance?")
    load.assert_called_once_with({"leave-dismissal-withdrawal-0002"})
