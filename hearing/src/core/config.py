from __future__ import annotations

import os
from dataclasses import dataclass

from shared.config import Config, load_config


@dataclass(frozen=True)
class HearingConfig:
    base: Config
    whisper_model: str
    wake_word_model: str
    listen_timeout_s: int
    silence_timeout_s: int
    vad_aggressiveness: int
    sample_rate: int


def load_hearing_config(env_path: str | None = None) -> HearingConfig:
    base = load_config(env_path)
    return HearingConfig(
        base=base,
        whisper_model=os.getenv("WHISPER_MODEL", "base"),
        wake_word_model=os.getenv("WAKE_WORD_MODEL", "hey_jarvis"),
        listen_timeout_s=int(os.getenv("LISTEN_TIMEOUT_S", "15")),
        silence_timeout_s=int(os.getenv("SILENCE_TIMEOUT_S", "2")),
        vad_aggressiveness=int(os.getenv("VAD_AGGRESSIVENESS", "2")),
        sample_rate=int(os.getenv("SAMPLE_RATE", "16000")),
    )
