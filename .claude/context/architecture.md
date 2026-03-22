# Architecture — Phase 1

## Data Flow

```
Hearing (105) → [MQTT: grendel/hearing/text] → Brain (106)
                                                      ↓
                                          Ollama API (VPS)
                                                      ↓
Brain (106) → [MQTT: grendel/speaking/text] → Speaking (101)
```

## MQTT Topics

| Topic | Publisher | Subscriber | Payload |
|---|---|---|---|
| `grendel/hearing/text` | Hearing | Brain | transcribed text (string) |
| `grendel/hearing/status` | Hearing | Brain | idle / listening / transcribing |
| `grendel/speaking/text` | Brain | Speaking | response text (string) |
| `grendel/speaking/status` | Speaking | Brain | idle / speaking |
| `grendel/brain/status` | Brain | — | idle / thinking |

## Services

**Hearing (RPi 105):**
- OpenWakeWord — detects "Hey Grendel"
- PyAudio — captures audio post-wake-word
- webrtcvad — VAD, stops on 2s silence or 15s max
- Whisper base — transcribes audio to text
- Publishes to `grendel/hearing/text`

**Brain (RPi 106):**
- Subscribes to `grendel/hearing/text`
- Maintains in-session conversation history
- POSTs to Ollama API with personality prompt + history
- Logs token counts and latency per request
- Publishes response to `grendel/speaking/text`

**Speaking (RPi 101):**
- Subscribes to `grendel/speaking/text`
- Piper TTS — generates audio from text
- aplay — outputs to 3.5mm speaker

## External Services (VPS: 82.165.32.162)

- Mosquitto MQTT broker — :1883
- Ollama + Mistral 7B — localhost:11434 (proxied via Apache HTTPS)
- Supabase (cloud) — grendel_thoughts table
