from functools import wraps
from typing import Any, Callable, TypeVar, cast
from flask import abort, redirect, url_for, request, session
from utility.logging_utility import logger
import random
import string

F = TypeVar("F", bound=Callable[..., Any])

def login_required(f: F) -> F:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not session.get("is_admin"):
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return redirect(url_for("admin.login", next=request.path))
        return f(*args, **kwargs)
    return cast(F, decorated_function)


def pw_protected(password: str) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if request.args.get("password") != password:
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
