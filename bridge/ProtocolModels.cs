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
/// Represents a single inventory slot in M1.
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
/// Player state model for Milestone 1.
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
