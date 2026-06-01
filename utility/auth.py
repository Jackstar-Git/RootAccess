import random
import string
from enum import IntFlag
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast
from flask import abort, redirect, url_for, request, session
from werkzeug.security import check_password_hash
from utility.logging_utility import logger, log_with_user
from utility.users import get_user_by_username, get_user_by_id

F = TypeVar("F", bound=Callable[..., Any])

class Permission(IntFlag):
    BLOGS_READ = 1 << 0
    BLOGS_CREATE = 1 << 1
    BLOGS_UPDATE_OWN = 1 << 2
    BLOGS_UPDATE = 1 << 3
    BLOGS_DELETE_OWN = 1 << 4
    BLOGS_DELETE = 1 << 5
    PROJECTS_READ = 1 << 6
    PROJECTS_CREATE = 1 << 7
    PROJECTS_UPDATE = 1 << 8
    MEDIA_READ = 1 << 9
    MEDIA_CREATE = 1 << 10
    MEDIA_UPDATE = 1 << 11
    MEDIA_DELETE = 1 << 12
    INTERACTIONS_MANAGE = 1 << 13
    CONTACTS_READ = 1 << 14
    CONTACTS_UPDATE = 1 << 15
    QUOTES_READ = 1 << 16
    QUOTES_CREATE = 1 << 17
    QUOTES_UPDATE = 1 << 18
    NOTES_UPDATE = 1 << 19
    EVENTS_READ = 1 << 20
    EVENTS_CREATE = 1 << 21
    EVENTS_UPDATE = 1 << 22
    EVENTS_DELETE = 1 << 23
    ANALYTICS_READ = 1 << 24
    ANALYTICS_UPDATE = 1 << 25
    USERS_READ = 1 << 26
    USERS_CREATE = 1 << 27
    USERS_UPDATE = 1 << 28
    USERS_DELETE = 1 << 29
    SYSTEM_DASHBOARD = 1 << 30
    SYSTEM_SETTINGS = 1 << 31
    SYSTEM_ADMIN = 1 << 62
    SYSTEM_ROOT = 1 << 63

OWNERSHIP_FALLBACKS = {
    Permission.BLOGS_UPDATE: Permission.BLOGS_UPDATE_OWN,
    Permission.BLOGS_DELETE: Permission.BLOGS_DELETE_OWN
}

class AuthManager:
    @staticmethod
    def get_user_bitmask(id: str) -> int:
        user = get_user_by_id(id)
        if not user:
            return 0
        return user.get("permissions", 0)

    @staticmethod
    def has_permission(id: str, required_perm: Permission) -> bool:
        user = get_user_by_id(id)
        if not user: return False
        
        user_bits = user.get("permissions", 0)
        if (user_bits & Permission.SYSTEM_ROOT) == Permission.SYSTEM_ROOT:
            return True
        return (user_bits & required_perm) == required_perm
    
    @staticmethod
    def has_permission_frontend(user_permissions: int, required_perm: Permission) -> bool:
        if (user_permissions & Permission.SYSTEM_ROOT) == Permission.SYSTEM_ROOT:
            return True
        return (user_permissions & required_perm) == required_perm

    @staticmethod
    def verify_ownership(id: str, blog_id: str) -> bool:
        from utility.blogs import get_item_by_id
        blog = get_item_by_id(blog_id)
        if not blog: return False
        user = get_user_by_id(id)
        if not user: return False

        return user.get("username", "").strip() in [a.strip() for a in blog.get("authors", [])]


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


def permission_required(required_perm: Permission) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            user_id = session.get("user_id")
            if not user_id:
                return redirect(url_for("admin.login", next=request.path))

            if AuthManager.has_permission(user_id, required_perm):
                return f(*args, **kwargs)

            fallback_perm = OWNERSHIP_FALLBACKS.get(required_perm)
            if fallback_perm and AuthManager.has_permission(user_id, fallback_perm):
                blog_id = _resolve_blog_id(kwargs)
                if blog_id and AuthManager.verify_ownership(user_id, blog_id):
                    return f(*args, **kwargs)


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