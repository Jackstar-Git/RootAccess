import json
import os
import uuid
import time
from typing import List, Dict, Any, Optional
from functools import lru_cache

DATA_FILE: str = "data/contacts.json"

@lru_cache(maxsize=1)
def load_contacts() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []

def _save_and_refresh_cache(contacts: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=4, ensure_ascii=False)
    
    load_contacts.cache_clear()
    get_contact_by_id.cache_clear()

@lru_cache(maxsize=128)
def get_contact_by_id(contact_id: str) -> Optional[Dict[str, Any]]:
    contacts = load_contacts()
    return next((c for c in contacts if str(c.get("id")) == str(contact_id)), None)

def add_contact(contact_data: Dict[str, Any]) -> Dict[str, Any]:
    contacts = load_contacts()
    
    contact_data["id"] = uuid.uuid4().hex[:8]
    contact_data["time_created"] = int(time.time())
    contact_data["is_read"] = False
    
    contacts.append(contact_data)
    _save_and_refresh_cache(contacts)
    return contact_data

def delete_contact(contact_id: str) -> bool:
    contacts = load_contacts()
    new_list = [c for c in contacts if str(c.get("id")) != str(contact_id)]
    
    if len(new_list) < len(contacts):
        _save_and_refresh_cache(new_list)
        return True
    return False

def mark_contact_read(contact_id: str) -> bool:
    contacts = load_contacts()
    for c in contacts:
        if str(c.get("id")) == str(contact_id):
            c["is_read"] = True
            _save_and_refresh_cache(contacts)
            return True
    return False