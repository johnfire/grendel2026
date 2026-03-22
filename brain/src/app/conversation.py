from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)

Message = dict[str, str]  # {"role": "user"|"assistant"|"system", "content": str}


class ConversationHistory:
    def __init__(self, system_prompt: str) -> None:
        self._system: Message = {"role": "system", "content": system_prompt}
        self._messages: list[Message] = []

    @classmethod
    def from_file(cls, path: Path) -> "ConversationHistory":
        try:
            system_prompt = path.read_text(encoding="utf-8").strip()
        except OSError as e:
            log.warning(f"Could not load personality prompt from {path}: {e}. Using empty prompt.")
            system_prompt = ""
        return cls(system_prompt)

    def add_user(self, text: str) -> None:
        self._messages.append({"role": "user", "content": text})

    def add_assistant(self, text: str) -> None:
        self._messages.append({"role": "assistant", "content": text})

    def get_messages(self) -> list[Message]:
        return [self._system] + self._messages

    def __len__(self) -> int:
        return len(self._messages)
