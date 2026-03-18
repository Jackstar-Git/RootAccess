# ========== IMPORTS ==========
import io
import os
import platform
import shutil
import subprocess
import time
import zipfile
from typing import Tuple, Union

from flask import Blueprint, jsonify, request, session, abort, send_file, Response, redirect, url_for, flash
import psutil

from CustomFlaskClass import app
from utility.auth import login_required
from utility.blogs import add_blog, delete_blog, update_blog, load_blogs, get_item_by_id
from utility.calendar import generate_calendar
from utility.contact import add_contact, delete_contact, mark_contact_read
from utility.events import get_events, add_event, delete_event
from utility.logging_utility import logger
from utility.others import convert_markdown_to_html
from utility.path_files import MAX_FILE_SIZE, ROOT_DIR, is_safe_path, sanitize_filename
from utility.projects import query_projects, search_projects, load_projects, get_project_by_id
from utility.settings import get_settings, update_settings, _load_settings, _load_settings_cached

# ========== BLUEPRINT INITIALIZATION ==========
internal_blueprint = Blueprint("internal", __name__, template_folder="./templates")

# ========== FILE HANDLING ROUTES ==========
@internal_blueprint.route("/uploads/<path:filename>", methods=["GET"])
def uploads(filename: str) -> Response:
    logger.info(f"GET request received for serving file from uploads | Filename: {filename}")
    try:
        return send_file(os.path.join(app.root_path, "uploads", filename))
    except Exception as e:
        logger.error(f"Error serving file from uploads | Filename: {filename} | Error: {str(e)}")
        abort(404)

@internal_blueprint.route("/plugins/<path:filename>", methods=["GET"])
def plugins(filename: str) -> Response:
    logger.info(f"GET request received for serving file from plugins | Filename: {filename}")
    try:
        return send_file(os.path.join(app.root_path, "plugins", filename))
    except Exception as e:
        logger.error(f"Error serving file from plugins | Filename: {filename} | Error: {str(e)}")
        abort(404)

@internal_blueprint.route("/download/<path:filepath>", methods=["GET"])
def download(filepath: str) -> Response:
    logger.info(f"GET request received for download | Path: {filepath}")
    is_public_path = filepath.startswith("uploads/")
    is_admin = session.get("is_admin", False)

    if not is_public_path and not is_admin:
        logger.warning(f"Unauthorized download attempt to restricted path: {filepath}")
        return abort(403)

    full_path = os.path.join(app.root_path, filepath)

    if filepath == "all":
        full_path = os.path.join(app.root_path)

    if not os.path.exists(full_path):
        logger.error(f"File or directory not found | Path: {full_path}")
        abort(404, description="File or directory not found.")

    if os.path.isfile(full_path):
        logger.info(f"Serving file | Path: {full_path}")
        return send_file(full_path, as_attachment=True)

    if os.path.isdir(full_path):
        logger.info(f"Creating zip for directory | Path: {full_path}")
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(full_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(full_path))
                    zipf.write(file_path, arcname)

        memory_file.seek(0)
        zip_filename = f"{os.path.basename(filepath)}.zip"
        return send_file(
            memory_file,
            as_attachment=True,
            download_name=zip_filename,
            mimetype="application/zip"
        )

    logger.error(f"Invalid path provided | Path: {filepath}")
    abort(400, description="Invalid path provided.")

# ========== CONTACT ROUTES ==========
@internal_blueprint.route("/api/contact", methods=["POST"])
def api_contact_submit() -> Response:
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    topic = request.form.get("topic", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if not all([name, email, topic, subject, message]):
        flash("All fields are required.", "error")
        return redirect(request.referrer or "/")

    attachments = []
    if "attachments" in request.files:
        files = request.files.getlist("attachments")
        upload_dir = os.path.join(app.root_path, "uploads", "contacts")
        os.makedirs(upload_dir, exist_ok=True)

        for file in files:
            if file and file.filename:
                filename = sanitize_filename(f"{int(time.time())}_{file.filename}")
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                attachments.append(f"/uploads/contacts/{filename}")

    contact_data = {
        "name": name,
        "email": email,
        "topic": topic,
        "subject": subject,
        "message": message,
        "attachments": attachments
    }

    try:
        add_contact(contact_data)
        flash("Your message has been sent successfully!", "success")
    except Exception as e:
        logger.error(f"Failed to save contact request: {e}")
        flash("Failed to send message. Please try again later.", "error")

    return redirect(request.referrer or "/")

@internal_blueprint.route("/api/admin/contacts/<action>", methods=["POST"])
@login_required
def api_admin_contacts(action: str) -> Response:
    data = request.get_json()
    contact_id = data.get("id")

    if not contact_id:
        return jsonify({"error": "Missing contact ID"}), 400

    try:
        if action == "delete":
            success = delete_contact(contact_id)
        elif action == "read":
            success = mark_contact_read(contact_id)
        else:
            return jsonify({"error": "Invalid action"}), 400

        if success:
            return jsonify({"success": True})
        return jsonify({"error": "Action failed or item not found"}), 404
    except Exception as e:
        logger.error(f"Failed to process contact action ({action}): {e}")
        return jsonify({"error": "Internal server error"}), 500

# ========== EVENTS ROUTES ==========
@internal_blueprint.route("/api/add-events/", methods=["POST"])
@login_required
def add_events() -> Union[Response, Tuple[Response, int]]:
    logger.info("Received POST request for adding events")

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400

    required_fields = {"year", "month", "day", "name", "description"}
    missing_fields = required_fields - set(data.keys())
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        year = int(data["year"])
        month = int(data["month"])
        day = int(data["day"])

        if not 1 <= month <= 12:
            return jsonify({"error": "Month must be between 1 and 12"}), 400
        if not 1 <= day <= 31:
            return jsonify({"error": "Day must be between 1 and 31"}), 400

        if month in [4, 6, 9, 11] and day > 30:
            return jsonify({"error": "This month only has 30 days"}), 400
        elif month == 2:
            if not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) and day > 28:
                return jsonify({"error": "February only has 28 days in non-leap years"}), 400
            elif day > 29:
                return jsonify({"error": "February only has 29 days in leap years"}), 400

    except ValueError:
        return jsonify({"error": "Year, month, and day must be integers"}), 400

    new_event = {
        "year": year,
        "month": month,
        "day": day,
        "name": data["name"].strip(),
        "description": data["description"].strip(),
    }

    try:
        added = add_event(new_event)
        return jsonify({
            "message": "Event added successfully",
            "event": added
        }), 201
    except Exception as e:
        logger.error(f"Failed to add event | Error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@internal_blueprint.route("/api/get-events/", methods=["GET"])
@login_required
def api_get_events() -> Response:
    try:
        year = request.args.get("year", type=int)
        month = request.args.get("month", type=int)
        day = request.args.get("day", type=int)

        all_events = get_events()
        filtered = [
            e for e in all_events
            if e.get("year") == year and e.get("month") == month and e.get("day") == day
        ]
        return jsonify(filtered)
    except Exception as e:
        logger.error(f"Failed to fetch events: {e}")
        return jsonify({"error": "Internal server error"}), 500

@internal_blueprint.route("/api/delete-event", methods=["GET"])
@login_required
def api_delete_event() -> Response:
    event_id = request.args.get("id")
    if event_id:
        try:
            delete_event(event_id)
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")

    return redirect(request.referrer or url_for("admin.dashboard"))

# ========== NOTES ROUTES ==========
@internal_blueprint.route("/api/save-note", methods=["POST"])
@login_required
def api_save_note() -> Response:
    data = request.get_json()
    if not data or "note" not in data:
        return jsonify({"error": "No note content provided."}), 400

    note_content = data["note"]
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/notes.md", "w", encoding="utf-8") as f:
            f.write(note_content)

        html_content = convert_markdown_to_html(note_content)
        return jsonify({"success": True, "html": html_content})
    except Exception as e:
        logger.error(f"Failed to save note: {e}")
        return jsonify({"error": "Internal server error"}), 500

# ========== SYSTEM ROUTES ==========
@internal_blueprint.route("/api/get-system-info/", methods=["GET"])
@login_required
def get_system_info() -> Union[Response, Tuple[Response, int]]:
    logger.info("Received GET request for system information")

    try:
        memory_info = psutil.virtual_memory()
        ram_usage = {
            "total": round(memory_info.total / (1024 ** 3), 2),
            "used": round(memory_info.used / (1024 ** 3), 2),
            "percentage": memory_info.percent
        }

        disk_info = psutil.disk_usage("/")
        disk_usage = {
            "total": round(disk_info.total / (1024 ** 3), 2),
            "used": round(disk_info.used / (1024 ** 3), 2),
            "percentage": disk_info.percent
        }

        cpu_usage = {
            "percentage": psutil.cpu_percent(interval=1)
        }

        return jsonify({
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "disk_usage": disk_usage
        })

    except Exception as e:
        logger.error(f"Failed to retrieve system information: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# ========== FILE MANAGEMENT ROUTES ==========
@internal_blueprint.route("/api/files/upload", methods=["POST"])
@login_required
def upload_file() -> Response:
    directory = request.args.get("dir", "").lstrip("/")
    root_dir = request.args.get("root", ROOT_DIR).lstrip("/")

    if "files[]" not in request.files:
        return jsonify({"error": "No files in request"}), 400

    files = request.files.getlist("files[]")
    if not files:
        return jsonify({"error": "No selected files"}), 400

    base_path = os.path.join(app.root_path, root_dir, directory)
    if not is_safe_path(os.path.join(app.root_path, root_dir), base_path):
        return jsonify({"error": "Invalid path"}), 400

    uploaded_files = []
    errors = []

    for file in files:
        if file.content_length > MAX_FILE_SIZE:
            errors.append(f"{file.filename}: File too large")
            continue

        filename = sanitize_filename(file.filename)
        file_path = os.path.join(base_path, filename)

        counter = 1
        while os.path.exists(file_path):
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{counter}{ext}"
            file_path = os.path.join(base_path, filename)
            counter += 1

        try:
            os.makedirs(base_path, exist_ok=True)
            file.save(file_path)
            uploaded_files.append({
                "filename": filename,
                "path": file_path,
                "size": file.content_length
            })
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    response = {"uploaded": uploaded_files}
    if errors:
        response["errors"] = errors
    return jsonify(response)

@internal_blueprint.route("/api/files/delete", methods=["DELETE"])
@login_required
def delete_files() -> Response:
    data = request.get_json()
    if not data or "files" not in data or "path" not in data:
        return jsonify({"error": "Invalid request"}), 400

    path = data["path"].lstrip("/")
    root_dir = data.get("root", ROOT_DIR).lstrip("/")
    files = data["files"]

    if not isinstance(files, list):
        return jsonify({"error": "Files must be an array"}), 400

    base_path = os.path.join(app.root_path, root_dir, path)
    if not is_safe_path(os.path.join(app.root_path, root_dir), base_path):
        return jsonify({"error": "Invalid path"}), 400

    errors = []
    deleted = []

    for filename in files:
        file_path = os.path.join(base_path, filename)
        try:
            if not os.path.exists(file_path):
                errors.append(f"{filename}: Not found")
                continue

            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)

            deleted.append(filename)
        except Exception as e:
            errors.append(f"{filename}: {str(e)}")

    response = {"deleted": deleted}
    if errors:
        response["errors"] = errors
    return jsonify(response)

@internal_blueprint.route("/api/files/rename", methods=["POST"])
@login_required
def rename_file() -> Response:
    data = request.get_json()
    required = ["path", "name", "new_name"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    path = data["path"].lstrip("/")
    old_name = data["name"].lstrip("/")
    new_name = sanitize_filename(data["new_name"].lstrip("/"))
    root_dir = data.get("root", ROOT_DIR).lstrip("/")

    base_path = os.path.join(app.root_path, root_dir, path)
    old_path = os.path.join(base_path, old_name)
    new_path = os.path.join(base_path, new_name)

    if not is_safe_path(os.path.join(app.root_path, root_dir), base_path) or not is_safe_path(os.path.join(app.root_path, root_dir), new_path):
        return jsonify({"error": "Invalid path"}), 400

    if not os.path.exists(old_path):
        return jsonify({"error": "File not found"}), 404

    if os.path.exists(new_path):
        return jsonify({"error": "Destination exists"}), 409

    try:
        os.rename(old_path, new_path)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@internal_blueprint.route("/api/files/copy", methods=["POST"])
@login_required
def copy_file() -> Response:
    data = request.get_json()
    required = ["path", "file_name", "new_path"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    path = data["path"].lstrip("/")
    file_name = data["file_name"].lstrip("/")
    new_path = data["new_path"].lstrip("/")
    root_dir = data.get("root", ROOT_DIR).lstrip("/")

    source = os.path.join(app.root_path, root_dir, path, file_name)
    destination = os.path.join(app.root_path, root_dir, new_path, file_name)

    if not is_safe_path(os.path.join(app.root_path, root_dir), source) or not is_safe_path(os.path.join(app.root_path, root_dir), destination):
        return jsonify({"error": "Invalid path"}), 400

    if not os.path.exists(source):
        return jsonify({"error": "Source not found"}), 404

    if os.path.exists(destination):
        return jsonify({"error": "Destination exists"}), 409

    try:
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@internal_blueprint.route("/api/files/create_folder", methods=["POST"])
@login_required
def create_folder() -> Response:
    data = request.get_json()
    required = ["path", "folder_name"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    path = data["path"].lstrip("/")
    folder_name = sanitize_filename(data["folder_name"].lstrip("/"))
    root_dir = data.get("root", ROOT_DIR).lstrip("/")

    full_path = os.path.join(app.root_path, root_dir, path, folder_name)
    if not is_safe_path(os.path.join(app.root_path, root_dir), full_path):
        return jsonify({"error": "Invalid path"}), 400

    try:
        os.makedirs(full_path)
        return jsonify({"status": "success"}), 201
    except FileExistsError:
        return jsonify({"error": "Folder already exists"}), 409
    except Exception as e:
        logger.error(f"Failed to create folder | Path: {full_path} | Error: {str(e)}")
        return jsonify({"error": "Failed to create folder"}), 500

# ========== LOGS ROUTES ==========
@internal_blueprint.route("/api/get-logs", methods=["POST"])
@login_required
def get_logs() -> Response:
    logger.info("POST request received for getting logs")

    data = request.get_json()
    if not data:
        logger.warning("No data provided for getting logs")
        return jsonify({"error": "No data provided"}), 400

    severity: str = data.get("severityFilter", "ALL").upper()
    items_raw: int = int(data.get("itemsFilter", 500))
    sorting: str = data.get("sortingFilter", "DESC")

    log_path = "logs/app.log"

    if not os.path.exists(log_path):
        return jsonify({"logs": ["Log file not found or empty."]})

    with open(log_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    if severity != "ALL":
        filtered_lines = [line for line in lines if severity in line]
    else:
        filtered_lines = [line for line in lines if "DEBUG" not in line]

    if items_raw > 0:
        clean_lines = filtered_lines[-items_raw:]
    else:
        clean_lines = filtered_lines

    if sorting == "DESC":
        clean_lines = list(reversed(clean_lines))

    logger.info("Logs retrieved successfully")
    return jsonify({
        "logs": [line.strip() for line in clean_lines if line.strip()]
    })

@internal_blueprint.route("/api/clear-logs", methods=["POST"])
@login_required
def clear_logs() -> Response:
    logger.info("POST request received to clear logs")
    log_path = "logs/app.log"

    try:
        open(log_path, "w", encoding="utf-8").close()
        logger.info("Log file truncated successfully")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Failed to clear logs: {e}")
        return jsonify({"error": "Error occurred while clearing logs."}), 500

# ========== COMMAND ROUTES ==========
@internal_blueprint.route("/api/execute-command", methods=["POST"])
@login_required
def execute_command() -> Response:
    IS_WINDOWS = platform.system() == "Windows"

    COMMANDS_CONFIG = {
        "Windows": {
            "ping": ["ping", "google.com"],
            "uptime": ["net", "stats", "workstation"],
            "disk": ["wmic", "logicaldisk", "get", "caption,size,freespace"],
            "memory": ["systeminfo"],
            "cpu": ["wmic", "cpu", "get", "loadpercentage"],
            "ip": ["ipconfig", "/all"],
            "ls": ["dir"]
        },
        "Linux": {
            "ping": ["ping", "-c", "4", "google.com"],
            "uptime": ["uptime", "-p"],
            "disk": ["df", "-h"],
            "memory": ["free", "-m"],
            "cpu": ["top", "-bn1"],
            "ip": ["ip", "addr"],
            "ls": ["ls", "-la"]
        }
    }

    data = request.get_json()
    command_key = data.get("command", "").strip().lower()
    password_input = data.get("consolePassword", "")

    if password_input != "1234":
        return jsonify({"output": "Unauthorized: Incorrect Console Password.", "status": "error"}), 403

    os_type = "Windows" if IS_WINDOWS else "Linux"
    available_cmds = COMMANDS_CONFIG[os_type]

    if command_key == "help":
        cmd_list = ", ".join(available_cmds.keys())
        return jsonify({"output": f"Available commands ({os_type}): {cmd_list}, help", "status": "success"})

    if command_key not in available_cmds:
        return jsonify({"output": f"Command '{command_key}' not permitted or unknown for {os_type}.", "status": "error"}), 400

    try:
        result = subprocess.run(
            available_cmds[command_key],
            capture_output=True,
            text=True,
            timeout=15,
            encoding="utf-8",
            errors="replace",
            shell=IS_WINDOWS
        )

        output = result.stdout if result.stdout else result.stderr
        return jsonify({"output": output, "status": "success"})

    except Exception as e:
        return jsonify({"output": f"Execution Error: {str(e)}", "status": "error"}), 500

# ========== BLOGS ROUTES ==========
@internal_blueprint.route("/api/add-blog", methods=["POST"])
@login_required
def api_add_blog() -> Response:
    data = request.get_json()
    if not data or not data.get("title") or not data.get("content_raw"):
        return jsonify({"error": "Title and content are required."}), 400

    try:
        new_post = add_blog(data)
        logger.info(f"New blog created: {new_post['id']}")
        return jsonify({"success": True, "id": new_post["id"]})
    except Exception as e:
        logger.error(f"Failed to add blog: {e}")
        return jsonify({"error": "Internal server error while adding blog."}), 500

@internal_blueprint.route("/api/update-blog", methods=["POST"])
@login_required
def api_update_blog() -> Response:
    data = request.get_json()
    blog_id = data.get("id")

    if not blog_id:
        return jsonify({"error": "Blog ID is required for updates."}), 400

    try:
        success = update_blog(blog_id, data)
        if success:
            logger.info(f"Blog {blog_id} updated successfully")
            return jsonify({"success": True})
        return jsonify({"error": "Blog post not found."}), 404
    except Exception as e:
        logger.error(f"Failed to update blog {blog_id}: {e}")
        return jsonify({"error": "Error occurred during update."}), 500

@internal_blueprint.route("/api/delete-blog", methods=["DELETE"])
@login_required
def api_delete_blog() -> Response:
    data = request.get_json(silent=True)
    blog_id = data.get("id") if data else request.args.get("id")

    if not blog_id:
        return jsonify({"error": "No blog ID provided."}), 400

    try:
        if delete_blog(blog_id):
            logger.info(f"Blog {blog_id} deleted successfully")
            return jsonify({"success": True})
        return jsonify({"error": "Blog post not found."}), 404
    except Exception as e:
        logger.error(f"Failed to delete blog {blog_id}: {e}")
        return jsonify({"error": "Error occurred while deleting blog."}), 500

# ========== CACHE ROUTES ==========
@internal_blueprint.route("/api/clear-cache", methods=["POST"])
@login_required
def api_clear_cache() -> Response:
    try:
        # Targeting specific lru_cache decorated functions
        cacheable_functions = [
            get_settings,
            _load_settings,
            _load_settings_cached,
            load_blogs,
            get_item_by_id,
            query_projects,
            search_projects,
            load_projects,
            get_project_by_id,
            get_events,
            generate_calendar
        ]

        cleared_count = 0
        for func in cacheable_functions:
            if hasattr(func, "cache_clear"):
                func.cache_clear()
                cleared_count += 1

        return jsonify({
            "success": True,
            "message": f"Global cache cleared successfully ({cleared_count} modules)."
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

# ========== MARKDOWN ROUTES ==========
@internal_blueprint.route("/api/markdown-to-html/", methods=["POST"])
@login_required
def api_markdown_to_html() -> Response:
    data = request.get_json()
    if not data or "data" not in data:
        return jsonify({"error": "No markdown data provided."}), 400

    try:
        html_content = convert_markdown_to_html(data["data"])
        return Response(html_content, mimetype="text/html")
    except Exception as e:
        logger.error(f"Failed to convert markdown to HTML: {e}")
        return Response("<p><em>Error rendering preview</em></p>", status=500, mimetype="text/html")

# ========== BLOG SETTINGS ROUTES ==========
@internal_blueprint.route("/api/settings/topics/add", methods=["POST"])
@login_required
def add_topic() -> Response:
    new_topic = request.form.get("new_topic", "").strip()

    try:
        current_config = get_settings("blog_config") or {"topics": [], "types": []}
        topics = current_config.get("topics", [])

        if new_topic and new_topic not in topics:
            topics.append(new_topic)
            update_settings({"blog_config": {"topics": topics}})

    except Exception as e:
        logger.error(f"Failed to add new blog topic: {e}")

    return redirect(request.referrer or "/")

@internal_blueprint.route("/api/settings/types/add", methods=["POST"])
@login_required
def add_type() -> Response:
    type_name = request.form.get("type_name", "").strip()
    type_icon = request.form.get("type_icon", "").strip()

    try:
        current_config = get_settings("blog_config") or {"topics": [], "types": []}
        types = current_config.get("types", [])

        if type_name and not any(t.get("name") == type_name for t in types):
            types.append({"name": type_name, "icon": type_icon})
            update_settings({"blog_config": {"types": types}})

    except Exception as e:
        logger.error(f"Failed to add new blog type: {e}")

    return redirect(request.referrer or "/")

@internal_blueprint.route("/api/settings/topics", methods=["PUT", "DELETE"])
@login_required
def api_manage_topics() -> Response:
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided."}), 400

    try:
        current_config = get_settings("blog_config") or {"topics": [], "types": []}
        topics = current_config.get("topics", [])

        if request.method == "PUT":
            old_name = data.get("old_name")
            new_name = data.get("new_name")

            if not old_name or not new_name:
                return jsonify({"error": "Missing parameters."}), 400

            if old_name in topics:
                topics = [new_name if t == old_name else t for t in topics]
                update_settings({"blog_config": {"topics": topics}})
                return jsonify({"success": True})

            return jsonify({"error": "Topic not found."}), 404

        elif request.method == "DELETE":
            topic_name = data.get("topic_name")

            if topic_name in topics:
                topics.remove(topic_name)
                update_settings({"blog_config": {"topics": topics}})
                return jsonify({"success": True})

            return jsonify({"error": "Topic not found."}), 404

    except Exception as e:
        logger.error(f"API Error managing topics: {e}")
        return jsonify({"error": "Internal server error."}), 500

@internal_blueprint.route("/api/settings/types", methods=["PUT", "DELETE"])
@login_required
def api_manage_types() -> Response:
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided."}), 400

    try:
        current_config = get_settings("blog_config") or {"topics": [], "types": []}
        types = current_config.get("types", [])

        if request.method == "PUT":
            old_name = data.get("old_name")
            new_name = data.get("new_name")
            new_icon = data.get("new_icon")

            if not old_name or not new_name or not new_icon:
                return jsonify({"error": "Missing parameters."}), 400

            for t in types:
                if t.get("name") == old_name:
                    t["name"] = new_name
                    t["icon"] = new_icon
                    update_settings({"blog_config": {"types": types}})
                    return jsonify({"success": True})

            return jsonify({"error": "Type not found."}), 404

        elif request.method == "DELETE":
            type_name = data.get("type_name")

            initial_length = len(types)
            types = [t for t in types if t.get("name") != type_name]

            if len(types) < initial_length:
                update_settings({"blog_config": {"types": types}})
                return jsonify({"success": True})

            return jsonify({"error": "Type not found."}), 404

    except Exception as e:
        logger.error(f"API Error managing types: {e}")
        return jsonify({"error": "Internal server error."}), 500
