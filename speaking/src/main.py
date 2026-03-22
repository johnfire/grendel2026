from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import logging

from shared.log_setup import setup_logging
from shared.mqtt_client import GrendelMQTT
from speaking.src.core.config import load_speaking_config
from speaking.src.app.tts import speak

TOPIC_IN = "grendel/speaking/text"
TOPIC_STATUS = "grendel/speaking/status"

log = logging.getLogger(__name__)


def main() -> None:
    cfg = load_speaking_config()
    setup_logging("speaking", cfg.base.log_level)

    log.info("Speaking service starting")

    mqtt = GrendelMQTT(cfg.base.mqtt, "speaking")

    def on_speaking_text(topic: str, payload: str) -> None:
        text = payload.strip()
        if not text:
            log.warning("Received empty payload — ignoring")
            return

        log.info(f"Speaking: {text!r}")
        mqtt.publish(TOPIC_STATUS, "speaking")
        speak(text, cfg)
        mqtt.publish(TOPIC_STATUS, "idle")

    mqtt.subscribe(TOPIC_IN, on_speaking_text)
    log.info(f"Subscribed to {TOPIC_IN}")

    mqtt.connect_and_run()


if __name__ == "__main__":
    main()
