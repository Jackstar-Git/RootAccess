# ========== IMPORTS ==========
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from CustomFlaskClass import app
from utility.auth import login_required
from utility.blogs import add_blog, get_item_by_id, load_blogs, update_blog
from utility.calendar import generate_calendar
from utility.contact import load_contacts
from utility.events import get_events
from utility.logging_utility import logger
from utility.others import convert_markdown_to_html
from utility.projects import add_project, get_project_by_id, load_projects, update_project
from utility.settings import get_settings, update_settings
from utility.analytics import get_all_analytics

# ========== BLUEPRINT INITIALIZATION ==========
admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

# ========== AUTHENTICATION ROUTES ==========
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

# ========== DASHBOARD ROUTES ==========
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

# ========== ANALYTICS ROUTES ==========
@admin_blueprint.route("/analytics")
@login_required
def analytics():
    analytics_data = get_all_analytics() 
    analytics_list = list(analytics_data.values()) 
    
    total_visits = sum(item.get("visits", 0) for item in analytics_list)
    total_unique = sum(item.get("unique_visits", 0) for item in analytics_list)
    
    return render_template(
        "admin/analytics.jinja", 
        analytics=analytics_list,
        total_visits=total_visits, 
        total_unique=total_unique
    )

# ========== CONTACT ROUTES ==========
@admin_blueprint.route("/requests/contact", methods=["GET"])
@login_required
def manage_contacts() -> render_template:
    contacts = load_contacts()
    contacts.sort(key=lambda x: x.get("time_created", 0), reverse=True)

    for c in contacts:
        c["formatted_date"] = datetime.fromtimestamp(c.get("time_created", 0)).strftime("%Y-%m-%d %H:%M")

    return render_template("admin/contacts.jinja", contacts=contacts)

# ========== MEDIA ROUTES ==========
@admin_blueprint.route("/media/all", methods=["GET"])
@login_required
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
            elif ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                file_type = "image"
            elif ext in [".mp4", ".mov", ".avi"]:
                file_type = "video"
            elif ext in [".zip", ".rar", ".7z"]:
                file_type = "archive"
            else:
                file_type = "document"

            files_data.append({
                "name": item,
                "type": file_type,
                "last_modified": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "size": stats.st_size if not os.path.isdir(item_path) else 0
            })

    files_data.sort(key=lambda x: (x["type"] != "folder", x["name"].lower()))

    return render_template(
        "admin/media-library.jinja",
        files=files_data,
        path=current_path,
        root=ROOT_DIR
    )

# ========== LOGS ROUTES ==========
@admin_blueprint.route("/settings/logs", methods=["GET"])
@login_required
def server_logs() -> render_template:
    logger.info("Server logs route accessed")
    with open("logs/app.log", "r", encoding="utf-8") as file:
        lines: List[str] = file.readlines()

    clean_lines: List[str] = lines[-50::]
    logger.info("Rendering server logs page")
    return render_template("admin/logs.jinja", logs=clean_lines)

# ========== BLOGS ROUTES ==========
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

@admin_blueprint.route("/blogs/create/", methods=["GET", "POST"])
@login_required
def create_blog():
    logger.info("Accessing blog creation portal.")

    if request.method == "POST":
        thumbnail_file = request.files.get("thumbnail")
        image_url = "/static/assets/images/defaults/blog-placeholder.png"

        if thumbnail_file and thumbnail_file.filename:
            upload_folder = "uploads/blogs"
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{int(time.time())}_{thumbnail_file.filename}"
            thumbnail_file.save(os.path.join(upload_folder, filename))
            image_url = f"/{upload_folder}/{filename}"

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
            logger.info(f'Blog "{blog_data["title"]}" created successfully.')
            flash("Blog post published!", "success")
            return redirect(url_for("admin.all_blogs"))
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
        return redirect(url_for("admin.all_blogs"))

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
            return redirect(url_for("admin.all_blogs"))

    return render_template(
        "admin/edit-blog.jinja",
        blog=blog,
        settings=get_settings("blog_config")
    )

# ========== PROJECTS ROUTES ==========
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
            logger.info(f'Project "{project_data["title"]}" created successfully.')
            flash("Project published!", "success")
            return redirect(url_for("admin.all_projects"))
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
        return redirect(url_for("admin.all_projects"))

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
            return redirect(url_for("admin.all_projects"))

    return render_template("admin/edit-project.jinja", project=project)

# ========== SETTINGS ROUTES ==========
@admin_blueprint.route("/settings/server", methods=["GET", "POST"])
@login_required
def server_settings():
    if request.method == "POST":
        try:
            settings = get_settings() or {}
            form_data = request.form.to_dict()

            if "server_config" not in settings:
                settings["server_config"] = {}

            settings["server_config"]["maintenance"] = "maintenance" in form_data
            settings["server_config"]["MAX_CONTENT_LENGTH"] = int(form_data.get("max_content_length", 12582912))
            settings["server_config"]["PERMANENT_SESSION_LIFETIME"] = int(form_data.get("permanent_session_lifetime", 1800))
            settings["server_config"]["SESSION_COOKIE_NAME"] = form_data.get("session_cookie_name", "session")
            settings["server_config"]["SESSION_COOKIE_HTTPONLY"] = "session_cookie_httponly" in form_data
            settings["server_config"]["SESSION_COOKIE_SECURE"] = "session_cookie_secure" in form_data
            settings["server_config"]["SESSION_COOKIE_SAMESITE"] = form_data.get("session_cookie_samesite", "Lax")

            with open("robots.txt", "w") as file:
                file.write(form_data.get("robots_txt", "").replace("\n", ""))

            update_settings(settings)
            return jsonify({"success": True, "message": "Settings updated successfully"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    robots = ""
    with open("robots.txt", "r") as file:
        robots = file.read()

    settings = get_settings() or {}
    return render_template("admin/server-settings.jinja",
                           settings=settings,
                           server_config=settings.get("server_config", {}),
                           robots_txt=robots)

@admin_blueprint.route("/settings/general", methods=["GET", "POST"])
@login_required
def general_settings():
    if request.method == "POST":
        try:
            settings = get_settings() or {}
            form_data = request.form.to_dict()

            if "general_config" not in settings:
                settings["general_config"] = {}

            settings["general_config"]["site_name"] = form_data.get("site_name", "")
            settings["general_config"]["site_description"] = form_data.get("site_description", "")

            update_settings(settings)
            return jsonify({"success": True, "message": "Settings updated successfully"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    settings = get_settings() or {}
    return render_template("admin/general-settings.jinja",
                           settings=settings,
                           general_config=settings.get("general_config", {}))

# ========== APPEARANCE ROUTES ==========
@admin_blueprint.route("/appearance/colors", methods=["GET", "POST"])
def general_appearance():
    if request.method == "POST":
        logger.info("General appearance settings updated")

        with open("static/css/root.css", "r") as file:
            css_content = file.read()

        for key, value in request.form.items():
            pattern = rf"--{key}:\s*[^;]+;"

            replacement = f"--{key}: {value};"
            if re.search(pattern, css_content):
                css_content = re.sub(pattern, replacement, css_content)
            else:
                css_content += f"\n{replacement}"

        with open("static/css/root.css", "w") as file:
            file.write(css_content)

        return redirect(url_for("admin.general_appearance"))

    logger.info("General appearance route accessed")
    with open("static/css/root.css") as file:
        content: str = file.read()

    root_styles = {}
    root_regex = r"--([a-zA-Z0-9-]+)\s*:\s*([^;]+);"
    matches = re.findall(root_regex, content)
    for match in matches:
        root_styles[f"{str(match[0])}"] = str(match[1]).strip()

    logger.debug("Rendering general appearance settings page")
    return render_template("admin/appearance.jinja", styles=root_styles)

@admin_blueprint.route("/appearance/templates", methods=["GET", "POST"])
def template_appearance():
    logger.info("Edit Templates route accessed")
    return render_template("admin/edit-templates.jinja")

@admin_blueprint.route("/appearance/templates/edit/<path:template>", methods=["GET", "POST"])
def template_appearance_edit(template):
    logger.info("Edit Templates route accessed")
    template_path = os.path.join(app.root_path, "templates", f"{template}")

    if request.method == "POST":
        new_content = request.form.get("template_content", "")
        with open(template_path, "w", encoding="utf-8") as file:
            file.write(new_content)

            template = app.jinja_env.get_template(sanitize_path(template))
            template.environment.cache.clear()
        logger.info("Template file saved successfully")
        return redirect(url_for("admin.template_appearance_edit", template=template))

    with open(template_path, "r", encoding="utf-8") as file:
        template_content = str(file.read())

    template_content = template_content.replace("<", "&lt;").replace(">", "&gt;")

    return render_template("admin/edit-template.jinja", template_content=template_content)

@admin_blueprint.route("/appearance/static", methods=["GET", "POST"])
def change_static_files():
    logger.info("Edit Static route accessed")
    return render_template("admin/edit-static.jinja")

@admin_blueprint.route("/appearance/static/edit/<path:file>", methods=["GET", "POST"])
def change_static_files_edit(file):
    logger.info("Edit Templates route accessed")
    file_path = os.path.join(app.root_path, "static", f"{file}")

    if request.method == "POST":
        new_content = request.form.get("template_content", "")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)

        logger.info("Static file saved successfully")
        return redirect(url_for("admin.template_appearance_edit", template=file))

    with open(file_path, "r", encoding="utf-8") as file:
        file_content = str(file.read())

    file_content = file_content.replace("<", "&lt;").replace(">", "&gt;")

    return render_template("admin/edit-template.jinja", template_content=file_content)