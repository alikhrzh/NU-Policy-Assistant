import logging
import re

import requests

logger = logging.getLogger(__name__)


def ask_ollama(messages, config):
    try:
        response = requests.post(
            f"{config.url.rstrip('/')}/api/chat",
            json={
                "model": config.model,
                "messages": messages,
                "stream": False,
                "think": False,
                "keep_alive": config.keep_alive,
                "options": {
                    "temperature": config.temperature,
                    "seed": config.seed,
                    "num_ctx": config.num_ctx,
                    "num_predict": config.num_predict,
                },
            },
            timeout=(config.connect_timeout, config.read_timeout),
        )
        if response.status_code == 404:
            return "model_missing", None, {}, [f"Install the model with ollama pull {config.model}."]
        response.raise_for_status()
        data = response.json()
        answer = re.sub(r"<think>.*?</think>", "", data["message"]["content"], flags=re.S).strip()
    except requests.Timeout:
        return "timeout", None, {}, ["Ollama timed out."]
    except requests.ConnectionError:
        return "model_unavailable", None, {}, ["Could not connect to the configured Ollama server."]
    except (requests.RequestException, ValueError, KeyError, TypeError):
        logger.exception("Ollama request failed")
        return "error", None, {}, ["Ollama could not generate an answer."]

    metrics = {
        key: data.get(key)
        for key in ("prompt_eval_count", "eval_count", "done_reason", "total_duration",
                    "load_duration", "prompt_eval_duration", "eval_duration")
    }
    warnings = []
    count = metrics["prompt_eval_count"]
    if isinstance(count, int) and count + config.num_predict >= config.num_ctx * 0.95:
        warnings.append("The request was close to the context limit.")
    if not answer:
        return "empty_answer", None, metrics, [*warnings, "Ollama returned an empty answer."]
    if metrics["done_reason"] == "length":
        return "truncated_output", answer, metrics, [*warnings, "The answer reached the output limit."]
    return "ok", answer, metrics, warnings
