import logging
import os
from datetime import datetime
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from utility.auth import login_required
from utility.blogs import load_blogs, add_blog, get_item_by_id, update_blog
from utility.events import get_events 
from utility.contact import load_contacts
from utility.calendar import generate_calendar
from utility.logging_utility import logger
from utility.settings import get_settings, update_settings
from utility.others import convert_markdown_to_html
from utility.projects import query_projects, search_projects, load_projects, get_project_by_id, update_project, add_project

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
            if request.form.get("remember"):
                session.permanent = True
            else:
                session.permanent = False
            session["is_admin"] = True
            return redirect(url_for("admin.dashboard"))

        logger.warning(f"Unauthorized admin access attempt from {request.remote_addr}")
        flash("Access denied: Wrong password", "error")

    return render_template("admin/login.jinja")

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
    events: List[Dict[str, Any]] = get_events() 
    month_name: str = datetime(year, month, 1).strftime("%B")

    notes_path = "data/notes.md"
    raw_note = ""
    if os.path.exists(notes_path):
        with open(notes_path, "r", encoding="utf-8") as f:
            raw_note = f.read()
    
    html_note = convert_markdown_to_html(raw_note)

    return render_template(
        "admin/admin.jinja",
        today=today,
        year=year,
        month=month,
        month_name=month_name,
        calendar=cal,
        events=events,
        raw_note=raw_note,
        html_note=html_note
    )

# ============== CONTACTS DASHBOARD ==============
@admin_blueprint.route("/requests/contact", methods=["GET"])
@login_required
def manage_contacts() -> render_template:
    contacts = load_contacts()
    contacts.sort(key=lambda x: x.get("time_created", 0), reverse=True)
    
    for c in contacts:
        c["formatted_date"] = datetime.fromtimestamp(c.get("time_created", 0)).strftime('%Y-%m-%d %H:%M')

    return render_template("admin/contacts.jinja", contacts=contacts)


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
        "admin/media-library.jinja",
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
    return render_template("admin/logs.jinja", logs=clean_lines)

# ============== BLOGS ==============
@admin_blueprint.route("/blogs/all", methods=["GET"])
@login_required
def all_blogs() -> render_template:
    search_query: str = request.args.get("search", "").lower()
    topic_query: str = request.args.get("topic", "all")

    raw_blogs = load_blogs()
    display_blogs: List[Dict[str, Any]] = []

    for blog in raw_blogs:
        if topic_query != "all" and topic_query not in blog.get("categories", []):
            continue

        if search_query:
            title_match: bool = search_query in blog.get("title", "").lower()
            author_match: bool = any(search_query in a.lower() for a in blog.get("author", []))
            if not (title_match or author_match):
                continue

        display_blogs.append(blog)

    display_blogs.sort(key=lambda x: x.get("time_created", 0), reverse=True)

    return render_template(
        "admin/all-blogs.jinja",
        blogs=display_blogs,
        settings=get_settings("blog_config"),
        query_params=request.args
    )

@admin_blueprint.route("/blogs/categories", methods=["GET"])
@login_required
def blogs_categories() -> render_template:
    return render_template("admin/blog-settings.jinja", settings=get_settings("blog_config"))  

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
    return render_template("admin/server-settings.jinja",
                         settings=settings,
                         robots=settings.get('robots_txt', ''))


@admin_blueprint.route("/blogs/create/", methods=["GET", "POST"])
@login_required
def create_blog():
    logger.info("Accessing blog creation portal.")

    if request.method == "POST":
        thumbnail_file = request.files.get("thumbnail")
        image_url = "/static/assets/images/defaults/blog-placeholder.png" 
        
        if thumbnail_file and thumbnail_file.filename:
            upload_folder = "uploads"
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{int(time.time())}_{thumbnail_file.filename}"
            thumbnail_file.save(os.path.join(upload_folder, filename))
            image_url = f"/uploads/{filename}"

        blog_data = {
            "author": request.form.getlist("authors[]"),
            "title": request.form.get("title"),
            "content_raw": request.form.get("content"),
            "status": request.form.get("status", "draft"),
            "image_url": image_url,
            "tags": [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()],
            "categories": request.form.getlist("categories"),
            "type": request.form.get("type"),
            "reading_time": request.form.get("reading_time"),
            "description": request.form.get("description")
        }
        
        try:
            add_blog(blog_data)
            logger.info(f"Blog '{blog_data['title']}' created successfully.")
            flash("Blog post published!", "success")
            return redirect(url_for('admin.all_blogs'))
        except Exception as e:
            logger.error(f"Failed to save blog: {str(e)}")
            flash("Error saving blog post.", "error")

    return render_template(
        "admin/add-blog.jinja", 
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
            "status": request.form.get("status", "draft"),
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
        "admin/edit-blog.jinja",
        blog=blog,
        settings=get_settings("blog_config")
    )

# ============== PROJECTS ==============
@admin_blueprint.route("/projects/all", methods=["GET"])
@login_required
def all_projects() -> render_template:
    search_query: str = request.args.get("search", "").lower()
    topic_query: str = request.args.get("topic", "all")

    raw_projects = load_projects()
    display_projects: List[Dict[str, Any]] = []

    for project in raw_projects:
        if topic_query != "all" and topic_query != project.get("topic", ""):
            continue

        if search_query:
            title_match: bool = search_query in project.get("title", "").lower()
            tech_match: bool = any(search_query in tech.lower() for tech in project.get("tech_stack", []))
            if not (title_match or tech_match):
                continue

        display_projects.append(project)

    # Note: Sort by newest based on time_created
    display_projects.sort(key=lambda x: x.get("time_created", 0), reverse=True)

    return render_template(
        "admin/all-projects.jinja",
        projects=display_projects,
        query_params=request.args
    )

@admin_blueprint.route("/projects/create/", methods=["GET", "POST"])
@login_required
def create_project():
    logger.info("Accessing project creation portal.")

    if request.method == "POST":
        thumbnail_file = request.files.get("thumbnail")
        image_url = None
        
        if thumbnail_file and thumbnail_file.filename:
            upload_folder = "uploads/projects"
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{int(time.time())}_{thumbnail_file.filename}"
            thumbnail_file.save(os.path.join(upload_folder, filename))
            image_url = f"/uploads/projects/{filename}"

        project_data = {
            "title": request.form.get("title"),
            "version": request.form.get("version"),
            "description_short": request.form.get("description_short"),
            "content_raw": request.form.get("content_raw"),
            "image_url": image_url,
            "github_url": request.form.get("github_url") or None,
            "demo_url": request.form.get("demo_url") or None,
            "download_file": request.form.get("download_file") or None,
            "tech_stack": request.form.getlist("tech_stack[]"),
            "tags": [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()],
            "maturity": request.form.get("maturity"),
            "activity": request.form.get("activity"),
            "topic": request.form.get("topic")
        }
        
        try:
            add_project(project_data)
            logger.info(f"Project '{project_data['title']}' created successfully.")
            flash("Project published!", "success")
            return redirect(url_for('admin.all_projects'))
        except Exception as e:
            logger.error(f"Failed to save project: {str(e)}")
            flash("Error saving project.", "error")

    return render_template("admin/add-project.jinja")

@admin_blueprint.route("/projects/edit/<project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id: str):
    project = get_project_by_id(project_id)

    if not project:
        flash("Project not found.", "error")
        return redirect(url_for('admin.all_projects'))

    if request.method == "POST":
        thumbnail_file = request.files.get("thumbnail")
        image_url = project.get("image_url")

        if thumbnail_file and thumbnail_file.filename:
            upload_folder = "uploads/projects"
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{int(time.time())}_{thumbnail_file.filename}"
            thumbnail_file.save(os.path.join(upload_folder, filename))
            image_url = f"/uploads/projects/{filename}"

        updated_data = {
            "title": request.form.get("title"),
            "version": request.form.get("version"),
            "description_short": request.form.get("description_short"),
            "content_raw": request.form.get("content_raw"),
            "image_url": image_url,
            "github_url": request.form.get("github_url") or None,
            "demo_url": request.form.get("demo_url") or None,
            "download_file": request.form.get("download_file") or None,
            "tech_stack": request.form.getlist("tech_stack[]"),
            "tags": [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()],
            "maturity": request.form.get("maturity"),
            "activity": request.form.get("activity"),
            "topic": request.form.get("topic")
        }

        if update_project(project_id, updated_data):
            flash("Successfully updated!", "success")
            return redirect(url_for('admin.all_projects'))

    return render_template("admin/edit-project.jinja", project=project)