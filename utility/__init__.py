from . import blogs
from .settings import get_settings
from . import logging_utility
from . import projects
from . import quotes
from . import calendar
from . import events
from . import path_files as path_utils
from . import auth
from . import contact

# convenience imports
def __getattr__(name):
    if name == "blogs":
        return blogs
    if name == "get_settings":
        return get_settings
    if name == "logging_utility":
        return logging_utility
    if name == "quotes":
        return quotes
    if name == "projects":
        return projects
    if name == "calendar":
        return calendar
    if name == "events":
        return events
    if name == "path_utils":
        return path_utils
    if name == "auth":
        return auth
    if name == "contact":
        return contact
    raise AttributeError(f"module {__name__} has no attribute {name}")
