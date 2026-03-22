from __future__ import annotations

import numpy as np
from openwakeword.model import Model

DETECTION_THRESHOLD = 0.5


class WakeWordDetector:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model = Model(wakeword_models=[model_name])

    def process(self, frame_bytes: bytes) -> bool:
        audio = np.frombuffer(frame_bytes, dtype=np.int16)
        prediction = self._model.predict(audio)
        score = prediction.get(self._model_name, 0.0)
        return score > DETECTION_THRESHOLD
