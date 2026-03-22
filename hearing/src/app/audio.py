from __future__ import annotations

import pyaudio

CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 480  # 30ms at 16kHz


class AudioStream:
    def __init__(self, sample_rate: int) -> None:
        self._sample_rate = sample_rate
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=sample_rate,
            input=True,
            frames_per_buffer=CHUNK,
        )

    def read_chunk(self) -> bytes:
        return self._stream.read(CHUNK, exception_on_overflow=False)

    def close(self) -> None:
        self._stream.stop_stream()
        self._stream.close()
        self._pa.terminate()
