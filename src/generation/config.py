import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationConfig:
    url: str = "http://127.0.0.1:11434"
    model: str = "qwen3.5:4b"
    prompt_version: str = "v2"
    temperature: float = 0.2
    seed: int = 42
    num_ctx: int = 8192
    num_predict: int = 400
    keep_alive: str = "5m"
    connect_timeout: float = 5
    read_timeout: float = 120
    neighbors: bool = True
    neighbor_count: int = 1
    expand_top: int = 3
    continuation_only: bool = True

    @classmethod
    def from_env(cls):
        defaults = cls()
        return cls(
            url=os.getenv("OLLAMA_URL", defaults.url),
            model=os.getenv("OLLAMA_MODEL", defaults.model),
            prompt_version=os.getenv("PROMPT_VERSION", defaults.prompt_version),
            temperature=float(os.getenv("OLLAMA_TEMPERATURE", defaults.temperature)),
            seed=int(os.getenv("OLLAMA_SEED", defaults.seed)),
            num_ctx=int(os.getenv("OLLAMA_NUM_CTX", defaults.num_ctx)),
            num_predict=int(os.getenv("OLLAMA_NUM_PREDICT", defaults.num_predict)),
            keep_alive=os.getenv("OLLAMA_KEEP_ALIVE", defaults.keep_alive),
            connect_timeout=float(os.getenv("OLLAMA_CONNECT_TIMEOUT", defaults.connect_timeout)),
            read_timeout=float(os.getenv("OLLAMA_READ_TIMEOUT", defaults.read_timeout)),
            neighbors=os.getenv("GENERATION_NEIGHBORS", "true").lower() in {"1", "true", "yes"},
            neighbor_count=int(os.getenv("GENERATION_NEIGHBOR_COUNT", defaults.neighbor_count)),
            expand_top=int(os.getenv("GENERATION_EXPAND_TOP", defaults.expand_top)),
            continuation_only=os.getenv("GENERATION_CONTINUATION_ONLY", "true").lower()
            in {"1", "true", "yes"},
        )
