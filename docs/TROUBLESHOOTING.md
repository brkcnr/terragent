# TerrAgent Troubleshooting Guide

Common issues and remediation steps.

## 1. WebSocket Connection Refused (`ConnectionRefusedError` / `127.0.0.1:8765`)
- **Symptom**: `TerrAgent` logs `Failed to connect to ws://127.0.0.1:8765. Retrying...`
- **Causes**:
  - tModLoader is not running or the world is not loaded.
  - The `TerrAgentBridge` mod is disabled in tModLoader's Mod Menu.
  - A firewall is blocking localhost port 8765.
- **Solution**:
  - Check the in-game tModLoader log to ensure `TerrAgentBridge` started on port 8765.
  - Verify port 8765 is not already in use by running `netstat -ano | findstr 8765` in PowerShell.

---

## 2. Protocol Version Mismatch (`ProtocolVersionMismatchError`)
- **Symptom**: `ProtocolVersionMismatchError: Protocol version mismatch: server=1.1.0, client=1.0.0`
- **Causes**:
  - The Python agent was updated without rebuilding and reinstalling the C# bridge mod (or vice versa).
- **Solution**:
  - Ensure both `TerrAgentBridge` and `TerrAgent` are on matching SemVer protocol versions.
  - Rebuild the C# mod and re-run the Python client.

---

## 3. Test Failures / Import Errors
- **Symptom**: `ModuleNotFoundError: No module named 'terragent'`
- **Solution**:
  - Install the package in editable mode: `pip install -e .` or ensure `PYTHONPATH` includes the `agent` directory.
