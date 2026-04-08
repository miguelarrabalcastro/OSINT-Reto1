"""
PulseTrack — Configuration Loader
Merges defaults.yaml + local.yaml + environment variable overrides.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

DEFAULTS_PATH = Path(__file__).parent.parent / "config" / "defaults.yaml"
ENV_PREFIX = "PULSETRACK_"


def load_config(local_path: str = "config/local.yaml") -> Dict[str, Any]:
    """
    Load and merge configuration. Priority: env vars > local.yaml > defaults.yaml
    """
    config = _load_yaml(DEFAULTS_PATH)

    local = Path(local_path)
    if local.exists():
        local_config = _load_yaml(local)
        config = _deep_merge(config, local_config)
        logger.debug(f"Merged local config: {local}")
    else:
        logger.debug(f"No local config at {local_path} — using defaults only")

    config = _apply_env_overrides(config)
    _validate(config)
    return config


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _apply_env_overrides(config: dict) -> dict:
    mapping = {
        f"{ENV_PREFIX}LOG_LEVEL": ("pulsetrack", "log_level"),
        f"{ENV_PREFIX}SCAN_INTERVAL": ("pulsetrack", "scan_interval"),
        f"{ENV_PREFIX}MAX_WORKERS": ("pulsetrack", "max_workers"),
    }
    for env_key, path in mapping.items():
        value = os.environ.get(env_key)
        if value is not None:
            section, key = path
            if section not in config:
                config[section] = {}
            config[section][key] = type(config[section].get(key, value))(value)
            logger.debug(f"Env override: {env_key} → {section}.{key} = {value!r}")
    return config


def _validate(config: dict):
    pt = config.get("pulsetrack", {})
    version = pt.get("version")
    if not version:
        raise ValueError("Config missing required field: pulsetrack.version")
    supported = ["2.3", "2.4"]
    if version not in supported:
        raise ValueError(f"Unsupported config version {version!r}. Supported: {supported}")
