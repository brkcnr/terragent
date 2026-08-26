# TerrAgent

[![CI](https://github.com/brkcnr/terragent/actions/workflows/ci.yml/badge.svg)](https://github.com/brkcnr/terragent/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**TerrAgent** is an autonomous AI agent engineered to play Terraria (PC, Windows, Classic difficulty) from a fresh character and world to defeating the Moon Lord.

Designed with a decoupled, high-performance architecture, TerrAgent runs at zero cost ($0) using local rule-based reflex execution and budget-managed Gemini free-tier planning.

---

## Key Architecture

- **Zero-Latency Reflex Execution**: Native 60 FPS in-game response without waiting for network or LLM round-trips.
- **tModLoader WebSocket Bridge**: A C# mod broadcasting game state and executing action commands on `ws://127.0.0.1:8765`.
- **Strict Protocol Versioning**: Automated SemVer handshake checking preventing silent protocol desynchronization.
- **Fail-Safe & Self-Healing**: Resilient exponential backoff reconnects, typed action results, and fail-safe reflex survival.

```
Terraria (tModLoader + TerrAgentBridge C#)
               ▲
               │ WebSocket (ws://127.0.0.1:8765)
               ▼
TerrAgent (Python: Reflex Engine + Action API)
```

---

## Quick Start

### 1. Installation

```powershell
# Clone repo
git clone https://github.com/brkcnr/terragent.git
cd terragent

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install in development mode
pip install -e .[dev]
```

### 2. Run Tests (No Terraria Required)

```powershell
pytest -v
```

### 3. Verify Code Quality

```powershell
ruff check .
ruff format --check .
mypy agent tests
```

---

## Repository Structure

```
terragent/
├── agent/terragent/      # Python agent core (schemas, bridge_client, reflex, config)
├── bridge/               # tModLoader C# mod (WebSocket server)
├── configs/              # YAML configuration files (default.yaml)
├── docs/                 # Architecture, Protocol, Setup, Decisions, Troubleshooting
├── tests/                # Unit & fake-bridge integration tests
├── .github/              # CI workflows and issue templates
├── pyproject.toml        # Tooling configuration (ruff, mypy, pytest)
├── PROJECT_STATE.md      # Live project status and milestone tracking
└── README.md
```

---

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Bridge Protocol Specification](docs/BRIDGE_PROTOCOL.md)
- [Architecture Decision Records (ADRs)](docs/DECISIONS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Milestone Roadmap](ROADMAP.md)

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
