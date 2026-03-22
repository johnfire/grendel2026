# Architecture Decision Records

## ADR-001: MQTT over Redis for inter-node messaging
**Date:** 2026-03-22
**Status:** Accepted
**Reason:** Purpose-built for IoT sensor networks. QoS levels, retained messages, LWT node dropout detection. Scales cleanly to Phase 7 drone/rover nodes.
**Consequences:** Redis not used in Phase 1. May be added in Phase 3 for world model caching.

## ADR-002: Ollama + Mistral 7B on VPS (CPU-only)
**Date:** 2026-03-22
**Status:** Accepted
**Reason:** Private, always-on, no API cost. VPS has 11GB RAM — sufficient for 4.4GB quantized model.
**Consequences:** Response latency higher than GPU inference. Acceptable for conversation use case.

## ADR-003: Ollama exposed via Apache reverse proxy (basic auth)
**Date:** 2026-03-22
**Status:** Accepted
**Reason:** Ollama has no built-in auth. Apache proxy adds auth without opening raw port 11434.
**Consequences:** RPi Brain calls `https://christopherrehm.de/ollama/` with credentials.

## ADR-004: Session memory — full history (Option A)
**Date:** 2026-03-22
**Status:** Accepted
**Reason:** Simple, correct. Mistral context window (32k tokens) won't be hit in normal conversation.
**Consequences:** Revisit in Phase 3 when cross-session world model memory is introduced.

## ADR-005: Folder structure by role, not by IP
**Date:** 2026-03-22
**Status:** Accepted
**Reason:** Self-documenting, hardware-independent. IP mapping lives in nodes.yml.
**Consequences:** Deployment scripts read nodes.yml to know which IP to target.

## ADR-006: TTS — Piper (espeak-ng for initial testing)
**Date:** 2026-03-22
**Status:** Accepted
**Reason:** Piper is purpose-built for edge/RPi, good voice quality, fully offline. espeak-ng used early to unblock pipeline testing.

## ADR-007: Wake word — OpenWakeWord
**Date:** 2026-03-22
**Status:** Accepted
**Reason:** Fully open source, no account or API key required. Custom "Hey Grendel" model to be trained.
