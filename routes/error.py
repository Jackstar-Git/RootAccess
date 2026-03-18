# ========== IMPORTS ==========
from flask import request, render_template, jsonify, Blueprint
from flask_wtf.csrf import CSRFError

from CustomFlaskClass import app
from utility.logging_utility import logger

# ========== ERROR HANDLERS ==========
@app.errorhandler(405)
def method_not_allowed(error) -> jsonify:
    logger.warning(f"405 Method Not Allowed: {request.path}; {error}")
    return jsonify({"error": str(error), "code": 405})

@app.errorhandler(404)
def page_not_found(error) -> render_template:
    logger.warning(f"A page was not found: {request.path}; {error}")
    return render_template("meta/404.jinja")

@app.errorhandler(403)
def access_denied(error) -> render_template:
    logger.warning(f"403 Access Denied: {request.path}; {error}")
    return render_template("meta/403.jinja")

@app.errorhandler(CSRFError)
def handle_csrf_error(e) -> jsonify:
    if "missing" in str(e):
        return jsonify({"error": "CSRF token missing", "code": 400})
    return jsonify({"error": "CSRF error", "code": 400})

@app.errorhandler(Exception)
def handle_general_errors(e) -> jsonify:
    logger.critical(f"An unexpected error occurred: {str(e)}", exc_info=True)
    return jsonify({"error": "Internal Server Error", "code": 500})
