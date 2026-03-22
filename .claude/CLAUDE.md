# Grendel — Claude Context

## Project
AGI system built on 6 Raspberry Pis + VPS. Each node runs a dedicated Python service communicating over MQTT.

## Current Phase
**Phase 1** — Grendel talks and listens.
Goal: 5-minute unscripted conversation.

## Entry Points by Node

| Node | Entry point |
|---|---|
| Brain | `brain/src/main.py` |
| Hearing | `hearing/src/main.py` |
| Speaking | `speaking/src/main.py` |
| Eye | `eye/src/main.py` |

## Run Commands
Each node runs its service directly:
```bash
python brain/src/main.py
python hearing/src/main.py
python speaking/src/main.py
```

## Key Constraints
- Python 3.10+ on all nodes
- Each node has its own `venv` and `requirements.txt`
- Secrets in `.env` per node — never committed
- Logs to `~/logs/` on each RPi, never to the repo
- MQTT broker: `82.165.32.162:1883` (user: grendel)
- Ollama API: `https://christopherrehm.de/ollama` (basic auth)
- Do NOT touch `shared/` without considering impact on all nodes

## Do Not Touch
- `.env` files on any node
- `/etc/mosquitto/` on VPS
- `/etc/apache2/` on VPS (unless fixing Ollama proxy)
