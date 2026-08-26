# TerrAgent Setup Guide

This guide walks through setting up TerrAgent on a Windows 10/11 machine.

## Prerequisites

1. **Python**: Python 3.11 or higher installed on your system with pip.
2. **Terraria & tModLoader**: Available on Steam (for live in-game execution).
3. **.NET SDK**: .NET 8.0 SDK (if building the C# mod from source).

> **Note on Testing**: You do **not** need Terraria or tModLoader installed to run the unit test suite or the fake bridge integration test.

---

## 1. Python Environment Setup

1. Open PowerShell or Command Prompt.
2. Clone the repository and navigate to the project directory:
   ```powershell
   git clone https://github.com/brkcnr/terragent.git
   cd terragent
   ```
3. Create and activate a Python virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -e .[dev]
   ```

---

## 2. Verify Code Quality and Test Suite

Run the full verification suite to ensure everything is operating cleanly:
```powershell
ruff check .
ruff format --check .
mypy agent tests
pytest -v
```

---

## 3. Building & Installing the tModLoader Bridge Mod (When Ready for Live Game)

1. Open the `bridge/` directory in a terminal:
   ```powershell
   cd bridge
   dotnet build -c Release
   ```
2. Copy the built `.dll` / mod files to your tModLoader mods folder:
   `%USERPROFILE%\Documents\My Games\Terraria\tModLoader\Mods`
3. Launch tModLoader, enable **TerrAgentBridge** in the Mod Manager, and enter a Classic world.

---

## 4. Running the Agent

Start the agent with the default configuration:
```powershell
python -m terragent.main --config configs/default.yaml
```

The agent will connect to `ws://127.0.0.1:8765`, perform the protocol version handshake, and begin receiving game state frames.
