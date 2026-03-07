from functools import lru_cache
import json
import os
from typing import Any, Optional, Dict, Final

SETTINGS_FILE: Final[str] = "data/settings.json"

@lru_cache(maxsize=1)
def _load_settings() -> Optional[Dict[str, Any]]:
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return None

@lru_cache(maxsize=128)
def get_settings(key: str) -> Any:
    data: Optional[Dict[str, Any]] = _load_settings()

    if data is None:
        return None

    if key in data:
        return data[key]

    if "-" not in key:
        return None

    val: Any = data
    for part in key.split("-"):
        if isinstance(val, dict) and part in val:
            val = val[part]
        else:
            return None
            
    return val