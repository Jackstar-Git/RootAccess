# ========== IMPORTS ==========
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for, abort
from flask.typing import ResponseReturnValue
from werkzeug.security import check_password_hash, generate_password_hash


from CustomFlaskClass import app
from utility.auth import AuthManager, permission_required, Permission, AuthManager
from utility.blogs import add_blog, get_item_by_id, load_blogs, update_blog, BlogPost
from utility.calendar import generate_calendar
from utility.contact import load_contacts
from utility.events import get_events
from utility.logging_utility import logger, log_with_user
from utility.converter import MarkdownConverter
from utility.projects import add_project, get_project_by_id, load_projects, update_project, Project
from utility.settings import get_settings, update_settings
from utility.analytics import get_all_analytics
from utility.quotes import load_quotes
from utility.users import User, get_user_by_username, get_user_by_id, load_users, update_user, delete_user, is_active

# ========== BLUEPRINT INITIALIZATION ==========
admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

# ========== AUTHENTICATION ROUTES ==========
@admin_blueprint.route("/login", methods=["GET", "POST"])
def login() -> ResponseReturnValue:
    if session.get("user_id"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username: str = request.form.get("username", "").strip()
        password: str = request.form.get("password", "")

        # Validate input
        if not username or not password:
            logger.warning(f"Login attempt with missing credentials from {request.remote_addr}")
            flash("Please provide both username and password.", "error")
            return render_template("admin/login.jinja")
        # Get user from users.json
        user_data: Optional[User] = get_user_by_username(username)

        if not user_data or not check_password_hash(user_data["password_hash"], password):
            logger.warning(f"Failed login attempt for user '{username}' from {request.remote_addr}")
            flash("Invalid username or password.", "error")
            return render_template("admin/login.jinja")

        if not is_active(user_data.get("id")):
            logger.warning(f"Login attempt for inactive user '{username}' from {request.remote_addr}")
            flash("This account is disabled or banned.", "error")
            return render_template("admin/login.jinja")


        session.clear()
        
        if request.form.get("remember"):
            session.permanent = True
        else:
            session.permanent = False
        
        user_id = user_data.get("id")
        # Store user info in session
        session["user_id"] = user_id
        logger.info(f"User '{username}' logged in successfully from {request.remote_addr}")
        flash(f"Welcome, {username}!", "success")
        
        # Redirect to next page or dashboard
        next_page: Optional[str] = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/login.jinja")

@admin_blueprint.route("/logout")
def logout() -> ResponseReturnValue:
    session.clear()
    return redirect(url_for("admin.login"))

# ========== DASHBOARD ROUTES ==========
@admin_blueprint.route("/dashboard")
@permission_required(Permission.SYSTEM_DASHBOARD)
def dashboard() -> ResponseReturnValue:
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

    html_note = MarkdownConverter.quick_convert(raw_note)

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
@permission_required(Permission.ANALYTICS_READ)
def analytics() -> ResponseReturnValue:
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
@permission_required(Permission.CONTACTS_READ)
def manage_contacts() -> ResponseReturnValue:
    contacts = load_contacts()
    contacts.sort(key=lambda x: x.get("time_created", 0), reverse=True)

    for c in contacts:
        c["formatted_date"] = datetime.fromtimestamp(c.get("time_created", 0)).strftime("%Y-%m-%d %H:%M")

    return render_template("admin/contacts.jinja", contacts=contacts)

# ========== USER ROUTES ==========
@admin_blueprint.route("/users/all", methods=["GET"])
@permission_required(Permission.USERS_READ)
def all_users() -> ResponseReturnValue:
    search_query: str = request.args.get("search", "").lower()
    hierarchy_query: str = request.args.get("hierarchy", "all")
    sort_query: str = request.args.get("sort", "name-asc")

    # Load all users using the new function
    all_users = load_users()

    display_users: List[User] = []
    for user in all_users:
        if hierarchy_query != "all":
            try:
                if "-" in hierarchy_query:
                    # Handle range (e.g., "1-3")
                    min_level, max_level = map(int, hierarchy_query.split("-"))
                    if not (min_level <= user.get("hierarchy_level") <= max_level):
                        continue
                elif "," in hierarchy_query:
                    # Handle comma-separated list (e.g., "1,2,3")
                    levels = list(map(int, hierarchy_query.split(",")))
                    if user.get("hierarchy_level")  not in levels:
                        continue
                else:
                    # Handle single number (e.g., "1")
                    if int(hierarchy_query) != user.get("hierarchy_level"):
                        continue
            except (ValueError, IndexError):
                pass

        # Filter by search query
        if search_query and search_query not in str(user.get("username")).lower():
            continue

        display_users.append(user)

    # Sort Results
    if sort_query == "hierarchy-asc":
        display_users.sort(key=lambda x: x["hierarchy_level"])
    elif sort_query == "hierarchy-desc":
        display_users.sort(key=lambda x: x["hierarchy_level"], reverse=True)
    elif sort_query == "name-desc":
        display_users.sort(key=lambda x: x["username"].lower(), reverse=True)
    elif sort_query == "created-asc":
        display_users.sort(key=lambda x: x["time_created"])
    elif sort_query == "created-desc":
        display_users.sort(key=lambda x: x["time_created"], reverse=True)
    else:  # Default: name-asc
        display_users.sort(key=lambda x: x["username"].lower())

    return render_template(
        "admin/all-users.jinja",
        users=display_users,
        query_params=request.args
    )

@admin_blueprint.route("/users/edit/<user_id>", methods=["GET", "POST"])
@permission_required(Permission.USERS_UPDATE)
def edit_user(user_id: str) -> ResponseReturnValue:
    current_user = get_user_by_id(session.get("user_id"))
    if not current_user:
        return redirect(url_for("admin.login"))

    target_user = get_user_by_id(user_id)
    if not target_user:
        flash("User not found.", "error")
        return redirect(url_for("admin.all_users"))

    current_user_hierarchy = current_user.get("hierarchy_level", 99)
    current_user_permissions = current_user.get("permissions", 0)
    target_user_hierarchy = target_user.get("hierarchy_level", 99)
    is_root: bool = AuthManager.has_permission(current_user["id"], Permission.SYSTEM_ROOT)

    # Non-root users cannot edit users with equal or higher hierarchy (lower number = higher hierarchy)
    if not is_root and current_user_hierarchy >= target_user_hierarchy:
        abort(403)

    # Generate permissions list for the template
    permissions_list = [
        ("Blogs: Read", Permission.BLOGS_READ),
        ("Blogs: Create", Permission.BLOGS_CREATE),
        ("Blogs: Update Own", Permission.BLOGS_UPDATE_OWN),
        ("Blogs: Update All", Permission.BLOGS_UPDATE),
        ("Blogs: Delete Own", Permission.BLOGS_DELETE_OWN),
        ("Blogs: Delete All", Permission.BLOGS_DELETE),
        ("Projects: Read", Permission.PROJECTS_READ),
        ("Projects: Create", Permission.PROJECTS_CREATE),
        ("Projects: Update", Permission.PROJECTS_UPDATE),
        ("Media: Read", Permission.MEDIA_READ),
        ("Media: Create", Permission.MEDIA_CREATE),
        ("Media: Update", Permission.MEDIA_UPDATE),
        ("Media: Delete", Permission.MEDIA_DELETE),
        ("Interactions: Manage", Permission.INTERACTIONS_MANAGE),
        ("Contacts: Read", Permission.CONTACTS_READ),
        ("Contacts: Update", Permission.CONTACTS_UPDATE),
        ("Quotes: Read", Permission.QUOTES_READ),
        ("Quotes: Create", Permission.QUOTES_CREATE),
        ("Quotes: Update", Permission.QUOTES_UPDATE),
        ("Notes: Update", Permission.NOTES_UPDATE),
        ("Events: Read", Permission.EVENTS_READ),
        ("Events: Create", Permission.EVENTS_CREATE),
        ("Events: Update", Permission.EVENTS_UPDATE),
        ("Events: Delete", Permission.EVENTS_DELETE),
        ("Analytics: Read", Permission.ANALYTICS_READ),
        ("Analytics: Update", Permission.ANALYTICS_UPDATE),
        ("Users: Read", Permission.USERS_READ),
        ("Users: Create", Permission.USERS_CREATE),
        ("Users: Update", Permission.USERS_UPDATE),
        ("Users: Delete", Permission.USERS_DELETE),
        ("System: Dashboard", Permission.SYSTEM_DASHBOARD),
        ("System: Settings", Permission.SYSTEM_SETTINGS),
        ("System: Admin", Permission.SYSTEM_ADMIN),
        ("System: Root", Permission.SYSTEM_ROOT),
    ]

    if request.method == "POST":
        # Get form data
        username = request.form.get("username", target_user["username"])
        hierarchy_level = int(request.form.get("hierarchy_level", target_user["hierarchy_level"]))
        profile_picture_url = target_user.get("profile_picture_url", "")
        
        # Extract new status and notes fields from form payload
        status = request.form.get("status", target_user.get("status", "Aktiv"))
        notes = request.form.get("notes", target_user.get("notes", ""))

        selected_permissions = 0
        for  _ , perm_value in permissions_list:
            if request.form.get(f"perm_{perm_value}"):
                selected_permissions |= perm_value

        profile_pic_file = request.files.get("profile_picture")
        if profile_pic_file and profile_pic_file.filename:
            upload_folder = "uploads/users"
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{int(time.time())}_{profile_pic_file.filename}"
            profile_pic_file.save(os.path.join(upload_folder, filename))
            profile_picture_url = f"/uploads/users/{filename}"

        if hierarchy_level <= current_user_hierarchy:
            flash("Cannot set hierarchy to a level higher than or equal to your own.", "error")
            return render_template(
                "admin/edit-user.jinja",
                max_hierarchy=current_user_hierarchy + 1 if not is_root else 0,
                user=target_user,
                permissions_list=permissions_list,
                current_user=current_user
            )

        # Validate permissions: can only grant permissions you have (unless root)
        if not is_root and (selected_permissions & ~current_user_permissions) != 0:
            flash("Cannot grant permissions you do not have.", "error")
            return render_template(
                "admin/edit-user.jinja",
                max_hierarchy=current_user_hierarchy + 1 if not is_root else 0,
                user=target_user,
                permissions_list=permissions_list,
                current_user=current_user
            )

        updated_data = {
            "username": username,
            "hierarchy_level": hierarchy_level,
            "permissions": selected_permissions,
            "profile_picture_url": profile_picture_url,
            "status": status,
            "notes": notes,
        }

        if update_user(user_id, updated_data):
            log_with_user("info", f"User updated successfully | Target User ID: {user_id} | Username: {username} | Status: {status}", session.get("user_id"))
            flash("User updated successfully!", "success")
            return redirect(url_for("admin.all_users"))

    # GET request: render the form
    return render_template(
        "admin/edit-user.jinja",
        max_hierarchy=current_user_hierarchy + 1 if not is_root else 0,
        user=target_user,
        permissions_list=permissions_list,
        current_user=current_user
    )

@admin_blueprint.route("/users/delete/<user_id>", methods=["POST"])
@permission_required(Permission.USERS_DELETE)
def delete_user_route(user_id: str) -> ResponseReturnValue:
    current_user_id: Optional[str] = session.get("user_id")
    current_user = get_user_by_id(current_user_id) if current_user_id else None
    
    if not current_user:
        log_with_user("warning", f"Delete user attempt with invalid session", current_user_id)
        return {"success": False, "message": "Unauthorized"}, 401

    target_user = get_user_by_id(user_id)
    if not target_user:
        log_with_user("warning", f"Attempted to delete non-existent user | Target User ID: {user_id}", current_user_id)
        return {"success": False, "message": "User not found"}, 404

    current_user_hierarchy = current_user.get("hierarchy_level", 1)
    target_user_hierarchy = target_user.get("hierarchy_level", 1)
    is_root = (current_user.get("permissions", 0) & Permission.SYSTEM_ROOT) == Permission.SYSTEM_ROOT

    # Non-root users cannot delete users with equal or higher hierarchy
    if not is_root and current_user_hierarchy >= target_user_hierarchy:
        log_with_user("warning", f"Insufficient permissions to delete user | Target User ID: {user_id}", current_user_id)
        return {"success": False, "message": "Cannot delete users with equal or higher hierarchy."}, 403

    if delete_user(user_id):
        log_with_user("info", f"User deleted successfully | Deleted User ID: {user_id}", current_user_id)
        return {"success": True, "message": "User deleted successfully"}
    
    log_with_user("error", f"Failed to delete user | User ID: {user_id}", current_user_id)
    return {"success": False, "message": "Failed to delete user"}, 500





# ========== MEDIA ROUTES ==========
@admin_blueprint.route("/media/all", methods=["GET"])
@permission_required(Permission.MEDIA_READ)
def library() -> ResponseReturnValue:
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
@permission_required(Permission.SYSTEM_ADMIN)
def server_logs() -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    log_with_user("info", "Accessed server logs", user_id)
    with open("logs/app.log", "r", encoding="utf-8") as f:
        lines: List[str] = f.readlines()

    clean_lines: List[str] = lines[-50::]
    log_with_user("debug", "Rendered server logs page", user_id)
    return render_template("admin/logs.jinja", logs=clean_lines)

# ========== BLOGS ROUTES ==========
@admin_blueprint.route("/blogs/all", methods=["GET"])
@permission_required(Permission.BLOGS_READ)
def all_blogs() -> ResponseReturnValue:
    search_query: str = request.args.get("search", "").lower()
    topic_query: str = request.args.get("topic", "all")

    raw_blogs = load_blogs()

    display_blogs: List[BlogPost] = []

    for blog in raw_blogs:
        if topic_query != "all" and topic_query not in blog.get("categories", []):
            continue

        if search_query:
            title_match: bool = search_query in blog.get("title", "").lower()
            author_match: bool = any(search_query in a.lower() for a in blog.get("authors", []))
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
@permission_required(Permission.BLOGS_READ)
def blogs_categories() -> ResponseReturnValue:
    return render_template("admin/blog-settings.jinja", settings=get_settings("blog_config"))

@admin_blueprint.route("/blogs/create/", methods=["GET", "POST"])
@permission_required(Permission.BLOGS_CREATE)
def create_blog() -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    log_with_user("info", "Accessing blog creation portal", user_id)

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

        # Handle scheduled publish date
        if blog_data["status"] == "draft":
            scheduled_date = request.form.get("scheduled_date")
            scheduled_time = request.form.get("scheduled_time", "00:00")
            
            if scheduled_date:
                try:
                    # Combine date and time, convert to timestamp
                    datetime_str = f"{scheduled_date} {scheduled_time}"
                    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                    scheduled_timestamp = int(dt.timestamp())
                    
                    # Validate that scheduled time is in the future
                    if scheduled_timestamp > int(time.time()):
                        blog_data["scheduled_date"] = scheduled_timestamp
                    else:
                        flash("Scheduled date/time must be in the future.", "error")
                        return render_template(
                            "admin/add-blog.jinja",
                            settings=get_settings("blog_config")
                        )
                except ValueError as e:
                    logger.error(f"Invalid scheduled date format: {str(e)}")
                    flash("Invalid scheduled date/time format.", "error")
                    return render_template(
                        "admin/add-blog.jinja",
                        settings=get_settings("blog_config")
                    )

        try:
            add_blog(blog_data)
            log_with_user("info", f'Blog "{blog_data["title"]}" created successfully', user_id)
            flash("Blog post published!", "success")
            return redirect(url_for("admin.all_blogs"))
        except Exception as e:
            log_with_user("error", f"Failed to save blog: {str(e)}", user_id)
            flash("Error saving blog post.", "error")

    return render_template(
        "admin/add-blog.jinja",
        settings=get_settings("blog_config")
    )

@admin_blueprint.route("/blogs/edit/<blog_id>", methods=["GET", "POST"])
@permission_required(Permission.BLOGS_UPDATE)
def edit_blog(blog_id: str) -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    blog = get_item_by_id(blog_id)

    if not blog:
        log_with_user("warning", f"Attempted to edit non-existent blog | Blog ID: {blog_id}", user_id)
        flash("Post not found.", "error")
        return redirect(url_for("admin.all_blogs"))

    if request.method == "POST":
        thumbnail_file = request.files.get("thumbnail")
        image_url = blog.get("image_url")

        if thumbnail_file and thumbnail_file.filename:
            upload_folder = "uploads/blogs"
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{int(time.time())}_{thumbnail_file.filename}"
            thumbnail_file.save(os.path.join(upload_folder, filename))
            image_url = f"/uploads/blogs/{filename}"

        updated_data = {
            "authors": request.form.getlist("authors[]"),
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

        # Handle scheduled publish date
        if updated_data["status"] == "draft":
            scheduled_date = request.form.get("scheduled_date")
            scheduled_time = request.form.get("scheduled_time", "00:00")
            
            if scheduled_date:
                try:
                    # Combine date and time, convert to timestamp
                    datetime_str = f"{scheduled_date} {scheduled_time}"
                    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                    scheduled_timestamp = int(dt.timestamp())
                    
                    # Validate that scheduled time is in the future
                    if scheduled_timestamp > int(time.time()):
                        updated_data["scheduled_date"] = scheduled_timestamp
                    else:
                        flash("Scheduled date/time must be in the future.", "error")
                        return render_template(
                            "admin/edit-blog.jinja",
                            blog=blog,
                            settings=get_settings("blog_config")
                        )
                except ValueError as e:
                    logger.error(f"Invalid scheduled date format: {str(e)}")
                    flash("Invalid scheduled date/time format.", "error")
                    return render_template(
                        "admin/edit-blog.jinja",
                        blog=blog,
                        settings=get_settings("blog_config")
                    )
            elif blog.get("scheduled_date"):
                # If draft but no new schedule, remove old schedule
                updated_data["scheduled_date"] = None
        else:
            # If not draft, remove scheduled_date
            updated_data["scheduled_date"] = None

        if update_blog(blog_id, updated_data):
            log_with_user("info", f"Blog updated successfully | Blog ID: {blog_id} | Title: {updated_data.get('title')}", user_id)
            flash("Successfully updated!", "success")
            return redirect(url_for("admin.all_blogs"))
        else:
            log_with_user("error", f"Failed to update blog | Blog ID: {blog_id}", user_id)

    return render_template(
        "admin/edit-blog.jinja",
        blog=blog,
        settings=get_settings("blog_config")
    )

# ========== PROJECTS ROUTES ==========
@admin_blueprint.route("/projects/all", methods=["GET"])
@permission_required(Permission.PROJECTS_READ)
def all_projects() -> ResponseReturnValue:
    search_query: str = request.args.get("search", "").lower()
    topic_query: str = request.args.get("topic", "all")

    raw_projects = load_projects()
    display_projects: List[Project] = []

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
@permission_required(Permission.PROJECTS_CREATE)
def create_project() -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    log_with_user("info", "Accessing project creation portal", user_id)

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
            log_with_user("info", f"Project created successfully | Project: {project_data['title']}", user_id)
            flash("Project published!", "success")
            return redirect(url_for("admin.all_projects"))
        except Exception as e:
            log_with_user("error", f"Failed to save project | Error: {str(e)}", user_id)
            flash("Error saving project.", "error")

    return render_template("admin/add-project.jinja", settings=get_settings("project_config"))

@admin_blueprint.route("/projects/edit/<project_id>", methods=["GET", "POST"])
@permission_required(Permission.PROJECTS_UPDATE)
def edit_project(project_id: str) -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    project = get_project_by_id(project_id)

    if not project:
        log_with_user("warning", f"Attempted to edit non-existent project | Project ID: {project_id}", user_id)
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
            log_with_user("info", f"Project updated successfully | Project ID: {project_id} | Title: {updated_data.get('title')}", user_id)
            flash("Successfully updated!", "success")
            return redirect(url_for("admin.all_projects"))
        else:
            log_with_user("error", f"Failed to update project | Project ID: {project_id}", user_id)

    return render_template("admin/edit-project.jinja", project=project, settings=get_settings("project_config"))

# ========== CONTENT ROUTES ==========
@admin_blueprint.route("/content/quotes", methods=["GET"])
@permission_required(Permission.QUOTES_READ)
def manage_quotes() -> ResponseReturnValue:
    quotes = load_quotes()
    return render_template("admin/quotes.jinja", quotes=quotes)

# ========== SETTINGS ROUTES ==========
@admin_blueprint.route("/settings/server", methods=["GET", "POST"])
@permission_required(Permission.SYSTEM_ADMIN)
def server_settings() -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    
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

            with open("robots.txt", "w") as f:
                f.write(form_data.get("robots_txt", "").replace("\n", ""))

            update_settings(settings)
            log_with_user("info", "Server settings updated successfully", user_id)
            return jsonify({"success": True, "message": "Settings updated successfully"})
        except Exception as e:
            log_with_user("error", f"Failed to update server settings | Error: {str(e)}", user_id)
            return jsonify({"success": False, "message": str(e)}), 400

    robots = ""
    with open("robots.txt", "r") as f:
        robots = f.read()

    settings = get_settings() or {}
    return render_template("admin/server-settings.jinja",
                           settings=settings,
                           server_config=settings.get("server_config", {}),
                           robots_txt=robots)

@admin_blueprint.route("/settings/general", methods=["GET", "POST"])
@permission_required(Permission.SYSTEM_ADMIN)
def general_settings() -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    
    if request.method == "POST":
        try:
            settings = get_settings() or {}
            form_data = request.form.to_dict()

            settings["site_name"] = form_data.get("site_name", "")
            settings["site_description"] = form_data.get("site_description", "")
            settings["timezone"] = form_data.get("timezone", "UTC")

            update_settings(settings)
            log_with_user("info", "General settings updated successfully", user_id)
            return jsonify({"success": True, "message": "Settings updated successfully"})
        except Exception as e:
            log_with_user("error", f"Failed to update general settings | Error: {str(e)}", user_id)
            return jsonify({"success": False, "message": str(e)}), 400

    settings = get_settings() or {}
    return render_template("admin/general-settings.jinja", settings=settings)

# ========== APPEARANCE ROUTES ==========
@admin_blueprint.route("/appearance/colors", methods=["GET", "POST"])
@permission_required(Permission.SYSTEM_ADMIN)
def general_appearance() -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    
    if request.method == "POST":
        log_with_user("info", "General appearance settings updated", user_id)

        with open("static/css/root.css", "r") as f:
            css_content = f.read()

        for key, value in request.form.items():
            pattern = rf"--{key}:\s*[^;]+;"

            replacement = f"--{key}: {value};"
            if re.search(pattern, css_content):
                css_content = re.sub(pattern, replacement, css_content)
            else:
                css_content += f"\n{replacement}"

        with open("static/css/root.css", "w") as f:
            f.write(css_content)

        return redirect(url_for("admin.general_appearance"))

    log_with_user("info", "General appearance route accessed", user_id)
    with open("static/css/root.css") as f:
        content: str = f.read()

    root_styles = {}
    root_regex = r"--([a-zA-Z0-9-]+)\s*:\s*([^;]+);"
    matches = re.findall(root_regex, content)
    for match in matches:
        root_styles[f"{str(match[0])}"] = str(match[1]).strip()

    log_with_user("debug", "Rendering general appearance settings page", user_id)
    return render_template("admin/appearance.jinja", styles=root_styles)

@admin_blueprint.route("/appearance/templates", methods=["GET", "POST"])
@permission_required(Permission.SYSTEM_ADMIN)
def template_appearance() -> ResponseReturnValue:
    logger.info("Edit Templates route accessed")
    return render_template("admin/edit-templates.jinja")

@admin_blueprint.route("/appearance/templates/edit/<path:template>", methods=["GET", "POST"])
@permission_required(Permission.SYSTEM_ADMIN)
def template_appearance_edit(template: str) -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    log_with_user("info", f"Edit Template route accessed | Template: {template}", user_id)
    template_path = os.path.join(app.root_path, "templates", f"{template}")

    if request.method == "POST":
        new_content = request.form.get("template_content", "")
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(new_content)

            # Renamed variable to prevent shadowing argument 'template'
            #jinja_template = app.jinja_env.get_template(sanitize_path(template))
            #jinja_template.environment.cache.clear()
        log_with_user("info", f"Template file saved successfully | Template: {template}", user_id)
        return redirect(url_for("admin.template_appearance_edit", template=template))

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = str(f.read())

    template_content = template_content.replace("<", "&lt;").replace(">", "&gt;")

    return render_template("admin/edit-template.jinja", template_content=template_content)

@admin_blueprint.route("/appearance/static", methods=["GET", "POST"])
@permission_required(Permission.SYSTEM_ADMIN)
def change_static_files() -> ResponseReturnValue:
    logger.info("Edit Static route accessed")
    return render_template("admin/edit-static.jinja")

@admin_blueprint.route("/appearance/static/edit/<path:file>", methods=["GET", "POST"])
@permission_required(Permission.SYSTEM_ADMIN)
def change_static_files_edit(file: str) -> ResponseReturnValue:
    user_id: Optional[str] = session.get("user_id")
    log_with_user("info", f"Edit Static File route accessed | File: {file}", user_id)
    file_path = os.path.join(app.root_path, "static", f"{file}")

    if request.method == "POST":
        new_content = request.form.get("template_content", "")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        log_with_user("info", f"Static file saved successfully | File: {file}", user_id)
        return redirect(url_for("admin.template_appearance_edit", template=file))

    with open(file_path, "r", encoding="utf-8") as f:
        file_content = str(f.read())

    file_content = file_content.replace("<", "&lt;").replace(">", "&gt;")

    return render_template("admin/edit-template.jinja", template_content=file_content)