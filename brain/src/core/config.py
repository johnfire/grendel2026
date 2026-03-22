from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from shared.config import Config, load_config


@dataclass(frozen=True)
class BrainConfig:
    base: Config
    personality_prompt_path: Path


def load_brain_config(env_path: str | None = None) -> BrainConfig:
    base = load_config(env_path)

    raw = os.getenv("PERSONALITY_PROMPT_PATH", "brain/personality.txt")
    personality_prompt_path = Path(raw)

    return BrainConfig(
        base=base,
        personality_prompt_path=personality_prompt_path,
    )
