import io
import os
import zipfile

from flask import request, abort, session, Blueprint, send_file
from FlaskClass import app
from logging_utility import logger

internal_blueprint = Blueprint("internal", __name__, template_folder="./templates")

# serve files from uploads directory
@internal_blueprint.route("/uploads/<path:filename>", methods=["GET"])
def uploads(filename):
    logger.info(f"GET request received for serving file from uploads | Filename: {filename}")
    try:
        return send_file(os.path.join(app.root_path, "uploads", filename))
    except Exception as e:
        logger.error(f"Error serving file from uploads | Filename: {filename} | Error: {str(e)}")
        abort(404)

# serve files from plugins directory
@internal_blueprint.route("/plugins/<path:filename>", methods=["GET"])
def plugins(filename):
    logger.info(f"GET request received for serving file from plugins | Filename: {filename}")
    try:
        return send_file(os.path.join(app.root_path, "plugins", filename))
    except Exception as e:
        logger.error(f"Error serving file from plugins | Filename: {filename} | Error: {str(e)}")
        abort(404)

# authenticated download route
@internal_blueprint.route("/download/<path:filepath>", methods=["GET"])
def download(filepath):
    logger.info(f"GET request received for download | Path: {filepath}")
    if not session.get("login", False):
        logger.warning("Unauthorized download attempt")
        return abort(403)

    if not os.path.exists(filepath):
        logger.error(f"File or directory not found | Path: {filepath}")
        abort(404, description="File or directory not found.")

    if os.path.isfile(filepath):
        logger.info(f"Serving file | Path: {filepath}")
        return send_file(filepath, as_attachment=True)

    if os.path.isdir(filepath):
        logger.info(f"Creating zip for directory | Path: {filepath}")
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(filepath):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, filepath))
        
        memory_file.seek(0)
        zip_filename = os.path.basename(filepath) + ".zip"
        return send_file(memory_file, as_attachment=True, download_name=zip_filename, mimetype="application/zip")

    logger.error(f"Invalid path provided | Path: {filepath}")
    abort(400, description="Invalid path provided.")
