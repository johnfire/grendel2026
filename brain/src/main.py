from __future__ import annotations

import sys
from pathlib import Path

# Ensure shared/ is on the path when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import logging

from shared.log_setup import setup_logging
from brain.src.core.config import load_brain_config
from brain.src.app.conversation import ConversationHistory
from brain.src.app.ollama_client import OllamaClient
from shared.mqtt_client import GrendelMQTT

TOPIC_IN = "grendel/hearing/text"
TOPIC_OUT = "grendel/speaking/text"
TOPIC_STATUS = "grendel/brain/status"

log = logging.getLogger(__name__)


def main() -> None:
    cfg = load_brain_config()
    setup_logging("brain", cfg.base.log_level)

    log.info("Brain service starting")

    history = ConversationHistory.from_file(cfg.personality_prompt_path)
    ollama = OllamaClient(cfg.base.ollama)
    mqtt = GrendelMQTT(cfg.base.mqtt, "brain")

    def on_hearing_text(topic: str, payload: str) -> None:
        text = payload.strip()
        if not text:
            log.warning("Received empty payload on hearing/text — ignoring")
            return

        log.info(f"Heard: {text!r}")
        mqtt.publish(TOPIC_STATUS, "thinking")

        history.add_user(text)

        try:
            response = ollama.chat(history.get_messages())
        except Exception as e:
            log.error("Ollama request failed", exc_info=e)
            mqtt.publish(TOPIC_STATUS, "idle")
            return

        history.add_assistant(response.text)
        log.info(f"Responding: {response.text!r}")

        mqtt.publish(TOPIC_OUT, response.text)
        mqtt.publish(TOPIC_STATUS, "idle")

    mqtt.subscribe(TOPIC_IN, on_hearing_text)
    log.info(f"Subscribed to {TOPIC_IN}, publishing to {TOPIC_OUT}")

    mqtt.connect_and_run()


if __name__ == "__main__":
    main()
