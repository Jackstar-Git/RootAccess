import logging
import os
from datetime import datetime
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from utility.auth import login_required
from utility.blogs import load_blogs, add_blog, get_item_by_id, update_blog
from utility.calendar import generate_calendar
from utility.logging_utility import logger
from utility.settings import get_settings, update_settings

logger = logging.getLogger(__name__)
admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

# ============== AUTHENTICATION ==============
@admin_blueprint.before_request
def protect_admin() -> Optional[redirect]:
    if request.endpoint != "admin.login" and not session.get("is_admin"):
        return redirect(url_for("admin.login"))

@admin_blueprint.route("/login", methods=["GET", "POST"])
def login() -> Union[render_template, redirect]:
    if session.get("is_admin"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        input_pass: Optional[str] = request.form.get("password")
        stored_hash: Optional[str] = get_settings("admin-password-hash")

        if stored_hash and check_password_hash(stored_hash, input_pass):
            session.clear()
            session.permanent = True
            session["is_admin"] = True
            return redirect(url_for("admin.dashboard"))

        logger.warning(f"Unauthorized admin access attempt from {request.remote_addr}")
        flash("Access denied: Wrong password", "error")

    return render_template("admin/login.jinja-html")

@admin_blueprint.route("/logout")
def logout() -> redirect:
    session.clear()
    return redirect(url_for("admin.login"))

# ============== DASHBOARD ==============
@admin_blueprint.route("/dashboard")
@login_required
def dashboard() -> render_template:
    today: datetime = datetime.today()

    year: int = request.args.get("year", default=today.year, type=int)
    month: int = request.args.get("month", default=today.month, type=int)

    cal = generate_calendar(year, month)

    events: List[Dict[str, Any]] = []

    month_name: str = datetime(year, month, 1).strftime("%B")

    return render_template(
        "admin/admin.jinja-html",
        today=today,
        year=year,
        month=month,
        month_name=month_name,
        calendar=cal,
        events=events
    )

# ============== MEDIA LIBRARY ==============
@admin_blueprint.route("/media/all", methods=["GET"])
def library() -> render_template:
    ROOT_DIR: str = "uploads"
    current_path: str = request.args.get("path", "/")

    safe_path: str = current_path.strip("/")
    abs_path: str = os.path.join(ROOT_DIR, safe_path)

    files_data: List[Dict[str, Any]] = []

    if os.path.exists(abs_path) and os.path.isdir(abs_path):
        for item in os.listdir(abs_path):
            item_path: str = os.path.join(abs_path, item)
            stats = os.stat(item_path)

            ext: str = os.path.splitext(item)[1].lower()
            if os.path.isdir(item_path):
                file_type: str = "folder"
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

# ============== LOGS ==============
@admin_blueprint.route("/settings/logs", methods=["GET"])
def server_logs() -> render_template:
    logger.info("Server logs route accessed")
    with open("logs/app.log", "r", encoding="utf-8") as file:
        lines: List[str] = file.readlines()

    clean_lines: List[str] = lines[-50::]
    logger.info("Rendering server logs page")
    return render_template("admin/logs.jinja-html", logs=clean_lines)

# ============== BLOGS ==============
@admin_blueprint.route("/blogs/all", methods=["GET"])
@login_required
def all_blogs() -> render_template:
    search_query: str = request.args.get("search", "").lower()
    topic_query: str = request.args.get("topic", "all")

    raw_blogs = load_blogs()
    display_blogs: List[Dict[str, Any]] = []

    for blog in raw_blogs:
        if topic_query != "all" and topic_query not in blog.get("topics", []):
            continue

        if search_query:
            title_match: bool = search_query in blog.get("title", "").lower()
            author_match: bool = any(search_query in a.lower() for a in blog.get("author", []))
            if not (title_match or author_match):
                continue

        dt: datetime = datetime.fromtimestamp(blog.get("time_created", 0))
        blog['formatted_date'] = dt.strftime("%b %d, %Y")

        display_blogs.append(blog)

    display_blogs.sort(key=lambda x: x.get("time_created", 0), reverse=True)

    return render_template(
        "admin/all-blogs.jinja-html",
        blogs=display_blogs,
        settings=get_settings("blog_config"),
        query_params=request.args
    )

@admin_blueprint.route("/settings/server", methods=["GET", "POST"])
@login_required
def server_settings():
    if request.method == "POST":
        try:
            settings = get_settings()
            form_data = request.form.to_dict()

            settings['server_config']['maintenance'] = 'maintenance' in form_data
            settings['server_config']['MAX_CONTENT_LENGTH'] = int(form_data.get('max_content_length', 0))
            settings['server_config']['PERMANENT_SESSION_LIFETIME'] = int(form_data.get('permanent_session_lifetime', 0))
            settings['server_config']['SESSION_COOKIE_NAME'] = form_data.get('session_cookie_name', '')
            settings['robots_txt'] = form_data.get('robots_txt', '')

            update_settings(settings)
            logger.info("Server settings updated successfully")

            return jsonify({
                "success": True,
                "message": "Settings updated successfully"
            })
        except Exception as e:
            logger.error(f"Error updating server settings: {str(e)}")
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

    settings = get_settings()
    return render_template("admin/server-settings.jinja-html",
                         settings=settings,
                         robots=settings.get('robots_txt', ''))


@admin_blueprint.route("/blogs/create/", methods=["GET", "POST"])
@login_required
def create_blog():
    logger.info("Accessing blog creation portal.")

    if request.method == "POST":
        # 1. Handle Thumbnail Upload
        # The form uses name="thumbnail" for the file input
        thumbnail_file = request.files.get("thumbnail")
        image_url = "/static/assets/images/defaults/blog-placeholder.png" # Default fallback
        
        if thumbnail_file and thumbnail_file.filename:
            # Ensure the uploads directory exists
            upload_folder = "uploads"
            os.makedirs(upload_folder, exist_ok=True)
            
            # Create a unique filename using timestamp
            filename = f"{int(time.time())}_{thumbnail_file.filename}"
            thumbnail_file.save(os.path.join(upload_folder, filename))
            image_url = f"/uploads/{filename}"

        # 2. Construct Blog Data
        blog_data = {
            "author": request.form.getlist("authors[]"),
            "title": request.form.get("title"),
            "content_raw": request.form.get("content"),
            "image_url": image_url,
            "tags": [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()],
            "categories": request.form.getlist("categories")
        }
        
        # 3. Save to File
        try:
            add_blog(blog_data)
            logger.info(f"Blog '{blog_data['title']}' created successfully.")
            flash("Blog post published!", "success")
            return redirect(url_for('admin.all_blogs'))
        except Exception as e:
            logger.error(f"Failed to save blog: {str(e)}")
            flash("Error saving blog post.", "error")

    return render_template(
        "admin/add-blog.jinja-html", 
        settings=get_settings("blog_config")
    )

@admin_blueprint.route("/blogs/edit/<blog_id>", methods=["GET", "POST"])
@login_required
def edit_blog(blog_id: str):
    blog = get_item_by_id(blog_id)

    if not blog:
        flash("Post not found.", "error")
        return redirect(url_for('admin.all_blogs'))

    if request.method == "POST":
        thumbnail_file = request.files.get("thumbnail")
        image_url = blog.get("image_url")

        if thumbnail_file and thumbnail_file.filename:
            upload_folder = "uploads"
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{int(time.time())}_{thumbnail_file.filename}"
            thumbnail_file.save(os.path.join(upload_folder, filename))
            image_url = f"/uploads/{filename}"

        updated_data = {
            "author": request.form.getlist("authors[]"),
            "title": request.form.get("title"),
            "content_raw": request.form.get("content"),
            "image_url": image_url,
            "tags": [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()],
            "categories": request.form.getlist("categories"),
            "description": request.form.get("description"),
            "type": request.form.get("type"),
            "reading_time": request.form.get("reading_time")
        }

        if update_blog(blog_id, updated_data):
            flash("Successfully updated!", "success")
            return redirect(url_for('admin.all_blogs'))

    return render_template(
        "admin/edit-blog.jinja-html",
        blog=blog,
        settings=get_settings("blog_config")
    )