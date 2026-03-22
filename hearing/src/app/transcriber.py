from __future__ import annotations

import numpy as np
import whisper


class Transcriber:
    def __init__(self, model_name: str) -> None:
        self._model = whisper.load_model(model_name)

    def transcribe(self, audio_bytes: bytes) -> str:
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        result = self._model.transcribe(audio_np, language="en")
        return result["text"].strip()
