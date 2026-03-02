from .data import blogs
from .data.settings import get_settings
from . import blog_helpers
from . import logging_utility

# convenience imports
def __getattr__(name):
    if name == "blogs":
        return blogs
    if name == "get_settings":
        return get_settings
    if name == "blog_helpers":
        return blog_helpers
    raise AttributeError(f"module {__name__} has no attribute {name}")
