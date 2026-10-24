import copy
import os
import re
from typing import IO, Any

from werkzeug.utils import secure_filename

from utility.settings import get_settings, update_settings


THEME_SCHEMAS = {"light", "dark", "auto", "high-contrast"}
THEME_SCOPES = {
    "colors": "Colors",
    "typography": "Typography",
    "spacing": "Spacing",
    "shapes": "Shapes",
    "effects": "Effects",
    "borders": "Borders",
    "transitions": "Transitions",
    "opacity": "Opacity",
    "others": "Others",
}
_THEME_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_THEME_FIELDS = {
    "theme-name": "name",
    "theme-author": "author",
    "theme-description": "description",
    "theme-color-schema": "color_schema",
    "theme-scope": "scope",
}


def _theme_directory(app_root: str) -> str:
    return os.path.join(app_root, "static", "css", "themes")


def _theme_file_path(app_root: str, theme_id: str) -> str:
    if not _THEME_ID_PATTERN.fullmatch(theme_id) or theme_id in {"default", "light", "dark"}:
        raise ValueError("Invalid or protected theme identifier")
    directory = os.path.realpath(_theme_directory(app_root))
    path = os.path.realpath(os.path.join(directory, f"{theme_id}.css"))
    if os.path.commonpath((directory, path)) != directory:
        raise ValueError("Invalid theme path")
    return path


def parse_theme_metadata(content: str, filename: str) -> dict[str, str]:
    metadata = {field: "" for field in _THEME_FIELDS.values()}
    for block in re.findall(r"/\*(.*?)\*/", content, re.DOTALL):
        for line in block.splitlines():
            key, separator, value = line.strip().lstrip("*").strip().partition(":")
            normalized_key = key.strip().lstrip("@").lower()
            if separator and normalized_key in _THEME_FIELDS:
                metadata[_THEME_FIELDS[normalized_key]] = value.strip()
    if not metadata["name"]:
        metadata["name"] = os.path.splitext(os.path.basename(filename))[0].upper()
    return metadata


def validate_theme_css(content: str, filename: str) -> dict[str, Any]:
    metadata = parse_theme_metadata(content, filename)
    if metadata["color_schema"] not in THEME_SCHEMAS:
        raise ValueError("Theme CSS must define @theme-color-schema as light, dark, auto, or high-contrast.")
    scopes = []
    for value in metadata["scope"].split(","):
        scope = value.strip().lower()
        if not scope:
            continue
        if scope not in THEME_SCOPES:
            raise ValueError(f"Unsupported theme scope: {value.strip()}")
        canonical_scope = THEME_SCOPES[scope]
        if canonical_scope not in scopes:
            scopes.append(canonical_scope)
    metadata["scopes"] = scopes
    metadata["scope"] = ", ".join(scopes)
    return metadata


def _enabled_themes() -> dict[str, bool]:
    settings = get_settings() or {}
    management = settings.get("theme_management", {})
    enabled = management.get("enabled", {}) if isinstance(management, dict) else {}
    return enabled if isinstance(enabled, dict) else {}


def list_themes(app_root: str) -> list[dict[str, Any]]:
    enabled_state = _enabled_themes()
    themes: list[dict[str, Any]] = [{
        "id": "default",
        "name": "Default",
        "author": "",
        "description": "Protected light and dark modes defined in root.css.",
        "color_schema": "auto",
        "scope": "Colors, Typography, Spacing, Shapes, Borders, Transitions",
        "scopes": ["Colors", "Typography", "Spacing", "Shapes", "Borders", "Transitions"],
        "enabled": True,
        "valid": True,
        "protected": True,
        "filename": "root.css",
    }]
    directory = _theme_directory(app_root)
    if not os.path.isdir(directory):
        return themes

    for filename in sorted(os.listdir(directory), key=str.lower):
        if not filename.lower().endswith(".css"):
            continue
        theme_id = os.path.splitext(filename)[0].lower()
        if not _THEME_ID_PATTERN.fullmatch(theme_id) or theme_id in {"default", "light", "dark"}:
            continue
        path = _theme_file_path(app_root, theme_id)
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            metadata = parse_theme_metadata(content, filename)
            try:
                metadata = validate_theme_css(content, filename)
                valid = True
            except ValueError:
                metadata["scopes"] = []
                valid = False
        except (OSError, UnicodeError):
            metadata = {field: "" for field in _THEME_FIELDS.values()}
            metadata["name"] = os.path.splitext(filename)[0].upper()
            metadata["scopes"] = []
            valid = False
        themes.append({
            "id": theme_id,
            **metadata,
            "enabled": bool(enabled_state.get(theme_id, valid)) and valid,
            "valid": valid,
            "protected": False,
            "filename": filename,
        })
    return themes


def available_themes(app_root: str) -> list[dict[str, str]]:
    themes = [
        {"id": "light", "name": "Light", "color_schema": "light"},
        {"id": "dark", "name": "Dark", "color_schema": "dark"},
    ]
    themes.extend(
        {"id": theme["id"], "name": theme["name"], "color_schema": theme["color_schema"]}
        for theme in list_themes(app_root)
        if theme["id"] != "default" and theme["enabled"] and theme["valid"]
    )
    return themes


def read_theme_css(app_root: str, theme_id: str) -> str:
    path = _theme_file_path(app_root, theme_id)
    if not os.path.isfile(path):
        raise FileNotFoundError(theme_id)
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def save_theme_css(app_root: str, theme_id: str, content: str) -> None:
    path = _theme_file_path(app_root, theme_id)
    if not os.path.isfile(path):
        raise FileNotFoundError(theme_id)
    validate_theme_css(content, os.path.basename(path))
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def set_theme_enabled(app_root: str, theme_id: str, enabled: bool) -> None:
    if theme_id == "default":
        raise ValueError("The default theme is protected and cannot be disabled.")
    path = _theme_file_path(app_root, theme_id)
    if not os.path.isfile(path):
        raise FileNotFoundError(theme_id)
    with open(path, "r", encoding="utf-8") as file:
        validate_theme_css(file.read(), os.path.basename(path))

    settings = copy.deepcopy(get_settings() or {})
    management = settings.get("theme_management")
    if not isinstance(management, dict):
        management = {}
    enabled_themes = management.get("enabled")
    if not isinstance(enabled_themes, dict):
        enabled_themes = {}
    enabled_themes[theme_id] = bool(enabled)
    management["enabled"] = enabled_themes
    settings["theme_management"] = management
    update_settings(settings)


def upload_theme_css(app_root: str, filename: str, stream: IO[bytes]) -> str:
    safe_name = secure_filename(filename).lower()
    theme_id, extension = os.path.splitext(safe_name)
    if extension != ".css" or not _THEME_ID_PATTERN.fullmatch(theme_id) or theme_id in {"default", "light", "dark"}:
        raise ValueError("Use a safe .css filename; default, light, and dark are protected.")

    path = _theme_file_path(app_root, theme_id)
    if os.path.exists(path):
        raise FileExistsError(safe_name)
    content = stream.read().decode("utf-8")
    validate_theme_css(content, safe_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
    set_theme_enabled(app_root, theme_id, True)
    return theme_id
