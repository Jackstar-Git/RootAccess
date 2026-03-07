from datetime import datetime
import io
import os
import shutil
import zipfile
from typing import Dict, List, Optional, Union

from flask import Blueprint, request, abort, session, send_file, jsonify
from werkzeug.utils import secure_filename
import psutil

from FlaskClass import app, csrf
from utility.logging_utility import logger
from utility.path_files import MAX_FILE_SIZE, ROOT_DIR, sanitize_filename, is_safe_path, get_file_type
from utility.auth import login_required

internal_blueprint = Blueprint("internal", __name__, template_folder="./templates")

# File Serving Routes
@internal_blueprint.route("/uploads/<path:filename>", methods=["GET"])
def uploads(filename: str) -> str:
    """Serve files from uploads directory."""
    logger.info(f"GET request received for serving file from uploads | Filename: {filename}")
    try:
        return send_file(os.path.join(app.root_path, "uploads", filename))
    except Exception as e:
        logger.error(f"Error serving file from uploads | Filename: {filename} | Error: {str(e)}")
        abort(404)

@internal_blueprint.route("/plugins/<path:filename>", methods=["GET"])
def plugins(filename: str) -> str:
    """Serve files from plugins directory."""
    logger.info(f"GET request received for serving file from plugins | Filename: {filename}")
    try:
        return send_file(os.path.join(app.root_path, "plugins", filename))
    except Exception as e:
        logger.error(f"Error serving file from plugins | Filename: {filename} | Error: {str(e)}")
        abort(404)

@internal_blueprint.route("/download/<path:filepath>", methods=["GET"])
def download(filepath: str) -> str:
    """Authenticated download route."""
    logger.info(f"GET request received for download | Path: {filepath}")
    is_public_path = filepath.startswith("uploads/")
    is_admin = session.get("is_admin", False)

    if not is_public_path and not is_admin:
        logger.warning(f"Unauthorized download attempt to restricted path: {filepath}")
        return abort(403)

    full_path = os.path.join(app.root_path, filepath)
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

# API Endpoints
@internal_blueprint.route("/api/add-events/", methods=["POST"])
@login_required
def add_events() -> Union[str, tuple]:
    """Endpoint for adding new events to the calendar."""
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

        # Validate date ranges
        if not 1 <= month <= 12:
            return jsonify({"error": "Month must be between 1 and 12"}), 400
        if not 1 <= day <= 31:
            return jsonify({"error": "Day must be between 1 and 31"}), 400

        # Validate day for specific months
        if month in [4, 6, 9, 11] and day > 30:
            return jsonify({"error": "This month only has 30 days"}), 400
        elif month == 2:
            if not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) and day > 28:
                return jsonify({"error": "February only has 28 days in non-leap years"}), 400
            elif day > 29:
                return jsonify({"error": "February only has 29 days in leap years"}), 400

    except ValueError:
        return jsonify({"error": "Year, month, and day must be integers"}), 400

    from utility.events import get_events, add_event
    events = get_events()
    existing_ids = []
    for event in events:
        try:
            existing_ids.append(int(event["id"]))
        except (ValueError, TypeError):
            continue

    new_id = str(max(existing_ids, default=0) + 1)

    new_event = {
        "id": new_id,
        "year": year,
        "month": month,
        "day": day,
        "name": data["name"].strip(),
        "description": data["description"].strip(),
    }

    try:
        add_event(new_event)
        return jsonify({
            "message": "Event added successfully",
            "event": new_event
        }), 201
    except Exception as e:
        logger.error(f"Failed to add event | Error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@internal_blueprint.route("/api/get-system-info/", methods=["GET"])
@login_required
def get_system_info() -> str:
    """Endpoint for retrieving system information."""
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

# File Management Endpoints
@internal_blueprint.route("/api/files/upload", methods=["POST"])
@login_required
def upload_file() -> str:
    """Endpoint for file uploads."""
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
def delete_files() -> str:
    """Endpoint for file deletion."""
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
def rename_file() -> str:
    """Endpoint for renaming files."""
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
def copy_file() -> str:
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
def create_folder() -> str:
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
