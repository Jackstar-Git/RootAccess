from flask import render_template, request, redirect, url_for, session, Blueprint
from utility.logging_utility import logger
from utility import get_settings

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import logging

logger = logging.getLogger(__name__)
admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated_function

@admin_blueprint.before_request
def protect_admin():
    if request.endpoint != 'admin.login' and not session.get("is_admin"):
        return redirect(url_for("admin.login"))

@admin_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if session.get("is_admin"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        input_pass = request.form.get("password")
        stored_hash = get_settings("admin-password-hash")

        if stored_hash and check_password_hash(stored_hash, input_pass):
            session.clear()
            session.permanent = True
            session["is_admin"] = True
            return redirect(url_for("admin.dashboard"))
        
        logger.warning(f"Unauthorized admin access attempt from {request.remote_addr}")
        flash("Access denied: Wrong password", "error")

    return render_template("login.jinja-html")

@admin_blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))

@admin_blueprint.route("/dashboard")
@login_required
def dashboard():
    return render_template("admin/dashboard.jinja-html")