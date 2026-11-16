import logging
from dataclasses import asdict
from hashlib import sha256
from time import perf_counter

from .client import ask_ollama
from .config import GenerationConfig
from .context import build_sources
from .prompts import PROMPTS, build_messages
from .validate import validate_citations

logger = logging.getLogger(__name__)


def generate_answer(question, chunks, config=None):
    started = perf_counter()
    result = {
        "status": "error",
        "answer": None,
        "warnings": [],
        "sources": {},
        "citations": [],
        "invalid_citations": [],
        "uncited_sentences": 0,
        "model": None,
        "prompt_version": None,
        "prompt_hash": None,
        "parameters": {},
        "metrics": {},
        "top_rerank_score": None,
    }
    try:
        config = config or GenerationConfig.from_env()
        prompt = PROMPTS[config.prompt_version]
        result.update(
            model=config.model,
            prompt_version=config.prompt_version,
            prompt_hash=sha256(prompt.encode()).hexdigest()[:12],
            parameters=asdict(config),
        )
        if not chunks:
            result.update(status="no_sources", warnings=["No sources were retrieved."])
            return result

        result["top_rerank_score"] = chunks[0].get("rerank_score")
        sources = build_sources(chunks, config)
        result["sources"] = sources
        messages = build_messages(question, sources, config.prompt_version)
        status, answer, metrics, warnings = ask_ollama(messages, config)
        result.update(status=status, answer=answer, metrics=metrics, warnings=warnings)
        if answer:
            result.update(validate_citations(answer, len(sources)))
            if result["invalid_citations"]:
                warnings.append("The answer cites unavailable source numbers.")
            if result["uncited_sentences"]:
                warnings.append(f"Sentences without citations: {result['uncited_sentences']}.")
    except Exception:
        logger.exception("Answer generation failed")
        result.update(status="error", answer=None, warnings=["Could not generate the answer."])
    finally:
        result["elapsed_ms"] = (perf_counter() - started) * 1000
    return result
