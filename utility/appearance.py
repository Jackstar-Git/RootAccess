import os
from typing import IO

from werkzeug.utils import secure_filename


_ALLOWED_EXTENSIONS = {
    "templates": {".jinja", ".jinja-html"},
    "static": {".css", ".js"},
}


def _appearance_root(app_root: str, area: str) -> str:
    if area not in _ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported appearance file area")
    folder = "templates" if area == "templates" else "static"
    return os.path.realpath(os.path.join(app_root, folder))


def _validate_appearance_path(app_root: str, area: str, relative_path: str) -> str:
    root = _appearance_root(app_root, area)
    target = os.path.realpath(os.path.join(root, relative_path))
    normalized_path = os.path.normpath(relative_path).replace("\\", "/").lower()
    if area == "static" and (normalized_path == "css/root.css" or normalized_path.startswith("css/themes/")):
        raise ValueError("Root styles and managed themes are protected from the generic file editor")
    try:
        inside_root = os.path.commonpath((root, target)) == root
    except ValueError:
        inside_root = False

    if not inside_root or os.path.splitext(target)[1].lower() not in _ALLOWED_EXTENSIONS[area]:
        raise ValueError("Unsupported appearance file")
    if area == "static" and os.path.relpath(target, root).split(os.sep, 1)[0] not in {"css", "js"}:
        raise ValueError("Only files in static/css and static/js are supported")
    return target


def list_appearance_files(app_root: str, area: str) -> list[str]:
    root = _appearance_root(app_root, area)
    search_roots = [root] if area == "templates" else [os.path.join(root, "css"), os.path.join(root, "js")]
    files = []
    for search_root in search_roots:
        if not os.path.isdir(search_root):
            continue
        for directory, _, filenames in os.walk(search_root):
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() in _ALLOWED_EXTENSIONS[area]:
                    path = os.path.join(directory, filename)
                    normalized_path = os.path.relpath(path, root).replace(os.sep, "/").lower()
                    if area == "static" and (normalized_path == "css/root.css" or normalized_path.startswith("css/themes/")):
                        continue
                    files.append(os.path.relpath(path, root).replace(os.sep, "/"))
    return sorted(files, key=str.lower)


def read_appearance_file(app_root: str, area: str, relative_path: str) -> str:
    target = _validate_appearance_path(app_root, area, relative_path)
    if not os.path.isfile(target):
        raise FileNotFoundError(relative_path)
    with open(target, "r", encoding="utf-8") as file:
        return file.read()


def write_appearance_file(app_root: str, area: str, relative_path: str, content: str) -> None:
    target = _validate_appearance_path(app_root, area, relative_path)
    if not os.path.isfile(target):
        raise FileNotFoundError(relative_path)
    with open(target, "w", encoding="utf-8") as file:
        file.write(content)


def upload_appearance_file(app_root: str, area: str, filename: str, stream: IO[bytes], category: str = "") -> str:
    safe_name = secure_filename(filename)
    extension = os.path.splitext(safe_name)[1].lower()
    if not safe_name or extension not in _ALLOWED_EXTENSIONS.get(area, set()):
        raise ValueError("Unsupported file type")

    if area == "templates":
        relative_path = safe_name
    elif area == "static" and category in {"css", "js"} and extension == f".{category}":
        relative_path = os.path.join(category, safe_name)
    else:
        raise ValueError("Choose a matching CSS or JavaScript destination")

    target = _validate_appearance_path(app_root, area, relative_path)
    if os.path.exists(target):
        raise FileExistsError(safe_name)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "wb") as file:
        while chunk := stream.read(64 * 1024):
            file.write(chunk)
    return relative_path.replace(os.sep, "/")


