from __future__ import annotations

import logging
import multiprocessing
import numpy as np
import whisper

log = logging.getLogger(__name__)


def _transcribe_worker(model_name: str, audio_bytes: bytes, result_queue: multiprocessing.Queue) -> None:
    model = whisper.load_model(model_name)
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    result = model.transcribe(audio_np, language="en")
    result_queue.put(result["text"].strip())


class Transcriber:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name

    def transcribe(self, audio_bytes: bytes) -> str:
        q: multiprocessing.Queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=_transcribe_worker, args=(self._model_name, audio_bytes, q))
        p.start()
        p.join(timeout=120)

        if p.exitcode != 0:
            log.error(f"Whisper subprocess crashed with exit code {p.exitcode}")
            return ""

        return q.get() if not q.empty() else ""
