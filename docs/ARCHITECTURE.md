# TerrAgent Architecture Specification

## 1. Overview

TerrAgent is an autonomous agent designed to play Terraria (PC, Windows, Classic difficulty) from a fresh character and world to defeating the Moon Lord.

Terraria runs at 60 FPS, whereas LLM inference takes hundreds of milliseconds to several seconds. Putting an LLM in the real-time control loop leads to immediate in-game death and unviable latency. TerrAgent addresses this fundamentally by decoupling **real-time reflex execution** from **hierarchical cognitive planning** across two distinct processes on localhost.

```
+-------------------------------------------------------------------------+
|                              Terraria Process                           |
|                       (tModLoader + TerrAgentBridge)                    |
|       - Native game loop (60 FPS)                                       |
|       - Reads world/player state, exports JSON via WebSocket            |
|       - Receives action commands and executes them in-game              |
+-------------------------------------------------------------------------+
                                    ▲
                                    │ WebSocket (ws://127.0.0.1:8765)
                                    │ Protocol Version Handshake (e.g. 1.0.0)
                                    ▼
+-------------------------------------------------------------------------+
|                             TerrAgent (Python)                          |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  | Input / Perception Layer (bridge_client.py, schemas.py)           |  |
|  | - Reconnect backoff, type-validated Pydantic GameState            |  |
|  +-------------------------------------------------------------------+  |
|                                   │                                     |
|                                   ▼                                     |
|  +-------------------------------------------------------------------+  |
|  | Reflex Layer (reflex.py)                                          |  |
|  | - 10-60 Hz deterministic rule loop (zero LLM calls)               |  |
|  | - Local survival, retreat, health threshold reactions             |  |
|  +-------------------------------------------------------------------+  |
|                                   │                                     |
|                                   ▼                                     |
|  +-------------------------------------------------------------------+  |
|  | Action API & Dispatcher                                           |  |
|  | - Structured, typed ActionCommand & ActionResult                  |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

## 2. Layered Responsibilities

### 2.1 Bridge Mod (C# / tModLoader)
- Runs an embedded WebSocket server listening on `127.0.0.1:8765`.
- Implements strict protocol version handshaking (`protocol_version`) on client connection. Refuses mismatched versions immediately.
- Broadcasts typed `GameState` updates at a configurable frequency (~10 Hz).
- Executes received `ActionCommand` payloads (e.g., `MoveTo`) and responds with typed execution results.

### 2.2 Input & Perception Layer (`schemas.py`, `bridge_client.py`)
- Manages the WebSocket connection with exponential backoff and jitter.
- Enforces data integrity using Pydantic schemas. Unparseable or malformed payloads are caught and logged without crashing the loop.
- Isolates higher-level planning from raw socket communications.

### 2.3 Reflex Layer (`reflex.py`)
- Operates tick-by-tick without network or LLM latency.
- In Milestone 1, provides deterministic baseline survival reactions (e.g. retreating when HP drops below threshold).
- Future milestones will build upon this foundation with Behavior Trees and Utility AI.

## 3. Modularity and Extensibility

- **Action API Contract**: All tactical and strategic decisions emit abstract action commands rather than issuing low-level socket writes directly.
- **Fail-Safe Design**: If any component disconnects, the bridge client handles retries gracefully, and the agent pauses safely.
- **Data-Driven Configuration**: All ports, timeouts, and thresholds are loaded via YAML config files (`configs/default.yaml`).
