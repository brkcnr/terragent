# TerrAgent Project State

**Last Updated**: 2026-08-26  
**Current Milestone**: M3 (Pre-hardmode Combat) — Completed  
**Status**: Milestone 3 Complete, Ready for M4  

---

## 1. Executive Summary

TerrAgent is an autonomous Terraria AI agent engineered for zero-cost, local execution on Windows PC using a decoupled architecture:
1. Native C# tModLoader Bridge (`TerrAgentBridge`) running at game tick rate on WebSocket `ws://127.0.0.1:8765`.
2. Python Agent (`terragent`) running a zero-LLM reflex combat engine with lead aiming, vector-based kiting controllers, multi-tiered arena generation, persistent SQLite memory, and postmortem failure analysis.

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
- [x] **M3: Pre-hardmode Combat (Completed)**
  - Data-driven boss strategies configuration (`configs/boss_strategies.yaml`) covering Eye of Cthulhu, Eater of Worlds, and Brain of Cthulhu
  - Multi-tiered platform arena generator with campfires, heart lanterns, and sunflowers (`agent/terragent/arena.py`)
  - Deterministic reflex combat engine with circle kiting, horizontal platform sprinting, predictive lead aiming, weapon switching, and auto-potion healing (`agent/terragent/combat.py`)
  - SQLite-backed postmortem failure analysis and attempt limiter (`agent/terragent/postmortem.py`)
  - Full unit and fake bridge test suite (38/38 tests passing green)
- [ ] **M4: Hardmode Transition** (Pending review)
- [ ] **M5: Mechanical Bosses**
- [ ] **M6: Endgame & Moon Lord**

---

## 3. Current Architecture & Boundaries

- **Combat Engine**: Sub-millisecond vector math calculations (`circle_kite`, `horizontal_run`, `calculate_lead_aim`), weapon slot switching, and potion management.
- **Arena Builder**: Multi-level wooden platform generator with life regeneration auras (Campfires, Heart Lanterns) and movement speed boosts (Sunflowers).
- **Strategies**: Declarative YAML configuration (`configs/boss_strategies.yaml`) specifying phase triggers, gear minimums, and combat patterns.
- **Postmortem**: Historical battle logging and failure diagnostics (`PostmortemManager`) to adapt combat strategies between attempts.
- **Testing**: 100% testable without Terraria installed via fake bridge mock server (38 tests passing).

---

## 4. Known Issues & Technical Debt

- None currently identified for M1/M2/M3 scope.

---

## 5. Next Priority

- Proceed to Milestone 4 (Hardmode Transition: Skeletron defeat, Dungeon loot acquisition, Underworld hellstone tier, hellbridge construction, and Wall of Flesh battle).
