from flask import Blueprint
from .internal import internal_blueprint
from .legal import legal_blueprint
from .products import product_blueprint
from .checkout import checkout_blueprint
from .admin import admin_blueprint
from .other_routes import other_blueprint

# Collect all blueprints from globals()
blueprints = [obj for _, obj in globals().items() if isinstance(obj, Blueprint)]

__all__ = ["blueprints"]
