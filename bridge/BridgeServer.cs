using System;
using System.IO;
using System.Net;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace TerrAgentBridge;

/// <summary>
/// WebSocket server managing localhost communication between Terraria and TerrAgent.
/// </summary>
public class BridgeServer : IDisposable
{
    public const string ProtocolVersion = "1.0.0";
    private readonly string _prefix;
    private HttpListener? _httpListener;
    private CancellationTokenSource? _cts;
    private Task? _listenTask;

    public bool IsRunning => _httpListener?.IsListening ?? false;

    public BridgeServer(string host = "127.0.0.1", int port = 8765)
    {
        _prefix = $"http://{host}:{port}/";
    }

    /// <summary>
    /// Starts the WebSocket listener server asynchronously.
    /// </summary>
    public void Start()
    {
        if (IsRunning) return;

        _cts = new CancellationTokenSource();
        _httpListener = new HttpListener();
        _httpListener.Prefixes.Add(_prefix);
        _httpListener.Start();

        Console.WriteLine($"[TerrAgentBridge] Server started on {_prefix}");
        _listenTask = Task.Run(() => AcceptClientsAsync(_cts.Token));
    }

    private async Task AcceptClientsAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested && _httpListener != null && _httpListener.IsListening)
        {
            try
            {
                var context = await _httpListener.GetContextAsync();
                if (context.Request.IsWebSocketRequest)
                {
                    _ = ProcessWebSocketRequestAsync(context, ct);
                }
                else
                {
                    context.Response.StatusCode = 400;
                    context.Response.Close();
                }
            }
            catch (HttpListenerException) when (ct.IsCancellationRequested)
            {
                break;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[TerrAgentBridge] Error accepting connection: {ex.Message}");
            }
        }
    }

    private async Task ProcessWebSocketRequestAsync(HttpListenerContext context, CancellationToken ct)
    {
        WebSocketContext wsContext;
        try
        {
            wsContext = await context.AcceptWebSocketAsync(subProtocol: null);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[TerrAgentBridge] WebSocket handshake failed: {ex.Message}");
            context.Response.StatusCode = 500;
            context.Response.Close();
            return;
        }

        var webSocket = wsContext.WebSocket;
        Console.WriteLine("[TerrAgentBridge] Client connected. Initiating protocol handshake...");

        using var clientCts = CancellationTokenSource.CreateLinkedTokenSource(ct);

        try
        {
            // 1. Perform Protocol Version Handshake
            bool handshakePassed = await HandleHandshakeAsync(webSocket, clientCts.Token);
            if (!handshakePassed)
            {
                Console.WriteLine("[TerrAgentBridge] Handshake failed or version mismatch. Closing connection.");
                await webSocket.CloseAsync(WebSocketCloseStatus.ProtocolError, "Version mismatch", ct);
                return;
            }

            Console.WriteLine("[TerrAgentBridge] Protocol handshake verified. Starting 10 Hz state stream and command receiver.");

            // 2. Run state broadcast and incoming command listener concurrently
            var broadcastTask = BroadcastGameStateLoopAsync(webSocket, clientCts.Token);
            var receiveTask = ReceiveCommandsLoopAsync(webSocket, clientCts.Token);

            await Task.WhenAny(broadcastTask, receiveTask);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[TerrAgentBridge] Client session ended: {ex.Message}");
        }
        finally
        {
            clientCts.Cancel();
            if (webSocket.State == WebSocketState.Open || webSocket.State == WebSocketState.CloseReceived)
            {
                try
                {
                    await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
                }
                catch { }
            }
            webSocket.Dispose();
            Console.WriteLine("[TerrAgentBridge] WebSocket client disconnected.");
        }
    }

    private async Task<bool> HandleHandshakeAsync(WebSocket ws, CancellationToken ct)
    {
        byte[] buffer = new byte[4096];
        var result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), ct);
        if (result.MessageType != WebSocketMessageType.Text)
        {
            return false;
        }

        string json = Encoding.UTF8.GetString(buffer, 0, result.Count);
        HandshakeRequest? req;
        try
        {
            req = JsonSerializer.Deserialize<HandshakeRequest>(json);
        }
        catch
        {
            return false;
        }

        if (req == null || req.Type != "handshake")
        {
            return false;
        }

        bool match = req.ProtocolVersion == ProtocolVersion;
        var response = new HandshakeResponse
        {
            Type = "handshake_ack",
            ServerName = "TerrAgentBridge-tModLoader",
            ProtocolVersion = ProtocolVersion,
            Status = match ? "ok" : "error",
            Message = match ? "Connected successfully" : $"Protocol mismatch. Server={ProtocolVersion}, Client={req.ProtocolVersion}"
        };

        byte[] respBytes = JsonSerializer.SerializeToUtf8Bytes(response);
        await ws.SendAsync(new ArraySegment<byte>(respBytes), WebSocketMessageType.Text, true, ct);

        return match;
    }

    private async Task BroadcastGameStateLoopAsync(WebSocket ws, CancellationToken ct)
    {
        while (!ct.IsCancellationRequested && ws.State == WebSocketState.Open)
        {
            // Milestone 1: Push sample/mocked game state snapshot for local development and testing
            var state = new GameStateModel
            {
                Type = "game_state",
                ProtocolVersion = ProtocolVersion,
                Timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0,
                Player = new PlayerStateModel
                {
                    Hp = 100,
                    MaxHp = 100,
                    X = 2500.0f,
                    Y = 1200.0f,
                    SelectedSlot = 0,
                    Inventory = new()
                    {
                        new InventorySlotModel { Slot = 0, ItemId = 3507, Name = "Copper Shortsword", Stack = 1 },
                        new InventorySlotModel { Slot = 1, ItemId = 3509, Name = "Copper Pickaxe", Stack = 1 },
                        new InventorySlotModel { Slot = 2, ItemId = 3506, Name = "Copper Axe", Stack = 1 },
                        new InventorySlotModel { Slot = 3, ItemId = 0, Name = "", Stack = 0 },
                        new InventorySlotModel { Slot = 4, ItemId = 0, Name = "", Stack = 0 }
                    }
                }
            };

            byte[] jsonBytes = JsonSerializer.SerializeToUtf8Bytes(state);
            await ws.SendAsync(new ArraySegment<byte>(jsonBytes), WebSocketMessageType.Text, true, ct);

            // 10 Hz stream interval (100 ms)
            await Task.Delay(100, ct);
        }
    }

    private async Task ReceiveCommandsLoopAsync(WebSocket ws, CancellationToken ct)
    {
        byte[] buffer = new byte[8192];
        while (!ct.IsCancellationRequested && ws.State == WebSocketState.Open)
        {
            var result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), ct);
            if (result.MessageType == WebSocketMessageType.Close)
            {
                break;
            }

            if (result.MessageType == WebSocketMessageType.Text)
            {
                string json = Encoding.UTF8.GetString(buffer, 0, result.Count);
                try
                {
                    using var doc = JsonDocument.Parse(json);
                    var root = doc.RootElement;
                    if (root.TryGetProperty("action", out var actionProp) && actionProp.GetString() == "move_to")
                    {
                        var cmd = JsonSerializer.Deserialize<MoveCommandModel>(json);
                        if (cmd != null)
                        {
                            Console.WriteLine($"[TerrAgentBridge] MoveTo received: Target=({cmd.TargetX}, {cmd.TargetY}), Duration={cmd.DurationMs}ms");
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[TerrAgentBridge] Malformed command received: {ex.Message}");
                }
            }
        }
    }

    /// <summary>
    /// Stops the server and releases all network resources.
    /// </summary>
    public void Stop()
    {
        _cts?.Cancel();
        if (_httpListener != null && _httpListener.IsListening)
        {
            try
            {
                _httpListener.Stop();
                _httpListener.Close();
            }
            catch { }
        }
    }

    public void Dispose()
    {
        Stop();
        _cts?.Dispose();
    }
}
