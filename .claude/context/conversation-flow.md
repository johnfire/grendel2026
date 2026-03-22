# Grendel Conversation Flow

What happens at each step when you say "Hey Jarvis":

1. **Wake word detection** — OpenWakeWord continuously listens. When your audio scores above 0.5 for `hey_jarvis`, it triggers.

2. **VAD capture** — webrtcvad records audio frame by frame. Stops on 2 seconds of consecutive silence OR 15 seconds total. This is where your question is captured.

3. **Whisper transcription** — Captured audio is sent to a subprocess that loads Whisper base and runs `model.transcribe()`. Takes ~15-20s on RPi 4B CPU. Returns text.

4. **MQTT publish** — Text published to `grendel/hearing/text`.

5. **Brain receives** — On RPi 106, Brain's MQTT handler fires. Adds your message to conversation history and calls Ollama on the VPS via HTTPS.

6. **Ollama/Mistral thinks** — Mistral 7B runs on VPS CPU. Takes ~10-15s. Returns response text.

7. **Brain publishes response** — Text published to `grendel/speaking/text`.

8. **Speaking receives** — On RPi 101, `espeak-ng` is called with the response text. You hear it.

9. **Cooldown** — Back on RPi 106, OWW resets and 4 seconds of audio is read and discarded. Prevents OWW re-triggering on leftover audio in its buffers.

10. **Back to step 1** — Waiting for the next "Hey Jarvis".

## Total latency: ~30-40 seconds

| Step | Time |
|------|------|
| VAD capture | 2-15s (depends on how long you speak + silence) |
| Whisper transcription | ~15-20s |
| Ollama response | ~10-15s |
| espeak-ng playback | real-time |
