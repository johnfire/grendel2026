from __future__ import annotations

import logging
import subprocess

from speaking.src.core.config import SpeakingConfig

log = logging.getLogger(__name__)


def speak(text: str, cfg: SpeakingConfig) -> None:
    if cfg.tts_engine == "espeak":
        _speak_espeak(text, cfg)
    else:
        log.error(f"Unknown TTS engine: {cfg.tts_engine!r}. No audio produced.")


def _speak_espeak(text: str, cfg: SpeakingConfig) -> None:
    cmd = [
        "espeak-ng",
        "-v", cfg.tts_voice,
        "-s", str(cfg.tts_speed),
        text,
    ]
    try:
        subprocess.run(cmd, check=True, timeout=60)
    except FileNotFoundError:
        log.error("espeak-ng not found — install with: sudo apt install espeak-ng")
    except subprocess.TimeoutExpired:
        log.error(f"espeak-ng timed out speaking: {text!r}")
    except subprocess.CalledProcessError as e:
        log.error(f"espeak-ng exited with code {e.returncode}")
