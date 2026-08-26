# TerrAgentBridge (tModLoader Mod)

TerrAgentBridge is the native C# mod running inside Terraria (via tModLoader) that exposes a localhost WebSocket server (`ws://127.0.0.1:8765`).

## Building the Mod

1. Ensure the **.NET 8.0 SDK** is installed on your machine.
2. Open terminal in the `bridge/` directory:
   ```powershell
   dotnet build -c Release
   ```
3. Copy the output binary to your local tModLoader mods folder:
   - Windows: `%USERPROFILE%\Documents\My Games\Terraria\tModLoader\Mods`
4. Launch tModLoader and enable **TerrAgentBridge** in the Mod Menu.

## Protocol Handshake

Upon connection, the mod expects a JSON handshake with `protocol_version: "1.0.0"`. See `docs/BRIDGE_PROTOCOL.md` for full protocol documentation.
