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

### Place Tile Command (`place_tile`)
```json
{
  "type": "action",
  "command_id": "cmd_01J6B999",
  "action": "place_tile",
  "tile_x": 120,
  "tile_y": 80,
  "item_id": 30
}
```

### Attack Command (`attack`)
```json
{
  "type": "action",
  "command_id": "cmd_01J6ATK1",
  "action": "attack",
  "aim_x": 2650.0,
  "aim_y": 1150.0,
  "use_item_slot": 0,
  "continuous": true
}
```

### Use Potion Command (`use_potion`)
```json
{
  "type": "action",
  "command_id": "cmd_01J6POT1",
  "action": "use_potion",
  "potion_type": "healing"
}
```

### Set Spawn Command (`set_spawn`)
```json
{
  "type": "action",
  "command_id": "cmd_01J6C888",
  "action": "set_spawn",
  "tile_x": 125,
  "tile_y": 82
}
```

### Deposit Chest Command (`deposit_chest`)
```json
{
  "type": "action",
  "command_id": "cmd_01J6D777",
  "action": "deposit_chest",
  "chest_x": 130,
  "chest_y": 85,
  "inventory_slot": 10,
  "target_chest_slot": null
}
```

### Withdraw Chest Command (`withdraw_chest`)
```json
{
  "type": "action",
  "command_id": "cmd_01J6E666",
  "action": "withdraw_chest",
  "chest_x": 130,
  "chest_y": 85,
  "chest_slot": 2,
  "target_inventory_slot": null
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

---

## 4. Query Endpoints (Milestone 2)

Request-response queries over WebSocket for deterministic state verification.

### Housing Validity Query (`query_housing`)
- **Request**:
```json
{
  "type": "query",
  "query_id": "qry_01J6F555",
  "query": "query_housing",
  "tile_x": 125,
  "tile_y": 80
}
```
- **Response**:
```json
{
  "type": "query_response",
  "query_id": "qry_01J6F555",
  "query": "query_housing",
  "success": true,
  "is_valid": true,
  "failure_reason": null,
  "assigned_npc": "Merchant",
  "details": "Valid housing room suitable for NPCs"
}
```

### Chest Contents Query (`query_chest`)
- **Request**:
```json
{
  "type": "query",
  "query_id": "qry_01J6G444",
  "query": "query_chest",
  "chest_x": 130,
  "chest_y": 85
}
```
- **Response**:
```json
{
  "type": "query_response",
  "query_id": "qry_01J6G444",
  "query": "query_chest",
  "success": true,
  "chest_x": 130,
  "chest_y": 85,
  "items": [
    { "slot": 0, "item_id": 12, "name": "Iron Ore", "stack": 99 },
    { "slot": 1, "item_id": 19, "name": "Gold Bar", "stack": 15 }
  ],
  "details": "Chest read successfully"
}
```
