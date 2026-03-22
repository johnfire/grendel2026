"""Shared configuration loader for all Grendel nodes."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class MQTTConfig:
    host: str
    port: int
    user: str
    password: str


@dataclass(frozen=True)
class OllamaConfig:
    url: str
    user: str
    password: str
    model: str


@dataclass(frozen=True)
class Config:
    mqtt: MQTTConfig
    ollama: OllamaConfig
    log_level: str


def load_config(env_path: str | None = None) -> Config:
    """Load configuration from environment variables.

    Searches for .env in the provided path, then current directory,
    then the repo root. Raises EnvironmentError if required vars are missing.

    Args:
        env_path: Optional explicit path to a .env file.

    Returns:
        Populated Config object.

    Raises:
        EnvironmentError: If any required environment variable is missing.
    """
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    missing: list[str] = []

    def require(key: str) -> str:
        value = os.getenv(key)
        if not value:
            missing.append(key)
            return ""
        return value

    mqtt = MQTTConfig(
        host=require("MQTT_HOST"),
        port=int(os.getenv("MQTT_PORT", "1883")),
        user=require("MQTT_USER"),
        password=require("MQTT_PASSWORD"),
    )

    ollama = OllamaConfig(
        url=require("OLLAMA_URL"),
        user=require("OLLAMA_USER"),
        password=require("OLLAMA_PASSWORD"),
        model=os.getenv("OLLAMA_MODEL", "mistral:7b-instruct-q4_K_M"),
    )

    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return Config(
        mqtt=mqtt,
        ollama=ollama,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
