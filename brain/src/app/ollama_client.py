from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import requests
from requests.auth import HTTPBasicAuth

from shared.config import OllamaConfig
from brain.src.app.conversation import Message

log = logging.getLogger(__name__)


@dataclass
class OllamaResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    duration_ms: float


class OllamaClient:
    def __init__(self, config: OllamaConfig) -> None:
        self._config = config
        self._auth = HTTPBasicAuth(config.user, config.password)
        self._url = config.url.rstrip("/") + "/api/chat"

    def chat(self, messages: list[Message]) -> OllamaResponse:
        payload = {
            "model": self._config.model,
            "messages": messages,
            "stream": False,
        }

        start = time.monotonic()
        response = requests.post(
            self._url,
            json=payload,
            auth=self._auth,
            timeout=120,
        )
        duration_ms = (time.monotonic() - start) * 1000

        response.raise_for_status()
        data = response.json()

        text = data["message"]["content"]
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        log.info(
            "Ollama response received",
            extra={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "duration_ms": round(duration_ms),
                "model": self._config.model,
            },
        )

        return OllamaResponse(
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            duration_ms=duration_ms,
        )
