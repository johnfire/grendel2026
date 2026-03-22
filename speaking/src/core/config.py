from __future__ import annotations

import os
from dataclasses import dataclass

from shared.config import Config, load_config


@dataclass(frozen=True)
class SpeakingConfig:
    base: Config
    tts_engine: str   # "espeak" | "piper"
    tts_voice: str    # espeak voice string, e.g. "en-gb"
    tts_speed: int    # espeak words-per-minute


def load_speaking_config(env_path: str | None = None) -> SpeakingConfig:
    base = load_config(env_path)

    return SpeakingConfig(
        base=base,
        tts_engine=os.getenv("TTS_ENGINE", "espeak"),
        tts_voice=os.getenv("TTS_VOICE", "en-gb"),
        tts_speed=int(os.getenv("TTS_SPEED", "150")),
    )
