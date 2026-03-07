from datetime import datetime
import os

from flask import render_template, request, redirect, url_for, session, Blueprint
from utility.logging_utility import logger
from utility import get_settings, calendar
from utility.auth import login_required
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import logging

logger = logging.getLogger(__name__)
admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

@admin_blueprint.before_request
def protect_admin():
    if request.endpoint != "admin.login" and not session.get("is_admin"):
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

    return render_template("admin/login.jinja-html")

@admin_blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))

@admin_blueprint.route("/dashboard")
@login_required
def dashboard():
    today = datetime.today()
    
    year = request.args.get("year", default=today.year, type=int)
    month = request.args.get("month", default=today.month, type=int)

    cal = calendar.generate_calendar(year, month)

    events = [] 
    
    month_name = datetime(year, month, 1).strftime("%B")

    return render_template(
        "admin/admin.jinja-html",
        today=today,
        year=year,
        month=month,
        month_name=month_name,
        calendar=cal,
        events=events
    )

@admin_blueprint.route("/media/all", methods=["GET"])
def library():
    ROOT_DIR = "uploads"
    current_path = request.args.get("path", "/")
    
    safe_path = current_path.strip("/")
    abs_path = os.path.join(ROOT_DIR, safe_path)

    files_data = []
    
    if os.path.exists(abs_path) and os.path.isdir(abs_path):
        for item in os.listdir(abs_path):
            item_path = os.path.join(abs_path, item)
            stats = os.stat(item_path)
            
            # Determine type
            ext = os.path.splitext(item)[1].lower()
            if os.path.isdir(item_path):
                file_type = "folder"
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                file_type = "image"
            elif ext in ['.mp4', '.mov', '.avi']:
                file_type = "video"
            elif ext in ['.zip', '.rar', '.7z']:
                file_type = "archive"
            else:
                file_type = "document"

            files_data.append({
                "name": item,
                "type": file_type,
                "last_modified": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M'),
                "size": stats.st_size if not os.path.isdir(item_path) else 0
            })

    files_data.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))

    return render_template(
        "admin/media-library.jinja-html", 
        files=files_data, 
        path=current_path,
        root=ROOT_DIR
    )