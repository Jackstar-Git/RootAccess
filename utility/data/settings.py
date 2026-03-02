import json
import os
from typing import Any, Optional

SETTINGS_FILE = "data/settings.json"


def _load_settings() -> Optional[dict]:
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_settings(key: str) -> Any:
    data = _load_settings()

    if data is None:
        return None

    # try direct lookup first
    if key in data:
        return data[key]

    # if key has no hyphen there is nothing more we can do
    if "-" not in key:
        return None

    val = data
    for part in key.split("-"):
        if isinstance(val, dict) and part in val:
            val = val[part]
        else:
            return None
    return val
