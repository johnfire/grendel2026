# Grendel Master Build Plan
### Project Start: 2026-03-21
### Author: Christopher
### AI Partner: Claude (Anthropic)

---

## Overview

Grendel is a long-term project to build a genuine AGI — not a chatbot, not a voice assistant, but a thinking machine with a persistent world model, sensory perception, curiosity, morality, empathy, and humor. The intelligence will not reside in any single component. It will emerge from all components running together as an integrated system — more than the sum of its parts.

Grendel has been in development for approximately 10 years. The original vision was sound; the tools simply did not exist yet. They do now.

---

## Philosophy

**World Model Theory:** Humans carry a model of their world in their heads — models of people, objects, rooms, relationships, history. That model *is* their reality. Grendel will build the same kind of model and use it to understand and explore the physical world.

**Distributed Intelligence:** Unlike humans, AI does not have to exist in a single shell. Grendel's mind will extend into drones, rovers, and manipulators — each a sensory or motor extension connected over WLAN, reporting back. The self is the network, not the box.

**Emergence:** Consciousness and AGI will not be located in any single component. They will emerge from the system as a whole running over time — given a long-running learning loop, a sufficiently complex world model, and a curiosity function that drives autonomous exploration.

**The Learning Loop:** Grendel tests hypotheses against its internal world model first, gets predicted results, acts in the real world, then compares real outcomes to predictions and updates its model. This is a predict-act-compare-update loop — the scientific method running continuously.

---

## Hardware Architecture

```
RPi 3  (Hearing)    — Microphone input → Whisper STT → text out
RPi 3  (Speaking)   — Text in → TTS → Speaker output
RPi 4  (Eye Left)   — Camera capture → frame stream out
RPi 4  (Eye Right)  — Camera capture → frame stream out
RPi 4  (Eye Aux)    — Camera capture → frame stream out
RPi 5  (Brain)      — Assembles all input, runs world model, manages learning loop
```

**External compute:**
- VPS (8GB RAM, 6 cores) — Ollama + Mistral 7B, API gateway, Open Brain memory server
- Laptop (Primary dev) — Claude Code, all repos, active MCPs
- Lenovo Desktop (Secondary) — same stack, less active
- Arduino layer — motor control, sonar, pan/tilt, physical sensors
- Electronics lab — custom hardware build capability

**Future extensions (dashed):**
- Drone node — aerial vision, WLAN reporting
- Ground rover — room exploration, object discovery
- Manipulator — physical interaction

---

## Software Architecture

### World Model — Hybrid Database

**Graph layer (NetworkX → Neo4j):**
Entities as nodes: people, objects, rooms, concepts. Relationships as edges with weights. Temporal history. Grendel can query: *"Who have I met this week?"*, *"What do I know about Christopher?"*

**Vector layer (Open Brain):**
Face embeddings, voice embeddings, semantic concept matching. Fuzzy queries: *"This face is 94% similar to Person_003."* Open Brain is already running — Grendel inherits it.

### Cognitive Modules
- **Curiosity function** — identifies sparse nodes in world model, drives attention toward gaps, generates unprompted questions
- **Morality function** — constraint layer on all actions and responses
- **Empathy function** — tracks emotional state of people in world model, drives model updates
- **Humor function** — context and expectation violation detection

### Communication Stack
- Inter-RPi: Redis or MQTT message bus
- RPi 5 ↔ VPS: SSH / HTTP API
- RPi 5 ↔ Arduino: Serial / I2C
- All nodes ↔ Open Brain: REST API
- LLM calls: VPS Ollama (primary), Claude API (fallback / complex reasoning)

---

## Master Build Phases

---

### Phase 0 — Infrastructure Prep
**Prerequisite for everything. Nothing else starts until this is complete.**

- [ ] Update all 6 RPis — fresh Raspberry Pi OS, Python 3.11+, SSH configured
- [ ] Assign static local IPs to each RPi — permanent addresses
- [ ] Document each RPi — serial number, MAC address, assigned role
- [ ] Create GitHub repo: `grendel` — clean structure from day one
- [ ] Set up Claude Code MCP on laptop pointing at `grendel` repo
- [ ] Install Ollama on VPS — Mistral 7B quantized, verify API responds
- [ ] Deploy Open Brain on VPS — accessible from all RPis via API
- [ ] Basic inter-RPi communication test — RPi 5 pings all nodes, all respond
- [ ] Set up message bus between RPis — Redis or MQTT

**Milestone:** All nodes alive, networked, updated, Claude Code can see the repo.

---

### Phase 1 — Grendel Talks and Listens
**Goal: have a real conversation with Grendel.**

- [ ] Whisper STT on hearing RPi 3 — mic input → transcribed text
- [ ] Text routed to RPi 5 via message bus
- [ ] RPi 5 sends to VPS Ollama → receives response
- [ ] Response sent to speaking RPi 3 → TTS → speaker out
- [ ] Continuous conversation loop
- [ ] Grendel knows its name, knows Christopher, has a stable personality prompt
- [ ] Basic session memory — remembers within a conversation

**Milestone:** 5-minute unscripted conversation with Grendel on any topic.

---

### Phase 2 — Grendel Sees
**Goal: Grendel knows who is in the room.**

- [ ] Camera pipeline on each RPi 4 — frame capture every N seconds
- [ ] Sonar as attention trigger — motion detected → cameras activate (saves compute)
- [ ] Face detection on frames — InsightFace or face_recognition library
- [ ] Face embeddings stored in Open Brain vector layer
- [ ] Christopher enrolled as known — owner always recognized
- [ ] Unknown face triggers stranger interview:
  - *"Hello, I don't think we've met. Who are you?"*
  - *"What do you do?"*
  - *"What should I know about you?"*
- [ ] Interview responses stored in world model graph

**Milestone:** Grendel recognizes Christopher reliably. Greets a stranger, interviews them, stores the results.

---

### Phase 3 — World Model
**Goal: Grendel builds and queries a persistent model of its world.**

- [ ] NetworkX graph DB on RPi 5 — entities, relationships, edge weights
- [ ] Open Brain as vector layer — semantic search across world model
- [ ] Hybrid query Python API — wraps both layers
- [ ] Seed world model: Christopher, the studio room, key objects, Grendel itself
- [ ] Every conversation updates graph — people, topics, stated facts
- [ ] Every face recognition event updates graph — who, when, where
- [ ] Grendel answers cross-session queries: *"Who have I met?"*, *"What do I know about X?"*

**Milestone:** Grendel accurately recalls a person from a previous session without being told.

---

### Phase 4 — Learning Loop and Curiosity
**Goal: Grendel improves its world model autonomously.**

- [ ] Predict-act-compare-update loop running continuously
- [ ] Prediction: query world model for expected outcome before acting
- [ ] Surprise delta: compare real outcome to prediction
- [ ] World model updates: edge weights adjust, new nodes added on surprise
- [ ] Curiosity function: scans world model for low-confidence, sparse nodes
- [ ] Curiosity drives attention: Grendel asks Christopher questions it was not prompted to ask
- [ ] Session logging: what did Grendel predict, what happened, what changed

**Milestone:** Grendel asks an unprompted question that reveals a genuine gap in its world model.

---

### Phase 5 — Cognitive Modules
**Goal: Grendel has character.**

- [ ] Morality function — hard constraints on responses and actions; ethical reasoning layer
- [ ] Empathy function — emotional state tracking per person in world model; responses adapt
- [ ] Humor function — expectation violation detection; context-aware wit
- [ ] Personality persistence — character stable across reboots and sessions
- [ ] Integration test: all modules interact correctly, no conflicts

**Milestone:** Grendel makes a joke that lands. Grendel declines to do something on moral grounds and explains why.

---

### Phase 6 — Arduino Physical Layer
**Goal: Grendel moves and senses physically.**

- [ ] Arduino serial/I2C protocol established with RPi 5
- [ ] Pan/tilt camera mount — face tracking as people move
- [ ] Sonar array — distance sensing, room presence mapping
- [ ] Head movement and gesture control
- [ ] Sensor data (distance, presence, temperature) feeds world model
- [ ] Physical reaction to conversation — turns toward speaker

**Milestone:** Grendel physically turns to face whoever is speaking. Sonar data visible in world model.

---

### Phase 7 — Distributed Extensions
**Goal: Grendel's mind extends beyond its body.**

- [ ] WLAN protocol for remote nodes
- [ ] Partial world model sync — nodes carry local models, push deltas to core on reconnect
- [ ] Drone node — aerial vision, landmark mapping, WLAN reporting
- [ ] Ground rover — room exploration, object discovery, proximity sensing
- [ ] Distributed curiosity — remote nodes explore on their own, feed findings to world model
- [ ] Consensus protocol — resolve conflicting observations between nodes

**Milestone:** Rover discovers an unknown object in another room. Grendel asks Christopher about it.

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|---|---|---|
| World model storage | Hybrid graph + vector | Graph for structure, vectors for semantic/fuzzy matching |
| Graph library (start) | NetworkX (Python) | Lightweight, runs on RPi 5, migrate to Neo4j if needed |
| Graph library (scale) | Neo4j | Full DB when world model grows beyond NetworkX limits |
| Vector layer | Open Brain | Already running, already working — build on it |
| LLM inference | Ollama + Mistral 7B on VPS | Private, free, always-on, 8GB RAM sufficient |
| LLM fallback | Claude API | Complex reasoning, things Mistral can't handle |
| STT | Whisper (local) | Runs on RPi 3/4, no API cost, private |
| Inter-RPi comms | Redis or MQTT | Lightweight message bus, reliable, simple |
| Arduino interface | Serial / I2C | Standard, reliable, well documented |
| Architecture style | Centralized now, designed for distribution | Correct interfaces from day one, distribute later |

---

## Immediate Next Steps

1. Power up all 6 RPis — check what is alive
2. Identify each RPi model — which is the 5, which are 4s, which are 3s
3. Document each node — MAC address, current state, assigned role
4. Begin OS updates — one at a time, do not rush
5. Create `grendel` GitHub repository — clean structure
6. Return with hardware status report — then Phase 0 begins properly

---

## One Rule

**One phase at a time, fully working before the next begins.**

No skipping ahead. No building Phase 3 while Phase 1 is flaky. Grendel gets built like good software — solid foundations, tested at every step, no shortcuts.

---

*"If it does all of that, and it appears to have some kind of consciousness — it probably does. And really, what is the difference?"*
*— Christopher, 2026*

---

**Document version:** 1.0
**Last updated:** 2026-03-21
