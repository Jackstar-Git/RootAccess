from functools import wraps
from typing import Any, Callable, TypeVar, cast
from flask import redirect, url_for, request, session
from utility.logging_utility import logger
import random
from flask import session

F = TypeVar("F", bound=Callable[..., Any])

def login_required(f: F) -> F:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not session.get("is_admin"):
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return redirect(url_for("admin.login", next=request.path))
        return f(*args, **kwargs)
    return cast(F, decorated_function)



CAPTCHA_DATA = {
    "Weather": ["fa-sun", "fa-cloud-rain", "fa-snowflake", "fa-bolt"],
    "Transport": ["fa-car", "fa-plane", "fa-ship", "fa-bicycle"],
    "Food": ["fa-apple-whole", "fa-burger", "fa-pizza-slice", "fa-carrot"],
    "Tools": ["fa-hammer", "fa-screwdriver-wrench", "fa-wrench", "fa-mop"],
    "Communication": ["fa-envelope", "fa-phone", "fa-comments", "fa-paper-plane"]
}

def generate_captcha():
    target_category = random.choice(list(CAPTCHA_DATA.keys()))
    correct_icon = random.choice(CAPTCHA_DATA[target_category])
    
    decoys = []
    other_categories = [c for c in CAPTCHA_DATA.keys() if c != target_category]
    selected_decoy_cats = random.sample(other_categories, 3)
    for cat in selected_decoy_cats:
        decoys.append(random.choice(CAPTCHA_DATA[cat]))
    
    options = decoys + [correct_icon]
    random.shuffle(options)
    
    session['captcha_answer'] = correct_icon
    
    return {
        "question": f"Select the {target_category} icon",
        "options": options
    }

def verify_captcha(user_answer):
    stored_answer = session.get('captcha_answer')
    if not stored_answer:
        return False
    
    session.pop('captcha_answer', None)
    return user_answer == stored_answer
