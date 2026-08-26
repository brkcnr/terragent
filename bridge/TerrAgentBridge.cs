using System;

namespace TerrAgentBridge;

/// <summary>
/// Main mod lifecycle manager for TerrAgentBridge.
/// In a tModLoader environment, this integrates with Mod/ModSystem hooks.
/// </summary>
public class TerrAgentBridgeMod
{
    private static BridgeServer? _server;

    /// <summary>
    /// Lifecycle load hook invoked when mod is initialized.
    /// </summary>
    public static void Load()
    {
        Console.WriteLine("[TerrAgentBridge] Loading TerrAgentBridge mod v1.0.0...");
        _server = new BridgeServer("127.0.0.1", 8765);
        _server.Start();
    }

    /// <summary>
    /// Lifecycle unload hook invoked when mod is unloaded.
    /// </summary>
    public static void Unload()
    {
        Console.WriteLine("[TerrAgentBridge] Unloading TerrAgentBridge mod...");
        _server?.Stop();
        _server?.Dispose();
        _server = null;
    }
}
