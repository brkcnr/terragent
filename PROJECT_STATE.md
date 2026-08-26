# TerrAgent Project State

**Last Updated**: 2026-08-26  
**Current Milestone**: M2 (Base & NPCs) — Completed  
**Status**: Milestone 2 Complete, Ready for M3  

---

## 1. Executive Summary

TerrAgent is an autonomous Terraria AI agent engineered for zero-cost, local execution on Windows PC using a decoupled architecture:
1. Native C# tModLoader Bridge (`TerrAgentBridge`) running at game tick rate on WebSocket `ws://127.0.0.1:8765`.
2. Python Agent (`terragent`) running a zero-LLM reflex layer with strict Pydantic protocol schemas, persistent SQLite memory, parameterized building templates, and categorized chest storage.

---

## 2. Milestone Progress

- [x] **M1: Bootstrap (Completed)**
  - Project directory structure & packaging (`pyproject.toml`, CI workflow, configs)
  - Architectural documentation & ADRs (`docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/BRIDGE_PROTOCOL.md`)
  - Strict M1 Pydantic schemas (`agent/terragent/schemas.py`)
  - WebSocket Bridge Client with exponential backoff & version handshake (`agent/terragent/bridge_client.py`)
  - Minimal deterministic Reflex loop (`agent/terragent/reflex.py`)
  - C# tModLoader Bridge skeleton (`bridge/`)
  - Fake Bridge integration test suite passing without Terraria installed (`tests/test_bridge_connection.py`)
- [x] **M2: Base & NPCs (Completed)**
  - SQLite persistent memory store for rooms, town NPC roster, categorized chests, and base spawn (`agent/terragent/memory.py`)
  - Parameterized grid-relative room templates (10x6 interior NPC room & player bedroom) conforming to official Terraria housing bounds (`agent/terragent/housing.py`)
  - Programmatic housing verification queries (`query_housing`) and chest queries (`query_chest`) over WebSocket bridge (`agent/terragent/bridge_client.py`)
  - 8-category canonical chest storage engine and deposit/withdrawal routines (`agent/terragent/storage.py`)
  - Bed placement and spawn point setting actions (`SetSpawnCommand`)
  - Complete unit and integration test suite passing without Terraria installed (29/29 tests green)
- [ ] **M3: Pre-hardmode Combat** (Pending review)
- [ ] **M4: Hardmode Transition**
- [ ] **M5: Mechanical Bosses**
- [ ] **M6: Endgame & Moon Lord**

---

## 3. Current Architecture & Boundaries

- **Network**: Localhost WebSocket only (`ws://127.0.0.1:8765`). Protocol version strictly checked on handshake. Request-response queries for housing and chest verification.
- **Persistence**: Relational SQLite storage (`MemoryStore`) for rooms, town NPCs, chests, and spawn point.
- **Templates**: Grid-relative parameterized templates (`StructureTemplate`, `create_standard_npc_room`, `create_player_bedroom`).
- **Storage**: 8 canonical categories (`ores_bars`, `blocks_walls`, `weapons_tools`, `accessories_armor`, `potions_consumables`, `seeds_plants`, `boss_summons_trophies`, `misc`) with automated deposit planning protecting hotbar slots.
- **Testing**: 100% testable without Terraria installed via fake bridge mock server (29 tests passing).

---

## 4. Known Issues & Technical Debt

- None currently identified for M1/M2 scope.

---

## 5. Next Priority

- Await user review and approval of M2.
- Proceed to Milestone 3 (Pre-hardmode combat: arena building, Eye of Cthulhu and evil boss automated combat behaviors, summon farming, and postmortems).
