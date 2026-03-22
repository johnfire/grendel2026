# Handoff: Grendel Phase 1 — Brain Service Next

## Session Metadata
- Created: 2026-03-22 16:35:05
- Project: /home/christopher/programming/grendel2026
- Branch: main
- Session duration: ~3 hours

### Recent Commits (for context)
- e1a582d Add shared utilities: config loader, logging, MQTT client
- 473199d Initial project structure — Phase 0 complete, Phase 1 begins

## Handoff Chain
- **Continues from**: None (first session)
- **Supersedes**: None

## Current State Summary

Phase 0 infrastructure is 100% complete. The repo structure is built and committed. `shared/` utilities are written and committed. We are at the start of Phase 1 code — the next immediate task is writing the Brain service (`brain/src/`), which is the central coordinator: receives transcribed speech via MQTT, maintains conversation history, calls Ollama on the VPS, logs token usage, and publishes the response back via MQTT.

## Codebase Understanding

### Architecture Overview

6 Raspberry Pis + VPS. Each node runs a dedicated Python service. All inter-node communication via MQTT (Mosquitto on VPS). Ollama (Mistral 7B) runs on VPS, proxied via Apache HTTPS with basic auth. Grendel's memory lives in Supabase (grendel_thoughts table). `shared/` contains common utilities imported by all nodes.

Phase 1 flow:
```
Hearing (105) → MQTT grendel/hearing/text → Brain (106)
                                                   ↓ HTTPS
                                           Ollama on VPS
                                                   ↓
Brain (106) → MQTT grendel/speaking/text → Speaking (101)
```

### Critical Files

| File | Purpose | Relevance |
|------|---------|-----------|
| `shared/config.py` | Typed config loader from .env | All nodes import this |
| `shared/log_setup.py` | Structured JSON logging | All nodes import this |
| `shared/mqtt_client.py` | MQTT wrapper, auto-reconnect | All nodes import this |
| `shared/__init__.py` | Exports Config, load_config, setup_logging, GrendelMQTT | Clean import surface |
| `.env.example` | All required env vars | Copy to .env per node |
| `nodes.yml` | Role → IP mapping | brain=106, hearing=105, speaking=101 |
| `.claude/context/architecture.md` | MQTT topics, data flow | Essential reference |
| `.claude/context/decisions.md` | All ADRs | Essential reference |
| `.claude/context/stack.md` | Package versions per node | Essential reference |

### Key Patterns Discovered

- All nodes use `shared/` via `sys.path` insert or PYTHONPATH — not installed as a package
- Logs go to `~/logs/grendel/<node_name>.log` — NEVER to repo
- Secrets in `.env` per node — never committed
- paho-mqtt 2.1.0 (v2 API) — callback signatures differ from v1, use `CallbackAPIVersion.VERSION2`
- Anti-fragile: handler errors in MQTT client are caught and logged, loop never dies

## Work Completed

### Tasks Finished

- [x] Phase 0: All 6 RPis updated, static IPs assigned, roles documented
- [x] Phase 0: Ollama + Mistral 7B on VPS (CPU-only, 4.4GB q4_K_M)
- [x] Phase 0: Mosquitto MQTT broker on VPS (port 1883, auth required)
- [x] Phase 0: Open Brain — grendel_thoughts table in Supabase
- [x] Phase 0: Ollama Apache reverse proxy (https://christopherrehm.de/ollama/, basic auth)
- [x] Repo structure: brain/, hearing/, speaking/, eye/, shared/, docs/, .claude/
- [x] shared/config.py — typed config dataclasses, fails loudly on missing vars
- [x] shared/log_setup.py — JSON logging, ~/logs/grendel/
- [x] shared/mqtt_client.py — GrendelMQTT, auto-reconnect, isolated handlers

### Files Modified

| File | Changes | Rationale |
|------|---------|-----------|
| `shared/config.py` | New — typed config loader | All nodes need config |
| `shared/log_setup.py` | New — JSON logging | Coding standards compliance |
| `shared/mqtt_client.py` | New — MQTT wrapper | Anti-fragile messaging |
| `shared/__init__.py` | Exports public API | Clean imports |
| `brain/requirements.txt` | paho-mqtt, requests, python-dotenv | Brain dependencies |
| `hearing/requirements.txt` | whisper, pyaudio, webrtcvad, openwakeword | Hearing dependencies |
| `speaking/requirements.txt` | paho-mqtt, python-dotenv (piper TTS coming) | Speaking dependencies |

### Decisions Made

| Decision | Options Considered | Rationale |
|----------|-------------------|-----------|
| MQTT over Redis | Redis Pub/Sub vs MQTT | MQTT purpose-built for IoT, LWT, QoS, retained messages |
| OpenWakeWord | Porcupine vs OpenWakeWord | Fully open source, no API key |
| Piper TTS | espeak-ng, Piper, Coqui | Piper best quality/performance for RPi; espeak-ng for initial testing |
| Session memory: full history | Sliding window, summarisation | Simple, Mistral 32k context won't be hit in practice |
| Ollama via Apache proxy | Open port 11434, SSH tunnel | Apache uses existing SSL cert, adds auth without new ports |
| Folder structure by role | By IP (101-106) | Self-documenting, hardware-independent |
| 15s listen timeout + VAD | 1 min, 30s | 15s feels natural; stop on 2s silence OR 15s max |

## Pending Work

## Immediate Next Steps

1. **Write Brain service** (`brain/src/`) — this is the next task
   - `brain/src/core/config.py` — brain-specific config (personality prompt path)
   - `brain/src/app/conversation.py` — conversation history manager
   - `brain/src/app/ollama_client.py` — Ollama API caller with token logging
   - `brain/src/main.py` — entry point: MQTT subscribe, orchestrate, publish
2. **Write Speaking service** (`speaking/src/`) — simpler, do after Brain
3. **Write Hearing service** (`hearing/src/`) — most complex, use subagent
4. **Write Grendel personality prompt** — work with Christopher on this
5. **Deploy and test end-to-end** — ssh to each RPi, install deps, run services

### Blockers/Open Questions

- [ ] Personality prompt not yet written — needed before Brain can be tested
- [ ] `.env` files not yet created on RPis — needed before deployment

### Deferred Items

- Large binary transport for camera frames — deferred to Phase 2
- Eye service code — deferred to Phase 2
- Tests for shared/ — should be written before Phase 1 is called complete

## Important Context

**Node inventory (confirmed via SSH):**
- 192.168.0.101 — RPi 3B Rev 1.2, 1GB — Speaking
- 192.168.0.102 — RPi 2B Rev 1.1, 1GB — Eye
- 192.168.0.103 — RPi 2B Rev 1.1, 1GB — Eye
- 192.168.0.104 — RPi 2B Rev 1.1, 1GB — Spare
- 192.168.0.105 — RPi 3B+ Rev 1.3, 1GB — Hearing
- 192.168.0.106 — RPi 4B Rev 1.1, 4GB — Brain
- VPS: claude@82.165.32.162 (SSH key: ~/.ssh/id_ed25519)
- All RPis SSH as user `pi`, key-based, no password

**Infrastructure credentials (names only — get values from memory/project_decisions.md):**
- MQTT: broker at VPS:1883, user=grendel
- Ollama proxy: https://christopherrehm.de/ollama/, user=grendel
- Supabase project: qaonmvqhlvrrvfkqcjbf (EU West)

**Christopher's working rules (mandatory):**
- One step at a time — present work, stop, wait for "next"
- Architecture before implementation
- Always present pros/cons for decisions
- No docstrings/comments on code he didn't touch
- Concise, direct, no fluff

**Phase 1 milestone:** 5-minute unscripted conversation with Grendel.

### Assumptions Made

- RPi 2Bs too slow for on-device face detection — Phase 2 processing on Brain/VPS
- 101 (Speaking) has a camera physically attached but unused until Phase 2
- espeak-ng used first to unblock pipeline; swap to Piper once pipeline works
- `shared/` imported via PYTHONPATH, not installed as package

### Potential Gotchas

- paho-mqtt v2 API differs from v1 — always use `CallbackAPIVersion.VERSION2` and new callback signatures
- Ollama proxy strips the `/ollama/` prefix — calls go to `localhost:11434/` on VPS
- Apache SSL vhosts use `82.165.32.162:443` not `*:443` (SNI fix — see vps-setup-euroart.md)
- RPi 2Bs have no camera interface (CSI) — only USB cameras work on them
- `shared/` must be on PYTHONPATH for each node — add to service startup or venv

## Environment State

### Tools/Services Used

- Mosquitto 2.0.18 on VPS — running, systemd, auto-start
- Ollama on VPS — running, systemd, auto-start, model: mistral:7b-instruct-q4_K_M
- Apache on VPS — /ollama/ proxy live, auth configured
- Supabase (cloud) — grendel_thoughts table + match_grendel_thoughts function

### Active Processes

- mosquitto.service (VPS) — active
- ollama.service (VPS) — active
- apache2.service (VPS) — active

### Environment Variables (names only)

- MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
- OLLAMA_URL, OLLAMA_USER, OLLAMA_PASSWORD, OLLAMA_MODEL
- LOG_LEVEL

## Related Resources

- `.claude/context/architecture.md` — MQTT topics, data flow diagram
- `.claude/context/decisions.md` — all ADRs with rationale
- `.claude/context/stack.md` — packages per node
- `.claude/CLAUDE.md` — project overview for Claude
- `nodes.yml` — role to IP mapping
- `/home/christopher/.claude/vps-setup-euroart.md` — VPS config reference
- `/home/christopher/.claude/projects/-home-christopher-programming-grendel2026/memory/` — session memories

---

**Security Reminder**: Credentials stored in memory/project_decisions.md — not in this file.
