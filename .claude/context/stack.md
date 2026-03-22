# Stack

## Language
Python 3.10+ on all nodes.

## Per-Node Dependencies

| Node | Key packages |
|---|---|
| Brain | paho-mqtt, requests, python-dotenv |
| Hearing | paho-mqtt, openWakeWord, pyaudio, webrtcvad, openai-whisper, python-dotenv |
| Speaking | paho-mqtt, piper-tts, python-dotenv |
| Eye | paho-mqtt, picamera2, python-dotenv |
| Shared | paho-mqtt, python-dotenv |

## Infrastructure

| Service | Location | Version |
|---|---|---|
| Mosquitto | VPS 82.165.32.162:1883 | 2.0.18 |
| Ollama | VPS localhost:11434 | latest |
| Mistral 7B | VPS (via Ollama) | mistral:7b-instruct-q4_K_M |
| Supabase | Cloud (EU West) | PostgreSQL 17 + pgvector |
| Apache proxy | VPS | 2.4 |
