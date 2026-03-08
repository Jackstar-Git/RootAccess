from functools import lru_cache
import json
import os
from typing import Any, Optional, Dict, Final

SETTINGS_FILE: Final[str] = "data/settings.json"

def _ensure_data_dir() -> None:
    """Ensure the data directory exists"""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)

@lru_cache(maxsize=1)
def _load_settings() -> Dict[str, Any]:
    """Load settings from file, return empty dict if file doesn't exist"""
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return {}

def _save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to file"""
    _ensure_data_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

@lru_cache(maxsize=1)
def _load_settings_cached() -> Dict[str, Any]:
    """Cached version of settings loading"""
    return _load_settings()

def get_settings(key: str = None) -> Any:
    """
    Get settings value by key.
    If key is None, returns entire settings dict.
    Supports nested keys with '-' separator.
    """
    data: Dict[str, Any] = _load_settings_cached()

    if key is None:
        return data

    if key not in data and "-" in key:
        # Handle nested keys
        val: Any = data
        for part in key.split("-"):
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return None
        return val

    return data.get(key)

def update_settings(new_settings: Dict[str, Any]) -> None:
    """
    Update settings with new values.
    Can handle both top-level and nested keys.
    Automatically clears cache.
    """
    current_settings = _load_settings()
    updated = _deep_update(current_settings, new_settings)
    _save_settings(updated)
    _load_settings_cached.cache_clear()
    _load_settings.cache_clear()

def _deep_update(original: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep update dictionary with new values.
    Preserves original structure while updating values.
    """
    for key, value in new.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            original[key] = _deep_update(original[key], value)
        else:
            original[key] = value
    return original

def set_setting(key: str, value: Any) -> None:
    """
    Set a single setting value.
    Can handle nested keys with '-' separator.
    """
    current = _load_settings()
    keys = key.split("-")
    target = current

    for k in keys[:-1]:
        if k not in target or not isinstance(target[k], dict):
            target[k] = {}
        target = target[k]

    target[keys[-1]] = value
    _save_settings(current)
    _load_settings_cached.cache_clear()
    _load_settings.cache_clear()
