# ========== IMPORTS ==========
from flask import request, render_template, jsonify, Blueprint
from flask.typing import ResponseReturnValue
from flask_wtf.csrf import CSRFError

from CustomFlaskClass import app
from utility.logging_utility import logger, log_with_user

# ========== ERROR HANDLERS ==========
@app.errorhandler(429)
def ratelimit_handler(e) -> ResponseReturnValue:
    logger.warning(f"429 Rate Limit Exceeded: {request.path} by {request.remote_addr}; {e.description}")
    return jsonify({
        "error": "Too Many Requests",
        "message": "You have exceeded your request quota. Please wait a moment before trying again.",
        "code": 429
    }), 429

@app.errorhandler(405)
def method_not_allowed(error) -> ResponseReturnValue:
    logger.warning(f"405 Method Not Allowed: {request.path}; {error}")
    return jsonify({
        "error": "Method Not Allowed",
        "message": f"The {request.method} method is not allowed for this endpoint.",
        "code": 405
    })

@app.errorhandler(404)
def page_not_found(error) -> ResponseReturnValue:
    logger.warning(f"A page was not found: {request.path}; {error}")
    return render_template("meta/404.jinja")

@app.errorhandler(403)
def access_denied(error) -> ResponseReturnValue:
    username = request.environ.get('REMOTE_USER', 'unknown')
    log_with_user("warning", f"Access denied to {request.path}", username)
    return render_template("meta/403.jinja", trigger_error_toast=True, error_message="You do not have permission to access this resource.")

@app.errorhandler(CSRFError)
def handle_csrf_error(e) -> ResponseReturnValue:
    logger.warning(f"CSRF Error: {str(e)}")
    if "missing" in str(e).lower():
        return jsonify({
            "error": "Security Validation Failed",
            "message": "Security token missing. Please refresh and try again.",
            "code": 400
        }), 400
    return jsonify({
        "error": "Security Validation Failed",
        "message": "Security check failed. Please refresh the page and try again.",
        "code": 400
    }), 400

@app.errorhandler(Exception)
def handle_general_errors(e) -> ResponseReturnValue:
    logger.critical(f"An unexpected error occurred: {str(e)}", exc_info=True)
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Our team has been notified. Please try again later.",
        "code": 500
    }), 500
