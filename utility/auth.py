import json
import os
from enum import IntFlag
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast
from flask import abort, redirect, url_for, request, session
from utility.logging_utility import logger
from werkzeug.security import check_password_hash
import json
import os
import random
import string

F = TypeVar("F", bound=Callable[..., Any])

# ========== PERMISSION DEFINITIONS ==========
class Permission(IntFlag):
    # Blogs
    BLOGS_READ = 1 << 0
    BLOGS_CREATE = 1 << 1
    BLOGS_UPDATE_OWN = 1 << 2
    BLOGS_UPDATE = 1 << 3
    BLOGS_DELETE_OWN = 1 << 4
    BLOGS_DELETE = 1 << 5

    # Projects
    PROJECTS_READ = 1 << 6
    PROJECTS_CREATE = 1 << 7
    PROJECTS_UPDATE = 1 << 8

    # Media
    MEDIA_READ = 1 << 9
    MEDIA_CREATE = 1 << 10
    MEDIA_UPDATE = 1 << 11
    MEDIA_DELETE = 1 << 12

    # Interactions
    INTERACTIONS_MANAGE = 1 << 13

    # Contacts
    CONTACTS_READ = 1 << 14
    CONTACTS_UPDATE = 1 << 15

    # Quotes
    QUOTES_READ = 1 << 16
    QUOTES_CREATE = 1 << 17
    QUOTES_UPDATE = 1 << 18

    # Notes
    NOTES_UPDATE = 1 << 19

    # Events
    EVENTS_READ = 1 << 20
    EVENTS_CREATE = 1 << 21
    EVENTS_UPDATE = 1 << 22
    EVENTS_DELETE = 1 << 23

    # Analytics
    ANALYTICS_READ = 1 << 24
    ANALYTICS_UPDATE = 1 << 25

    # Users
    USERS_READ = 1 << 26
    USERS_CREATE = 1 << 27
    USERS_UPDATE = 1 << 28
    USERS_DELETE = 1 << 29

    # System Infrastructure
    SYSTEM_DASHBOARD = 1 << 30
    SYSTEM_SETTINGS = 1 << 31
    SYSTEM_ADMIN = 1 << 62
    SYSTEM_ROOT = 1 << 63

OWNERSHIP_FALLBACKS = {
    Permission.BLOGS_UPDATE: Permission.BLOGS_UPDATE_OWN,
    Permission.BLOGS_DELETE: Permission.BLOGS_DELETE_OWN
}

# ========== DATA ACCESS HELPERS ==========

def _load_users_from_file() -> Dict[str, Any]:
    users_path: str = "data/users.json"
    if not os.path.exists(users_path):
        logger.warning(f"Users file not found at {users_path}")
        return {}
    
    try:
        with open(users_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
            return data.get("users", {})
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {users_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load users from {users_path}: {e}")
        return {}

def get_users(app: Any) -> Dict[str, Any]:
    users_path: str = "data/users.json"
    if not os.path.exists(users_path):
        return {}
    
    try:
        current_mtime: float = os.path.getmtime(users_path)
        if app.users_cache is None or app.users_cache_mtime != current_mtime:
            app.users_cache = _load_users_from_file()
            app.users_cache_mtime = current_mtime
            logger.debug(f"Users cache refreshed from {users_path}")
    except Exception as e:
        logger.error(f"Error checking users.json mtime: {e}")
        return {}
    
    return app.users_cache or {}

def get_user(app: Any, username: str) -> Optional[Dict[str, Any]]:
    users: Dict[str, Any] = get_users(app)
    user_data: Optional[Dict[str, Any]] = users.get(username)
    
    if user_data is None:
        return None
        
    if not isinstance(user_data.get("password_hash"), str):
        return None
        
    # Corrected: We now expect an integer directly from the JSON
    if not isinstance(user_data.get("permissions"), int):
        logger.warning(f"User '{username}' missing valid integer permissions")
        return None
        
    return user_data

# ========== AUTH MANAGER CLASS ==========

class AuthManager:
    @staticmethod
    def get_user_bitmask(app: Any, username: str) -> int:
        user = get_user(app, username)
        if not user:
            return 0
        return user.get("permissions", 0)

    @staticmethod
    def has_permission(app: Any, username: str, required_perm: Permission) -> bool:
        user_bits = AuthManager.get_user_bitmask(app, username)
        
        # 1. Super User Check
        if (user_bits & Permission.SYSTEM_ROOT) == Permission.SYSTEM_ROOT:
            return True
            
        # 2. Standard Check
        return (user_bits & required_perm) == required_perm

    @staticmethod
    def has_permission_frontend(user_permissions: int, required_perm: Permission) -> bool:
        if (user_permissions & Permission.SYSTEM_ROOT) == Permission.SYSTEM_ROOT:
            return True
        return (user_permissions & required_perm) == required_perm

    @staticmethod
    def verify_ownership(username: str, blog_id: str) -> bool:
        from utility.blogs import get_item_by_id
        if not blog_id:
            return False

        try:
            blog = get_item_by_id(blog_id)
            if not blog:
                return False

            authors = blog.get("author", [])
            if isinstance(authors, str):
                authors = [authors]

            return any(
                isinstance(author, str) and username.strip() == author.strip()
                for author in authors
            )
        except Exception as exc:
            logger.error(f"Error loading blog for ownership check: {exc}")
            return False

def _resolve_blog_id(kwargs: Dict[str, Any]) -> Optional[str]:
    blog_id = None
    if "blog_id" in kwargs and kwargs["blog_id"]:
        blog_id = kwargs["blog_id"]
    elif request.view_args and request.view_args.get("blog_id"):
        blog_id = request.view_args.get("blog_id")
    else:
        payload = request.get_json(silent=True) or {}
        if isinstance(payload, dict):
            blog_id = payload.get("blog_id") or payload.get("id")

        if not blog_id:
            form_id = request.form.get("blog_id") or request.form.get("id")
            if form_id: blog_id = form_id

        if not blog_id:
            query_id = request.args.get("blog_id") or request.args.get("id")
            if query_id: blog_id = query_id

    return str(blog_id) if blog_id else None

# ========== DECORATOR ==========

def permission_required(required_perm: Permission) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            from CustomFlaskClass import app
            username: Optional[str] = session.get("username")
            
            if not username or not get_user(app, username):
                logger.warning(f"Unauthorized access attempt to {request.path} from {request.remote_addr}")
                return redirect(url_for("admin.login", next=request.path))
            
            # 1. Primary Global Check (e.g., BLOGS_UPDATE)
            if AuthManager.has_permission(app, username, required_perm):
                return f(*args, **kwargs)

            # 2. Automatic Fallback Check (e.g., lacks global update, check for BLOGS_UPDATE_OWN)
            fallback_perm = OWNERSHIP_FALLBACKS.get(required_perm)
            if fallback_perm and AuthManager.has_permission(app, username, fallback_perm):
                blog_id = _resolve_blog_id(kwargs)
                if blog_id and AuthManager.verify_ownership(username, blog_id):
                    # They have the scoped permission AND own the specific asset
                    return f(*args, **kwargs)

            # Deny if they lack global rights and either lack scoped rights or failed ownership check
            logger.warning(f"Permission denied for user '{username}' (requires '{required_perm.name}')")
            abort(403)
            
        return cast(F, decorated_function)
    return decorator

def pw_protected(password_hash: str) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            url_password = request.args.get("password")
            
            if url_password is None or not check_password_hash(password_hash, url_password):
                abort(401)
                
            return f(*args, **kwargs)
        return cast(F, decorated_function)
    return decorator


# ========== CAPTCHA FUNCTIONS ==========
CAPTCHA_DATA = {
    "food": ["apple-whole", "carrot", "utensils", "martini-glass", "pizza-slice", "burger", "mug-hot", "egg", "bread-slice", "fish", "lemon", "ice-cream", "pepper-hot", "cheese"],
    "weather": ["sun", "cloud", "cloud-rain", "snowflake", "wind", "umbrella", "tornado", "droplet", "bolt", "moon", "cloud-bolt", "rainbow", "temperature-high", "smog"],
    "tools": ["hammer", "wrench", "screwdriver", "screwdriver-wrench", "toolbox", "ruler", "pen", "scissors", "compass-drafting", "paint-roller", "trowel", "plug"],
    "animals": ["dog", "cat", "dove", "fish", "horse", "cow", "hippo", "otter", "crow", "dragon", "spider", "frog", "worm"],
    "sports": ["football", "basketball", "baseball", "table-tennis-paddle-ball", "volleyball", "hockey-puck", "golf-ball", "skateboard", "bicycle", "person-swimming", "bowling-ball", "dumbbell", "medal"],
    "music": ["music", "guitar", "drum", "microphone", "headphones", "compact-disc", "circle-play", "circle-pause", "volume-high", "radio", "record-vinyl"],
    "transport": ["car", "truck", "bus", "train", "plane", "anchor", "motorcycle", "helicopter", "rocket", "ship", "subway", "tractor"],
    "nature": ["tree", "leaf", "mountain", "droplet", "water", "fire", "seedling", "mountain-sun", "wind", "volcano", "sun-plant-wilt"]
}


def generate_captcha():
    category = random.choice(list(CAPTCHA_DATA.keys()))
    correct_icon = random.choice(CAPTCHA_DATA[category])
    
    decoy_icons = []
    while len(decoy_icons) < 3:
        other_category = random.choice(list(CAPTCHA_DATA.keys()))
        if other_category != category:
            candidate = random.choice(CAPTCHA_DATA[other_category])
            if candidate not in decoy_icons and candidate != correct_icon:
                decoy_icons.append(candidate)
    
    choices = [correct_icon] + decoy_icons
    random.shuffle(choices)
    
    captcha_id = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    
    if "captcha_data" not in session:
        session["captcha_data"] = {}
    
    session["captcha_data"][captcha_id] = {
        "category": category,
        "correct_answer": correct_icon,
        "choices": choices
    }
    session.modified = True
    
    logger.info(f"Generated captcha {captcha_id} for category '{category}'")
    
    return {
        "captcha_id": captcha_id,
        "category": category,
        "choices": choices
    }


def verify_captcha(captcha_id: str, selected_icon: str) -> bool:
    if "captcha_data" not in session or captcha_id not in session["captcha_data"]:
        logger.warning(f"Captcha verification failed: Invalid captcha ID {captcha_id}")
        return False
    
    captcha_info = session["captcha_data"][captcha_id]
    correct_answer = captcha_info["correct_answer"]
    
    del session["captcha_data"][captcha_id]
    session.modified = True
    
    is_correct = selected_icon == correct_answer
    
    if is_correct:
        logger.info(f"Captcha {captcha_id} verified successfully")
    else:
        logger.warning(f"Captcha {captcha_id} verification failed: Expected '{correct_answer}', got '{selected_icon}'")
    
    return is_correct


def refresh_captcha(captcha_id: str):
    if "captcha_data" in session and captcha_id in session["captcha_data"]:
        del session["captcha_data"][captcha_id]
        session.modified = True
    
    return generate_captcha()