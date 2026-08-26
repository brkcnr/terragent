# TerrAgent Bridge Protocol Specification (v1.0.0)

This document defines the WebSocket communication contract between **TerrAgent** (Python client) and **TerrAgentBridge** (tModLoader C# mod).

## 1. Connection & Handshake

- **Endpoint**: `ws://127.0.0.1:8765`
- **Encoding**: UTF-8 JSON
- **Protocol Version**: Current active protocol is `1.0.0`.

### Handshake Sequence
Upon connection, both parties must verify protocol compatibility before transmitting game frames or action commands.

1. **Client -> Server (Handshake Request)**:
```json
{
  "type": "handshake",
  "client_name": "TerrAgent-Python",
  "protocol_version": "1.0.0"
}
```

2. **Server -> Client (Handshake Response)**:
```json
{
  "type": "handshake_ack",
  "server_name": "TerrAgentBridge-tModLoader",
  "protocol_version": "1.0.0",
  "status": "ok",
  "message": "Connected successfully"
}
```

*Note: If the server or client detects a major/minor version mismatch, the connection is immediately terminated with a descriptive error message.*

---

## 2. Server -> Client: GameState Broadcast (~10 Hz)

The bridge pushes a JSON payload at 10 Hz containing the current snapshot of player state required for Milestone 1:

```json
{
  "type": "game_state",
  "protocol_version": "1.0.0",
  "timestamp": 1724678400.123,
  "player": {
    "hp": 100,
    "max_hp": 100,
    "x": 2500.5,
    "y": 1200.0,
    "selected_slot": 0,
    "inventory": [
      { "slot": 0, "item_id": 3507, "name": "Copper Shortsword", "stack": 1 },
      { "slot": 1, "item_id": 3509, "name": "Copper Pickaxe", "stack": 1 },
      { "slot": 2, "item_id": 3506, "name": "Copper Axe", "stack": 1 },
      { "slot": 3, "item_id": 0, "name": "", "stack": 0 },
      { "slot": 4, "item_id": 0, "name": "", "stack": 0 }
    ]
  }
}
```

### Field Definitions (M1 Scope):
- `type`: Must be `"game_state"`.
- `protocol_version`: String matching current protocol version.
- `timestamp`: Float Unix timestamp in seconds.
- `player.hp`: Current player health (integer).
- `player.max_hp`: Maximum player health (integer).
- `player.x`: World coordinate X in pixels (float).
- `player.y`: World coordinate Y in pixels (float).
- `player.selected_slot`: Active inventory hotbar slot index (0 to 4 in M1).
- `player.inventory`: Array of the first 5 inventory slots (`slot`, `item_id`, `name`, `stack`).

---

## 3. Client -> Server: Action Commands

Commands sent from the Python agent to the bridge mod.

### Move Command (`move_to`)
Requests movement toward target world coordinates:

```json
{
  "type": "action",
  "command_id": "cmd_01J6A8Z9B1234567890",
  "action": "move_to",
  "target_x": 2550.0,
  "target_y": 1200.0,
  "duration_ms": 500
}
```

### Action Result (Server -> Client)
```json
{
  "type": "action_result",
  "command_id": "cmd_01J6A8Z9B1234567890",
  "action": "move_to",
  "success": true,
  "execution_time_ms": 498.2,
  "failure_reason": null,
  "details": "Movement completed"
}
```

If execution fails:
```json
{
  "type": "action_result",
  "command_id": "cmd_01J6A8Z9B1234567890",
  "action": "move_to",
  "success": false,
  "execution_time_ms": 50.0,
  "failure_reason": "BLOCKED_BY_TERRAIN",
  "details": "Player cannot navigate past obstruction"
}
```
