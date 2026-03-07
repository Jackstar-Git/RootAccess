import os
from typing import Dict, List, Final
from werkzeug.utils import secure_filename

ALLOWED_FILE_TYPES: Final[Dict[str, List[str]]] = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
    "video": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"],
    "audio": [".mp3", ".wav", ".aac", ".flac", ".ogg"],
    "archive": [".zip", ".tar", ".rar", ".gz"],
    "document": [".pdf", ".docx", ".txt", ".pptx", ".xlsx"],
}

MAX_FILE_SIZE: Final[int] = 100 * 1024 * 1024
ROOT_DIR: Final[str] = "uploads"

def is_safe_path(base_path: str, target_path: str) -> bool:
    abs_base: str = os.path.abspath(base_path)
    abs_target: str = os.path.abspath(os.path.join(abs_base, target_path))
    return abs_target.startswith(abs_base)

def get_file_type(filename: str) -> str:
    _, ext = os.path.splitext(filename.lower())
    for file_type, extensions in ALLOWED_FILE_TYPES.items():
        if ext in extensions:
            return file_type
    return "other"

def sanitize_filename(filename: str) -> str:
    return secure_filename(filename)