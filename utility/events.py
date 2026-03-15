import json
import os
import uuid
from typing import List, Dict, Any, Optional, Union
from functools import lru_cache

DATA_FILE: str = "data/events.json"

@lru_cache(maxsize=1)
def load_events() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []

def _save_and_refresh_cache(events: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=4, ensure_ascii=False)
    
    load_events.cache_clear()
    get_event_by_id.cache_clear()

@lru_cache(maxsize=128)
def get_event_by_id(event_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    events = load_events()
    str_id = str(event_id)
    return next((e for e in events if str(e.get("id")) == str_id), None)

def add_event(new_event: Dict[str, Any]) -> Dict[str, Any]:
    events = load_events()
    
    if not new_event.get("id"):
        existing_ids = {str(e.get("id")) for e in events}
        while True:
            candidate = uuid.uuid4().hex[:8]
            if candidate not in existing_ids:
                new_event["id"] = candidate
                break
    else:
        new_event["id"] = str(new_event["id"])

    events.append(new_event)
    _save_and_refresh_cache(events)
    return new_event

def update_event(event_id: Union[int, str], updated_data: Dict[str, Any]) -> bool:
    events = load_events()
    str_id = str(event_id)
    
    for i, event in enumerate(events):
        if str(event.get("id")) == str_id:
            updated_data.pop("id", None)  # Prevent ID tampering
            events[i].update(updated_data)
            _save_and_refresh_cache(events)
            return True
    return False

def delete_event(event_id: Union[int, str]) -> bool:
    events = load_events()
    str_id = str(event_id)
    
    new_list = [e for e in events if str(e.get("id")) != str_id]
    if len(new_list) < len(events):
        _save_and_refresh_cache(new_list)
        return True
    return False

def get_events() -> List[Dict[str, Any]]:
    return load_events()