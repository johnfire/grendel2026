from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import logging

import webrtcvad

from shared.log_setup import setup_logging
from shared.mqtt_client import GrendelMQTT
from hearing.src.core.config import load_hearing_config
from hearing.src.app.audio import AudioStream, CHUNK
from hearing.src.app.wake_word import WakeWordDetector
from hearing.src.app.transcriber import Transcriber

TOPIC_TEXT = "grendel/hearing/text"
TOPIC_STATUS = "grendel/hearing/status"

log = logging.getLogger(__name__)

BYTES_PER_FRAME = CHUNK * 2  # 16-bit = 2 bytes per sample


def listen_until_silence(
    stream: AudioStream,
    vad: webrtcvad.Vad,
    sample_rate: int,
    silence_timeout_s: int,
    listen_timeout_s: int,
) -> bytes:
    frames_per_second = sample_rate / CHUNK
    silence_frame_limit = int(silence_timeout_s * frames_per_second)
    max_frames = int(listen_timeout_s * frames_per_second)

    captured: list[bytes] = []
    silent_frames = 0

    for _ in range(max_frames):
        chunk = stream.read_chunk()
        captured.append(chunk)
        is_speech = vad.is_speech(chunk, sample_rate=sample_rate)
        if is_speech:
            silent_frames = 0
        else:
            silent_frames += 1
            if silent_frames >= silence_frame_limit:
                break

    return b"".join(captured)


def run_pipeline(
    stream: AudioStream,
    wake_word: WakeWordDetector,
    transcriber: Transcriber,
    vad: webrtcvad.Vad,
    mqtt: GrendelMQTT,
    cfg,
) -> None:
    log.info("Waiting for wake word")
    mqtt.publish(TOPIC_STATUS, "idle")

    while True:
        chunk = stream.read_chunk()
        if wake_word.process(chunk):
            log.info("Wake word detected")
            mqtt.publish(TOPIC_STATUS, "listening")

            audio = listen_until_silence(
                stream,
                vad,
                cfg.sample_rate,
                cfg.silence_timeout_s,
                cfg.listen_timeout_s,
            )
            log.info(f"Captured {len(audio)} bytes of audio")

            mqtt.publish(TOPIC_STATUS, "transcribing")
            text = transcriber.transcribe(audio)
            log.info(f"Transcribed: {text!r}")

            if text:
                mqtt.publish(TOPIC_TEXT, text)

            wake_word.reset()
            # Cooldown: read and discard 4s so OWW buffer fully settles
            cooldown_end = time.monotonic() + 4.0
            while time.monotonic() < cooldown_end:
                stream.read_chunk()
            mqtt.publish(TOPIC_STATUS, "idle")
            log.info("Returning to wake word detection")


def main() -> None:
    cfg = load_hearing_config()
    setup_logging("hearing", cfg.base.log_level)

    log.info("Hearing service starting")

    log.info(f"Loading Whisper model: {cfg.whisper_model}")
    t0 = time.monotonic()
    transcriber = Transcriber(cfg.whisper_model)
    log.info(f"Whisper loaded in {time.monotonic() - t0:.1f}s")

    log.info(f"Loading OpenWakeWord model: {cfg.wake_word_model}")
    wake_word = WakeWordDetector(cfg.wake_word_model)
    log.info("OpenWakeWord loaded")

    vad = webrtcvad.Vad(cfg.vad_aggressiveness)

    mqtt = GrendelMQTT(cfg.base.mqtt, "hearing")
    mqtt.connect_background()

    stream = AudioStream(cfg.sample_rate)
    log.info("Audio stream opened")

    try:
        while True:
            try:
                run_pipeline(stream, wake_word, transcriber, vad, mqtt, cfg)
            except Exception as e:
                log.error("Pipeline error — restarting", exc_info=e)
                time.sleep(1)
    except KeyboardInterrupt:
        log.info("Shutting down")
    finally:
        stream.close()
        mqtt.disconnect()
        log.info("Hearing service stopped")


if __name__ == "__main__":
    main()
