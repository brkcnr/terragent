"""Configuration loading and validation for TerrAgent.

This module loads and validates YAML configuration files into strongly typed
Pydantic settings models.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class BridgeConfig(BaseModel):
    """Configuration settings for the WebSocket bridge connection."""

    host: str = Field(default="127.0.0.1", description="Bridge server hostname or IP")
    port: int = Field(default=8765, ge=1024, le=65535, description="Bridge server port")
    protocol_version: str = Field(default="1.0.0", description="Expected bridge protocol version")
    reconnect_initial_delay_seconds: float = Field(
        default=1.0, ge=0.1, description="Initial reconnect delay"
    )
    reconnect_max_delay_seconds: float = Field(
        default=10.0, ge=1.0, description="Maximum reconnect delay"
    )
    reconnect_backoff_factor: float = Field(
        default=2.0, ge=1.0, description="Exponential backoff multiplier"
    )
    max_reconnect_attempts: int = Field(
        default=10, ge=1, description="Maximum reconnection retry attempts"
    )
    timeout_seconds: float = Field(
        default=5.0, ge=0.5, description="Socket send/receive timeout in seconds"
    )


class ReflexConfig(BaseModel):
    """Configuration settings for the Reflex rule engine."""

    tick_hz: float = Field(default=10.0, ge=1.0, le=60.0, description="Reflex tick loop frequency")
    low_hp_threshold: int = Field(
        default=100, ge=1, description="HP threshold triggering retreat behavior"
    )
    safe_retreat_offset_x: float = Field(
        default=-50.0, description="World X pixel offset applied when retreating"
    )


class SafetyConfig(BaseModel):
    """Configuration settings for runtime safety and hotkeys."""

    max_session_runtime_seconds: int = Field(
        default=3600, ge=60, description="Maximum session duration before stopping"
    )
    emergency_killswitch_key: str = Field(
        default="F9", description="Keyboard key for emergency halt"
    )
    pause_resume_key: str = Field(default="F10", description="Keyboard key for pause/resume")


class TerrAgentConfig(BaseModel):
    """Root configuration model combining all subsystem settings."""

    bridge: BridgeConfig = Field(default_factory=BridgeConfig)
    reflex: ReflexConfig = Field(default_factory=ReflexConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)


def load_config(config_path: str | Path | None = None) -> TerrAgentConfig:
    """Load and validate configuration from a YAML file.

    Args:
        config_path: Optional path to a YAML configuration file. If None,
            returns default configuration settings.

    Returns:
        TerrAgentConfig: Validated configuration instance.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        ValueError: If YAML parsing or validation fails.
    """
    if config_path is None:
        return TerrAgentConfig()

    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path.resolve()}")

    with open(path, encoding="utf-8") as f:
        data: Any = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid configuration format in {path}: expected dictionary root")

    return TerrAgentConfig(**data)
