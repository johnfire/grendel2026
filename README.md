# Grendel

A long-term project to build a genuine AGI — a thinking machine with a persistent world model, sensory perception, curiosity, morality, empathy, and humor.

## Node Map

| Role | IP | Hardware |
|---|---|---|
| Brain | 192.168.0.106 | RPi 4 Model B, 4GB |
| Hearing | 192.168.0.105 | RPi 3 Model B+, 1GB |
| Speaking | 192.168.0.101 | RPi 3 Model B, 1GB |
| Eye (x2) | 192.168.0.102, .103 | RPi 2 Model B, 1GB |
| Spare | 192.168.0.104 | RPi 2 Model B, 1GB |

## Repository Structure

```
brain/       — Central coordinator. Manages conversation, calls Ollama, routes messages.
hearing/     — Whisper STT. Wake word detection, audio capture, transcription.
speaking/    — Piper TTS. Receives text, synthesises speech, plays audio.
eye/         — Camera capture. Frame streaming (Phase 2).
shared/      — Common utilities: MQTT client, logging, config loader.
scripts/     — Setup and deployment scripts.
docs/        — Architecture and planning documents.
```

## Build Phases

- **Phase 0** — Infrastructure ✓
- **Phase 1** — Grendel talks and listens
- **Phase 2** — Grendel sees
- **Phase 3** — World model
- **Phase 4** — Learning loop and curiosity
- **Phase 5** — Cognitive modules
- **Phase 6** — Arduino physical layer
- **Phase 7** — Distributed extensions

See [docs/grendel_master_plan.md](docs/grendel_master_plan.md) for the full build plan.

## Support

If you find this useful, a small donation helps keep projects like this going:
[Donate via PayPal](https://paypal.me/christopherrehm001)
