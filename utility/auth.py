from functools import wraps
from typing import Any, Callable, TypeVar, cast
from flask import redirect, url_for, request, session
from utility.logging_utility import logger

F = TypeVar("F", bound=Callable[..., Any])

def login_required(f: F) -> F:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not session.get("is_admin"):
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return redirect(url_for("admin.login", next=request.path))
        return f(*args, **kwargs)
    return cast(F, decorated_function)
