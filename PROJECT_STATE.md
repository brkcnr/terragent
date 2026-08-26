# TerrAgent Project State

**Last Updated**: 2026-08-26  
**Current Milestone**: M1 (Bootstrap)  
**Status**: In Progress  

---

## 1. Executive Summary

TerrAgent is an autonomous Terraria AI agent engineered for zero-cost, local execution on Windows PC using a decoupled architecture:
1. Native C# tModLoader Bridge (`TerrAgentBridge`) running at game tick rate on WebSocket `ws://127.0.0.1:8765`.
2. Python Agent (`terragent`) running a zero-LLM reflex layer with strict Pydantic protocol schemas.

---

## 2. Milestone Progress

- [x] **M1: Bootstrap (Current)**
  - Project directory structure & packaging (`pyproject.toml`, CI workflow, configs)
  - Architectural documentation & ADRs (`docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/BRIDGE_PROTOCOL.md`)
  - Strict M1 Pydantic schemas (`agent/terragent/schemas.py`)
  - WebSocket Bridge Client with exponential backoff & version handshake (`agent/terragent/bridge_client.py`)
  - Minimal deterministic Reflex loop (`agent/terragent/reflex.py`)
  - C# tModLoader Bridge skeleton (`bridge/`)
  - Fake Bridge integration test suite passing without Terraria installed (`tests/test_bridge_connection.py`)
- [ ] **M2: Base & NPCs** (Pending M1 approval)
- [ ] **M3: Pre-hardmode Combat**
- [ ] **M4: Hardmode Transition**
- [ ] **M5: Mechanical Bosses**
- [ ] **M6: Endgame & Moon Lord**

---

## 3. Current Architecture & Boundaries

- **Network**: Localhost WebSocket only (`ws://127.0.0.1:8765`). Protocol version strictly checked on handshake.
- **Schemas**: Validated with Pydantic v2 for `GameState`, `HandshakeRequest`, `HandshakeResponse`, `MoveCommand`, and `ActionResult`.
- **Reflex**: Zero LLM calls in the tick loop. Operates strictly via local deterministic rules.
- **Testing**: 100% testable without Terraria installed via fake bridge mock server.

---

## 4. Known Issues & Technical Debt

- None currently identified for M1 scope.

---

## 5. Next Priority

- Complete M1 verification suite (Ruff, Mypy, Pytest).
- Await user review and approval of M1 before commencing M2 (Base & NPCs).
