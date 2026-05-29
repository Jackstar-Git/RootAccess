from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast
from flask import abort, redirect, url_for, request, session
from utility.logging_utility import logger
from werkzeug.security import check_password_hash
import json
import os
import random
import string

F = TypeVar("F", bound=Callable[..., Any])

def _load_users_from_file() -> Dict[str, Any]:
    # Load users from users.json with error handling
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
        
        # If cache is empty or file was modified, reload
        if app.users_cache is None or app.users_cache_mtime != current_mtime:
            app.users_cache = _load_users_from_file()
            app.users_cache_mtime = current_mtime
            logger.debug(f"Users cache refreshed from {users_path}")
    except Exception as e:
        logger.error(f"Error checking users.json mtime: {e}")
        return {}
    
    return app.users_cache or {}

def get_user(app: Any, username: str) -> Optional[Dict[str, Any]]:
    # Get a user by username (dict with 'password_hash' and 'permissions', or None)
    users: Dict[str, Any] = get_users(app)
    user_data: Optional[Dict[str, Any]] = users.get(username)
    
    if user_data is None:
        return None
    
    if not isinstance(user_data.get("password_hash"), str):
        logger.warning(f"User '{username}' missing valid password_hash")
        return None
    
    if not isinstance(user_data.get("permissions"), list):
        logger.warning(f"User '{username}' missing valid permissions list")
        return None
    
    return user_data

def get_user_permissions(app: Any, username: str) -> List[str]:
    # Get permissions for a user (admin implies all permissions)
    # Returns empty list if user not found
    user: Optional[Dict[str, Any]] = get_user(app, username)
    
    if user is None:
        return []
    
    permissions: Any = user.get("permissions", [])
    
    if isinstance(permissions, list):
        # If user has 'admin', they have all permissions
        if "admin" in permissions:
            return ["admin"]
        return permissions
    
    logger.warning(f"User '{username}' has invalid permissions format")
    return []

def has_permission(app: Any, username: str, permission: str) -> bool:
    # Check if a user has a specific permission
    # Admin permission implies all other permissions
    permissions: List[str] = get_user_permissions(app, username)
    
    if "admin" in permissions:
        return True
    
    return permission in permissions


def _user_owns_blog(username: str, blog_id: Any) -> bool:
    from utility.blogs import get_item_by_id

    if not blog_id:
        return False

    try:
        blog = get_item_by_id(blog_id)
    except Exception as exc:
        logger.error(f"Error loading blog for ownership check: {exc}")
        return False

    if not blog:
        return False

    authors = blog.get("author", [])
    if isinstance(authors, str):
        authors = [authors]

    return any(
        isinstance(author, str) and username.strip() == author.strip()
        for author in authors
    )


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
            if form_id:
                blog_id = form_id

        if not blog_id:
            query_id = request.args.get("blog_id") or request.args.get("id")
            if query_id:
                blog_id = query_id

    return str(blog_id) if blog_id else None

# ========== DECORATORS ==========

def permission_required(required_permission: str) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            from CustomFlaskClass import app
            username: Optional[str] = session.get("username")
            
            # First check if user is logged in
            if not username or not get_user(app, username):
                logger.warning(f"Unauthorized access attempt to {request.path} from {request.remote_addr}")
                return redirect(url_for("admin.login", next=request.path))
            
            # 1. Global Permission Check (e.g., user has 'blogs:update' or 'admin')
            if has_permission(app, username, required_permission):
                return f(*args, **kwargs)

            # 2. Ownership Fallback Check (e.g., user lacks 'blogs:update' but has 'blogs:update:own')
            own_permission_variant = f"{required_permission}:own"
            
            if has_permission(app, username, own_permission_variant):
                # User has the constrained permission, so ownership MUST be verified
                blog_id = _resolve_blog_id(kwargs)
                if blog_id and _user_owns_blog(username, blog_id):
                    return f(*args, **kwargs)

            # Deny access if neither check passes
            logger.warning(
                f"Permission denied for user '{username}' to access {request.path} "
                f"(requires '{required_permission}')"
            )
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