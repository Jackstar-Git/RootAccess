from flask import Blueprint
from .internal import internal_blueprint

# Collect all blueprints from globals()
blueprints = [obj for _, obj in globals().items() if isinstance(obj, Blueprint)]

__all__ = ["blueprints"]
