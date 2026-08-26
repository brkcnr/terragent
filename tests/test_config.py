"""Unit tests for configuration loader."""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError
from terragent.config import BridgeConfig, ReflexConfig, TerrAgentConfig, load_config


def test_default_config_instantiation() -> None:
    """Test default configuration values."""
    config = load_config(None)
    assert isinstance(config, TerrAgentConfig)
    assert config.bridge.host == "127.0.0.1"
    assert config.bridge.port == 8765
    assert config.bridge.protocol_version == "1.0.0"
    assert config.reflex.tick_hz == 10.0
    assert config.reflex.low_hp_threshold == 100


def test_load_config_from_file() -> None:
    """Test loading configuration from default.yaml."""
    config_file = Path("configs/default.yaml")
    assert config_file.exists()

    config = load_config(config_file)
    assert config.bridge.port == 8765
    assert config.reflex.safe_retreat_offset_x == -50.0


def test_load_nonexistent_config() -> None:
    """Test that missing config file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_path/config.yaml")


def test_invalid_config_values() -> None:
    """Test that invalid config values fail Pydantic validation."""
    with pytest.raises(ValidationError):
        BridgeConfig(port=999999)  # Port out of bounds

    with pytest.raises(ValidationError):
        ReflexConfig(tick_hz=0.0)  # Invalid frequency


def test_malformed_yaml_content() -> None:
    """Test loading non-dictionary YAML file."""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
        f.write("- item1\n- item2\n")
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="expected dictionary root"):
            load_config(temp_path)
    finally:
        Path(temp_path).unlink(missing_ok=True)
