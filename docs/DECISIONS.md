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
