# Architecture Decision Records (ADRs)

## ADR 001: Separation of Real-Time Reflex Loop and High-Level Planning
- **Status**: Accepted (2026-08-26)
- **Context**: Terraria runs at 60 FPS. Network calls or LLM round-trips can take several seconds. If real-time character survival depends on LLM responses, the character will immediately die.
- **Decision**: Decouple the system into two communicating processes:
  1. A C# tModLoader bridge mod running natively inside Terraria at game tick rate.
  2. A local Python agent with a zero-LLM reflex layer (deterministic local rules in M1, Behavior Trees in later milestones) that executes tick-by-tick actions, alongside an asynchronous tactical/strategic planning layer.
- **Consequences**: Enables immediate local reactions without network lag.

---

## ADR 002: Strict Protocol Versioning and Connection Handshake
- **Status**: Accepted (2026-08-26)
- **Context**: Protocol drift between the C# mod and Python agent during iterative development could cause silent data corruption or undefined behavior.
- **Decision**: Enforce a mandatory handshake phase on WebSocket connection. Both client and server exchange `protocol_version` (SemVer). Any mismatch causes immediate failure and clean disconnection with actionable error messages.
- **Consequences**: Guarantees schema consistency across language boundaries.

---

## ADR 003: Pydantic v2 for State Validation and Serialization
- **Status**: Accepted (2026-08-26)
- **Context**: Game state payloads and action commands must be strongly typed and validated before reaching higher-level layers.
- **Decision**: Use Pydantic v2 models for all incoming and outgoing WebSocket payloads.
- **Consequences**: Clear, explicit validation error messages; robust type hints; zero runtime ambiguity.

---

## ADR 004: Tooling and Code Quality Standards
- **Status**: Accepted (2026-08-26)
- **Context**: Need unified, fast, and strict static analysis, formatting, and test automation.
- **Decision**: Standardize on `ruff` for linting and formatting, `mypy` in strict mode for static typing, and `pytest` with `pytest-asyncio` for unit/integration testing.
- **Consequences**: Sub-second linting, single configuration file (`pyproject.toml`), and zero type ambiguity.

---

## ADR 005: Strict Scope Discipline for Milestone 1
- **Status**: Accepted (2026-08-26)
- **Context**: Specifications outline complex systems for later milestones (bosses, housing, chests, GOAP, LLM budget limiter). Implementing placeholders or half-baked versions prematurely pollutes the codebase and violates incremental engineering.
- **Decision**: In M1, implement strictly the minimal viable components (connection, version handshake, M1 player schema, movement command, basic reflex rule, and fake-bridge test). Omit all future milestone code until their respective milestones.
- **Consequences**: Keeps the codebase clean, tested, and maintainable.

---

## ADR 006: SQLite for Persistent Memory and Chest Indexing
- **Status**: Accepted (2026-08-26)
- **Context**: The agent needs to track housing rooms, assigned NPCs, chest locations, and chest item contents across sessions and trip cycles without losing items or repeating room builds.
- **Decision**: Use an embedded SQLite database (`sqlite3` standard library) managed via a dedicated `MemoryStore` / `Database` layer.
- **Consequences**: Zero external database dependencies, instant transactions, persistent state across restarts.

---

## ADR 007: Parameterized Grid-Relative Building Templates for Housing
- **Status**: Accepted (2026-08-26)
- **Context**: Terraria world seeds and base spawn locations are random. Hardcoding absolute tile coordinates is strictly prohibited.
- **Decision**: Define building templates (e.g. 10x6 interior NPC room, bed bedroom) using relative grid coordinates `(dx, dy, block_type, wall_type, furniture_type)` evaluated from a dynamic base origin.
- **Consequences**: Robust, reusable structure placement that adapts to any world spawn terrain.

---

## ADR 008: Explicit Query-Response Cycle for In-Game Housing & Chests
- **Status**: Accepted (2026-08-26)
- **Context**: In-game housing validity involves complex game rules (corruption proximity, tile integrity, lighting, solid surfaces). Client-side guessing leads to desync.
- **Decision**: Expose programmatic query endpoints (`query_housing`, `query_chest`) on the bridge WebSocket. The agent queries the bridge and verifies validity with the game engine before marking a room as valid or assigning NPCs.
- **Consequences**: 100% accurate housing verification conforming to Terraria's native engine checks.
