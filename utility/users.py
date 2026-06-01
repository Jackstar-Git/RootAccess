import json
import os
import time
from typing import List, Union, Optional, TypedDict, Any, Dict, Literal
from functools import lru_cache
import uuid

class User(TypedDict):
    id: str
    username: str
    password_hash: str
    profile_picture_url: Optional[str]
    hierarchy_level: int
    permissions: int
    time_created: int
    last_modified: int
    status: Literal["active", "banned", "disabled", "test"]
    notes: str

DATA_FILE: str = "data/users.json"

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def _build_default_user_payload(user: Dict[str, Any] | User) -> User:
    return {
        "id": str(user["id"]) if user.get("id") is not None else "",
        "username": user.get("username", ""),
        "password_hash": user.get("password_hash", ""),
        "profile_picture_url": user.get("profile_picture_url", None),
        "hierarchy_level": user.get("hierarchy_level", 1),
        "permissions": user.get("permissions", 0),
        "time_created": user.get("time_created", 0),
        "last_modified": user.get("last_modified", 0),
        "status": user.get("status", "active"),
        "notes": user.get("notes", ""),      
    }

def _save_and_refresh_cache(users: List[User]) -> None:
    normalized_users = [_build_default_user_payload(user) for user in users]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(normalized_users, f, indent=4, ensure_ascii=False)

    load_users.cache_clear()
    get_user_by_id.cache_clear()
    get_user_by_username.cache_clear()

# ==========================================
# 2. CORE CRUD OPERATIONS
# ==========================================

@lru_cache(maxsize=1)
def load_users() -> List[User]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [_build_default_user_payload(item) for item in data]
            return []
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []

@lru_cache(maxsize=128)
def get_user_by_id(user_id: Union[int, str]) -> Optional[User]:
    users: List[User] = load_users()
    str_id: str = str(user_id)
    return next((user for user in users if str(user.get("id")) == str_id), None)

@lru_cache(maxsize=128)
def get_user_by_username(username: str) -> Optional[User]:
    users: List[User] = load_users()
    return next((user for user in users if user.get("username") == username), None)

def add_user(new_user: Dict[str, Any]) -> User:
    users: List[User] = load_users()
    now = int(time.time())

    if not new_user.get("id"):
        existing_ids = {str(u.get("id")) for u in users}
        while (candidate := uuid.uuid4().hex[:12]) in existing_ids:
            pass
        new_user["id"] = candidate
    else:
        new_user["id"] = str(new_user["id"])

    full_user_payload: Dict[str, Any] = {
        "id": new_user["id"],
        "username": new_user.get("username", ""),
        "password_hash": new_user.get("password_hash", ""),
        "profile_picture_url": new_user.get("profile_picture_url", None),
        "hierarchy_level": new_user.get("hierarchy_level", 1),
        "permissions": new_user.get("permissions", 0),
        "time_created": new_user.get("time_created", now),
        "last_modified": now,
        "status": new_user.get("status", "active"),
        "notes": new_user.get("notes", ""),
    }

    final_user = _build_default_user_payload(full_user_payload)
    users.append(final_user)
    _save_and_refresh_cache(users)
    return final_user

def update_user(user_id: Union[int, str], updated_data: Dict[str, Any]) -> bool:
    users: List[User] = load_users()
    str_id: str = str(user_id)

    for i, user in enumerate(users):
        if str(user.get("id")) == str_id:
            updated_data.pop("id", None)
            updated_data.pop("time_created", None)
            
            merged_payload = dict(user)
            merged_payload.update(updated_data)

            if merged_payload.get("status") == "disabled":
                merged_payload["username"] = "Deleted User"
                merged_payload["profile_picture_url"] = None
                merged_payload["permissions"] = 0
                merged_payload["hierarchy_level"] = 10
                merged_payload["time_created"] = 0

            merged_payload["last_modified"] = int(time.time())

            users[i] = _build_default_user_payload(merged_payload)
            _save_and_refresh_cache(users)
            return True
    return False

def delete_user(user_id: Union[int, str]) -> bool:
    users: List[User] = load_users()
    str_id: str = str(user_id)
    new_list = [u for u in users if str(u.get("id")) != str_id]
    if len(new_list) < len(users):
        _save_and_refresh_cache(new_list)
        return True
    return False

# ==========================================
# 3. OTHER OPERATIONS (SEARCH, FILTER, UTILS)
# ==========================================

def search_users(search_query: str) -> List[User]:
    users: List[User] = load_users()
    if not search_query or not search_query.strip():
        return users
    query: str = search_query.lower()
    return [u for u in users if query in u.get("username", "").lower()]

def query_users(
    limit: Optional[int] = 10,
    exclude_id: Optional[Any] = None,
    match_mode: Literal["AND", "OR"] = "AND",
    **criteria: Any
) -> List[User]:
    user_list: List[User] = load_users()
    filtered_results: List[User] = []

    for user in user_list:
        if exclude_id is not None and user.get("id") == exclude_id:
            continue
        if not criteria:
            filtered_results.append(user)
            continue

        matches = []
        for key, target in criteria.items():
            current = user.get(key)
            item_match = False
            if isinstance(current, list):
                if isinstance(target, list):
                    item_match = any(item in current for item in target)
                else:
                    item_match = target in current
            else:
                item_match = (current == target)
            matches.append(item_match)

        is_match = all(matches) if match_mode == "AND" else any(matches)
        if is_match:
            filtered_results.append(user)

    return filtered_results[:limit]

def sort_users(user_list: List[User], sort_by: str) -> List[User]:
    if sort_by == "name-asc":
        return sorted(user_list, key=lambda x: x.get("username", "").lower())
    elif sort_by == "name-desc":
        return sorted(user_list, key=lambda x: x.get("username", "").lower(), reverse=True)
    elif sort_by == "hierarchy-asc":
        return sorted(user_list, key=lambda x: x.get("hierarchy_level", 0))
    elif sort_by == "hierarchy-desc":
        return sorted(user_list, key=lambda x: x.get("hierarchy_level", 0), reverse=True)
    elif sort_by == "created-asc":
        return sorted(user_list, key=lambda x: x.get("time_created", 0))
    elif sort_by == "created-desc":
        return sorted(user_list, key=lambda x: x.get("time_created", 0), reverse=True)
    else:  # Default: oldest
        return sorted(user_list, key=lambda x: x.get("time_created", 0))

def is_active(user_id: Union[int, str]) -> bool:
    user = get_user_by_id(user_id)
    return user is not None and user.get("status") not in ["disabled", "banned"]