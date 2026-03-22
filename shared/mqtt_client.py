"""MQTT client wrapper for all Grendel nodes.

Handles connection, reconnection, publishing, and subscription.
A single bad message or handler error will never crash the client loop.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

import paho.mqtt.client as mqtt

from shared.config import MQTTConfig

log = logging.getLogger(__name__)

# Type alias for message handler callbacks
MessageHandler = Callable[[str, str], None]


class GrendelMQTT:
    """MQTT client with auto-reconnect and isolated message dispatch.

    Args:
        config: MQTT connection configuration.
        node_name: Node identifier used as the client ID.
    """

    def __init__(self, config: MQTTConfig, node_name: str) -> None:
        self._config = config
        self._node_name = node_name
        self._handlers: dict[str, MessageHandler] = {}
        self._subscriptions: list[str] = []

        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"grendel-{node_name}",
        )
        self._client.username_pw_set(config.user, config.password)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    # --- Public interface ---

    def subscribe(self, topic: str, handler: MessageHandler) -> None:
        """Register a handler for a topic.

        Args:
            topic: MQTT topic string.
            handler: Callable(topic, payload) called on each message.
        """
        self._handlers[topic] = handler
        self._subscriptions.append(topic)

    def publish(self, topic: str, payload: str, qos: int = 1) -> None:
        """Publish a message to a topic.

        Args:
            topic: MQTT topic string.
            payload: Message payload as string.
            qos: Quality of service level (0, 1, or 2). Defaults to 1.
        """
        try:
            self._client.publish(topic, payload, qos=qos)
        except Exception as e:
            log.error(f"Publish failed on topic {topic}", exc_info=e)

    def connect_and_run(self) -> None:
        """Connect to the broker and start the blocking network loop.

        Retries connection indefinitely on failure with exponential backoff.
        """
        self._connect_with_retry()
        self._client.loop_forever()

    def connect_background(self) -> None:
        """Connect to the broker and start a non-blocking background loop."""
        self._connect_with_retry()
        self._client.loop_start()

    def disconnect(self) -> None:
        """Gracefully disconnect from the broker."""
        self._client.loop_stop()
        self._client.disconnect()

    # --- Internal callbacks ---

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: object,
        connect_flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: object,
    ) -> None:
        if reason_code.is_failure:
            log.error(f"MQTT connect failed: {reason_code}")
            return

        log.info(f"MQTT connected to {self._config.host}:{self._config.port}")

        # Re-subscribe on every connect (handles broker restarts)
        for topic in self._subscriptions:
            client.subscribe(topic, qos=1)
            log.info(f"Subscribed to {topic}")

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: object,
        disconnect_flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: object,
    ) -> None:
        if reason_code.is_failure:
            log.warning(f"MQTT disconnected unexpectedly: {reason_code}. Will reconnect.")

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: object,
        message: mqtt.MQTTMessage,
    ) -> None:
        topic = message.topic
        try:
            payload = message.payload.decode("utf-8")
        except UnicodeDecodeError as e:
            log.error(f"Could not decode message on {topic}", exc_info=e)
            return

        handler = self._handlers.get(topic)
        if handler is None:
            log.warning(f"No handler registered for topic {topic}")
            return

        # Isolate handler errors — one bad message never kills the loop
        try:
            handler(topic, payload)
        except Exception as e:
            log.error(f"Handler error on topic {topic}", exc_info=e)

    def _connect_with_retry(self) -> None:
        """Attempt to connect, retrying with backoff until successful."""
        delay = 2
        max_delay = 60

        while True:
            try:
                self._client.connect(
                    self._config.host,
                    self._config.port,
                    keepalive=60,
                )
                return
            except OSError as e:
                log.warning(
                    f"MQTT connection failed ({e}). Retrying in {delay}s."
                )
                time.sleep(delay)
                delay = min(delay * 2, max_delay)
