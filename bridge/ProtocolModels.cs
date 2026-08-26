using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace TerrAgentBridge;

/// <summary>
/// Handshake request payload received from client.
/// </summary>
public class HandshakeRequest
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "handshake";

    [JsonPropertyName("client_name")]
    public string ClientName { get; set; } = string.Empty;

    [JsonPropertyName("protocol_version")]
    public string ProtocolVersion { get; set; } = string.Empty;
}

/// <summary>
/// Handshake response payload returned to client.
/// </summary>
public class HandshakeResponse
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "handshake_ack";

    [JsonPropertyName("server_name")]
    public string ServerName { get; set; } = "TerrAgentBridge-tModLoader";

    [JsonPropertyName("protocol_version")]
    public string ProtocolVersion { get; set; } = "1.0.0";

    [JsonPropertyName("status")]
    public string Status { get; set; } = "ok";

    [JsonPropertyName("message")]
    public string Message { get; set; } = "Connected successfully";
}

/// <summary>
/// Represents a single inventory slot.
/// </summary>
public class InventorySlotModel
{
    [JsonPropertyName("slot")]
    public int Slot { get; set; }

    [JsonPropertyName("item_id")]
    public int ItemId { get; set; }

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("stack")]
    public int Stack { get; set; }
}

/// <summary>
/// Represents a Town NPC status in the roster.
/// </summary>
public class TownNPCModel
{
    [JsonPropertyName("npc_type")]
    public int NpcType { get; set; }

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("is_housed")]
    public bool IsHoused { get; set; }

    [JsonPropertyName("room_id")]
    public int? RoomId { get; set; }
}

/// <summary>
/// Player state model.
/// </summary>
public class PlayerStateModel
{
    [JsonPropertyName("hp")]
    public int Hp { get; set; }

    [JsonPropertyName("max_hp")]
    public int MaxHp { get; set; }

    [JsonPropertyName("x")]
    public float X { get; set; }

    [JsonPropertyName("y")]
    public float Y { get; set; }

    [JsonPropertyName("selected_slot")]
    public int SelectedSlot { get; set; }

    [JsonPropertyName("inventory")]
    public List<InventorySlotModel> Inventory { get; set; } = new();
}

/// <summary>
/// Periodic GameState snapshot model pushed at ~10 Hz.
/// </summary>
public class GameStateModel
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "game_state";

    [JsonPropertyName("protocol_version")]
    public string ProtocolVersion { get; set; } = "1.0.0";

    [JsonPropertyName("timestamp")]
    public double Timestamp { get; set; }

    [JsonPropertyName("player")]
    public PlayerStateModel Player { get; set; } = new();

    [JsonPropertyName("town_npcs")]
    public List<TownNPCModel> TownNpcs { get; set; } = new();

    [JsonPropertyName("spawn_tile_x")]
    public int? SpawnTileX { get; set; }

    [JsonPropertyName("spawn_tile_y")]
    public int? SpawnTileY { get; set; }
}

/// <summary>
/// Move action command received from client.
/// </summary>
public class MoveCommandModel
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "action";

    [JsonPropertyName("command_id")]
    public string CommandId { get; set; } = string.Empty;

    [JsonPropertyName("action")]
    public string Action { get; set; } = "move_to";

    [JsonPropertyName("target_x")]
    public float TargetX { get; set; }

    [JsonPropertyName("target_y")]
    public float TargetY { get; set; }

    [JsonPropertyName("duration_ms")]
    public int DurationMs { get; set; }
}

/// <summary>
/// Housing query request payload.
/// </summary>
public class QueryHousingRequestModel
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "query";

    [JsonPropertyName("query_id")]
    public string QueryId { get; set; } = string.Empty;

    [JsonPropertyName("query")]
    public string Query { get; set; } = "query_housing";

    [JsonPropertyName("tile_x")]
    public int TileX { get; set; }

    [JsonPropertyName("tile_y")]
    public int TileY { get; set; }
}

/// <summary>
/// Housing query response payload.
/// </summary>
public class QueryHousingResponseModel
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "query_response";

    [JsonPropertyName("query_id")]
    public string QueryId { get; set; } = string.Empty;

    [JsonPropertyName("query")]
    public string Query { get; set; } = "query_housing";

    [JsonPropertyName("success")]
    public bool Success { get; set; }

    [JsonPropertyName("is_valid")]
    public bool IsValid { get; set; }

    [JsonPropertyName("failure_reason")]
    public string? FailureReason { get; set; }

    [JsonPropertyName("assigned_npc")]
    public string? AssignedNpc { get; set; }

    [JsonPropertyName("details")]
    public string Details { get; set; } = string.Empty;
}

/// <summary>
/// Item slot within a chest.
/// </summary>
public class ChestItemSlotModel
{
    [JsonPropertyName("slot")]
    public int Slot { get; set; }

    [JsonPropertyName("item_id")]
    public int ItemId { get; set; }

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("stack")]
    public int Stack { get; set; }
}

/// <summary>
/// Chest query request payload.
/// </summary>
public class QueryChestRequestModel
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "query";

    [JsonPropertyName("query_id")]
    public string QueryId { get; set; } = string.Empty;

    [JsonPropertyName("query")]
    public string Query { get; set; } = "query_chest";

    [JsonPropertyName("chest_x")]
    public int ChestX { get; set; }

    [JsonPropertyName("chest_y")]
    public int ChestY { get; set; }
}

/// <summary>
/// Chest query response payload.
/// </summary>
public class QueryChestResponseModel
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "query_response";

    [JsonPropertyName("query_id")]
    public string QueryId { get; set; } = string.Empty;

    [JsonPropertyName("query")]
    public string Query { get; set; } = "query_chest";

    [JsonPropertyName("success")]
    public bool Success { get; set; }

    [JsonPropertyName("chest_x")]
    public int ChestX { get; set; }

    [JsonPropertyName("chest_y")]
    public int ChestY { get; set; }

    [JsonPropertyName("items")]
    public List<ChestItemSlotModel> Items { get; set; } = new();

    [JsonPropertyName("details")]
    public string Details { get; set; } = string.Empty;
}

/// <summary>
/// Action result model sent back after executing a command.
/// </summary>
public class ActionResultModel
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "action_result";

    [JsonPropertyName("command_id")]
    public string CommandId { get; set; } = string.Empty;

    [JsonPropertyName("action")]
    public string Action { get; set; } = string.Empty;

    [JsonPropertyName("success")]
    public bool Success { get; set; }

    [JsonPropertyName("execution_time_ms")]
    public double ExecutionTimeMs { get; set; }

    [JsonPropertyName("failure_reason")]
    public string? FailureReason { get; set; }

    [JsonPropertyName("details")]
    public string Details { get; set; } = string.Empty;
}
