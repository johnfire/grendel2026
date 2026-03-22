# Handoff: Phase 1 Services Deployed — Pipeline Working

## Session Metadata
- Created: 2026-03-22 19:00:05
- Project: /home/christopher/programming/grendel2026
- Branch: main
- Session duration: ~3.5 hours

### Recent Commits (for context)
- 5542bda Use PulseAudio default device for mic input
- eef737f Feed drain frames through OWW to flush mel feature buffer
- 161f6d3 Drain stale audio after wake word to prevent re-triggering
- 63b5b31 Fix hearing stability: subprocess Whisper + OWW buffer reset
- 66c5ff7 Auto-detect USB mic device index in AudioStream

## Handoff Chain

- **Continues from**: [2026-03-22-163505-phase1-brain-service.md](./2026-03-22-163505-phase1-brain-service.md)
- **Supersedes**: None

## Current State Summary

All three Phase 1 services (Brain, Speaking, Hearing) are written, deployed, and running. The full pipeline works: say "Hey Jarvis" → Whisper transcribes → Brain calls Ollama → Speaking plays response via espeak-ng. End-to-end tested and confirmed working. Christopher heard Grendel respond. The OWW re-trigger bug has had several fixes applied (currently 4s time-based cooldown after each detection). Pipeline is functional but not yet on systemd auto-start.

## Codebase Understanding

### Architecture Overview

All three services run on RPi 106 (Brain 4B) and RPi 101 (Speaking 3B). Hearing was moved from RPi 105 (3B+) to RPi 106 (4B) because PyTorch 2.x requires Cortex-A72+ — the 3B+'s Cortex-A53 is incompatible.

Brain and Hearing are co-located on RPi 106 (4B, 4GB RAM). Each has its own venv. PYTHONPATH=. is set at service startup — shared/ is not installed as a package.

Whisper runs in a subprocess (multiprocessing) for each transcription to prevent native crashes from killing the service. OWW uses `hey_jarvis` model temporarily — custom "hey_grendel" model deferred.

### Critical Files

| File | Purpose | Relevance |
|------|---------|-----------|
| `brain/src/main.py` | Brain entry point | MQTT → Ollama → MQTT |
| `brain/src/app/ollama_client.py` | Ollama API calls | POST to /api/chat, logs tokens |
| `brain/src/app/conversation.py` | Session history | Full history passed to Mistral |
| `brain/personality.txt` | System prompt | Placeholder — work with Christopher to refine |
| `hearing/src/main.py` | Hearing entry point | Wake word → VAD → Whisper → MQTT |
| `hearing/src/app/transcriber.py` | Whisper transcription | Runs in subprocess via multiprocessing |
| `hearing/src/app/wake_word.py` | OWW detector | Uses hey_jarvis model |
| `speaking/src/main.py` | Speaking entry point | MQTT → espeak-ng |
| `nodes.yml` | Role → IP mapping | brain+hearing=106, speaking=101, spares=104+105 |

### Key Patterns Discovered

- Hearing and Brain co-located on 106 — each has its own venv at `brain/venv` and `hearing/venv`
- Services started with: `cd ~/grendel2026 && PYTHONPATH=. nohup <venv>/bin/python <service>/src/main.py > /tmp/<service>.log 2>&1 &`
- Speaking on 101 has its own venv at `speaking/venv`
- numpy must be pinned to `<2` in hearing venv — tflite-runtime (OWW) was compiled against numpy 1.x
- setuptools must be pinned to `<72` in hearing venv — Python 3.13 removed pkg_resources (needed by webrtcvad wrapper)
- USB mic on RPi 106 is C-Media CM108 (card 3). Must use PulseAudio default device (not raw hw) — raw hw device rejects 16kHz
- TMPDIR must be set to /home/pi/tmp when pip-installing on RPi 105/106 — /tmp is 453MB tmpfs, insufficient for PyTorch wheel download

## Work Completed

### Tasks Finished

- [x] Brain service written and deployed to RPi 106
- [x] Speaking service written and deployed to RPi 101
- [x] Hearing service written and deployed to RPi 106 (moved from 105)
- [x] Netcup firewall opened for port 1883 (MQTT) — was blocking all connections
- [x] espeak-ng installed on RPi 101
- [x] portaudio19-dev installed on RPi 106 (required for PyAudio build)
- [x] numpy<2 pinned in hearing venv (tflite compat)
- [x] setuptools<72 installed in hearing venv (pkg_resources compat)
- [x] Full pipeline tested end-to-end — Christopher heard Grendel respond
- [x] OWW re-trigger fix: 4s time-based cooldown after each detection

### Files Modified

| File | Changes | Rationale |
|------|---------|-----------|
| `brain/src/main.py` | New | Brain entry point |
| `brain/src/app/conversation.py` | New | Conversation history manager |
| `brain/src/app/ollama_client.py` | New | Ollama API client with token logging |
| `brain/src/core/config.py` | New | Brain-specific config |
| `brain/personality.txt` | New | Placeholder personality prompt |
| `speaking/src/main.py` | New | Speaking entry point |
| `speaking/src/app/tts.py` | New | espeak-ng wrapper |
| `speaking/src/core/config.py` | New | Speaking config |
| `hearing/src/main.py` | New + multiple fixes | Hearing entry point, re-trigger fixes |
| `hearing/src/app/audio.py` | New | PyAudio stream, PulseAudio default device |
| `hearing/src/app/wake_word.py` | New | OWW detector with reset() |
| `hearing/src/app/transcriber.py` | New | Whisper in subprocess |
| `hearing/src/core/config.py` | New | Hearing config, hey_jarvis default |
| `nodes.yml` | Updated | Hearing moved to 106, 105 demoted to spare |

### Decisions Made

| Decision | Options Considered | Rationale |
|----------|-------------------|-----------|
| Hearing on RPi 106 | RPi 105 (3B+) vs 106 (4B) | Cortex-A53 can't run torch 2.x — SIGILL |
| Whisper in subprocess | In-process vs subprocess | Native crash on 2nd run on ARM; subprocess isolates it |
| PulseAudio for mic | Raw hw:3,0 vs PulseAudio default | Raw hw rejects 16kHz; PulseAudio resamples |
| 4s cooldown for OWW | Frame count drain vs time-based | Time-based more reliable, unaffected by frame rate |

## Pending Work

### Immediate Next Steps

1. **Systemd auto-start** — Brain, Speaking, and Hearing need systemd unit files so they restart on boot and after crashes. Do all three.
2. **Python 3.12 upgrade** — RPi 101 and 106 are on Python 3.9. Christopher wants to upgrade. Discuss impact on venvs (need to rebuild).
3. **OWW re-trigger** — The 4s cooldown appears to be working but needs more testing. Monitor `tail -f /tmp/hearing.log` across multiple interactions.
4. **Personality prompt** — `brain/personality.txt` is a placeholder. Work with Christopher to write a real one.
5. **Tests for shared/** — Deferred from Phase 0, still not written.

### Blockers/Open Questions

- [ ] OWW re-trigger may still occur in some conditions — needs extended testing
- [ ] Whisper subprocess adds ~2s overhead per call (process spawn + model reload) — acceptable for now

### Deferred Items

- Custom "hey_grendel" wake word model — needs audio samples and OWW training
- Piper TTS (swap from espeak-ng) — deferred until pipeline is stable
- Tests for shared/ — deferred to end of Phase 1
- Eye service — Phase 2

## Context for Resuming Agent

### Important Context

**All three services are currently running** on their respective RPis (as of end of session). They were started manually with nohup — they will NOT survive a reboot. Systemd is the immediate next task.

**Credentials are in memory** at `/home/christopher/.claude/projects/-home-christopher-programming-grendel2026/memory/project_decisions.md` — MQTT password and Ollama password are there. .env files already exist on each RPi at `~/grendel2026/.env`.

**Total latency is ~30-40s** — Whisper ~15-20s + Ollama ~10-15s. Christopher is aware and accepts this for now.

**VPS firewall**: Netcup control panel (not UFW, not IONOS) — port 1883 was opened this session. If MQTT stops working, check Netcup panel first.

**hearing venv has pinned deps** that are NOT in requirements.txt:
- `numpy<2` (pinned manually on RPi 106)
- `setuptools<72` (pinned manually on RPi 106)
These need to be added to `hearing/requirements.txt` to survive a clean reinstall.

### Assumptions Made

- OWW `hey_jarvis` model is close enough to "Hey Jarvis" pronunciation for reliable detection
- 4s cooldown is sufficient to prevent OWW re-triggering — needs more real-world testing
- PulseAudio will always route USB mic as default input on RPi 106

### Potential Gotchas

- **Two hearing instances** = MQTT connect/disconnect loop (client ID conflict). Always check `ps aux | grep hearing` before starting.
- **Whisper subprocess** reloads the model every call (~5s overhead). Consider caching the model to disk or using a persistent worker in future.
- **numpy/setuptools pins** not in requirements.txt — clean reinstall will break hearing venv.
- **TMPDIR** must be `/home/pi/tmp` when pip-installing on RPis — /tmp is tmpfs and too small for torch.
- **git pull hint messages** about pull strategy are harmless noise on the RPis.

## Environment State

### Active Processes (at end of session)

- `hearing/venv/bin/python hearing/src/main.py` — RPi 106, PID varies, log at `/tmp/hearing.log`
- `brain/venv/bin/python brain/src/main.py` — RPi 106, log at `/tmp/brain.log`
- `speaking/venv/bin/python speaking/src/main.py` — RPi 101, log at `/tmp/speaking.log`
- `mosquitto.service` — VPS, active
- `ollama.service` — VPS, active

### Environment Variables (names only)

- MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
- OLLAMA_URL, OLLAMA_USER, OLLAMA_PASSWORD, OLLAMA_MODEL
- PERSONALITY_PROMPT_PATH (brain only)
- WHISPER_MODEL, WAKE_WORD_MODEL, LISTEN_TIMEOUT_S, SILENCE_TIMEOUT_S, VAD_AGGRESSIVENESS, SAMPLE_RATE (hearing only)
- TTS_ENGINE, TTS_VOICE, TTS_SPEED (speaking only)
- LOG_LEVEL

## Related Resources

- `.claude/context/architecture.md` — MQTT topics, data flow
- `.claude/context/decisions.md` — ADRs
- `nodes.yml` — role to IP mapping
- `/home/christopher/.claude/projects/-home-christopher-programming-grendel2026/memory/project_decisions.md` — credentials
- Previous handoff: `.claude/handoffs/2026-03-22-163505-phase1-brain-service.md`
