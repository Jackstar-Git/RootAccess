# ========== IMPORTS ==========
import json
import os
import secrets
import threading
import time
from datetime import datetime
from typing import Any, Dict, Union, Optional, List

from flask import Flask, request, session, render_template, Response
from flask_wtf.csrf import CSRFProtect, generate_csrf

from utility.auth import get_user_permissions
from utility.logging_utility import logger

# ========== CUSTOM FLASK CLASS ==========
class CustomFlask(Flask):
    def __init__(self, import_name: str, *args, **kwargs) -> None:
        super().__init__(import_name, *args, **kwargs)
        self.load_server_config()
        self.logger.disabled = True
        self.secret_key = secrets.token_hex(64)
        
        # User Cache Setup
        self.users_cache: Optional[Dict[str, Any]] = None
        self.users_cache_mtime: Optional[float] = None
        
        # Analytics Cache Setup
        self.analytics_cache = {}
        self.analytics_lock = threading.Lock()
        self.last_analytics_flush = time.time()
        self._load_initial_analytics()

        self.add_template_filter(self.datetime_filter, name="datetimeformat")
        self.add_template_filter(self.strftime_filter, name="strftime")
        self.before_request(self.request_handler)
        self.context_processor(self.utility_processor)

    def __getitem__(self, key: str) -> Any:
        return self.config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.config[key] = value

    def update_config(self, config_dict: Dict[str, Any]) -> None:
        self.config.update(config_dict)

    def __repr__(self) -> str:
        return f"<CustomFlask name={self.name}, server_name={self.config.get('SERVER_NAME')} >"

    def load_server_config(self) -> None:
        settings = self._read_settings_file()
        server_config = settings.get("server_config", {})
        self.config.update(server_config)

    def _read_settings_file(self) -> Dict[str, Any]:
        settings_path = "data/settings.json"
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
        
    def _load_initial_analytics(self) -> None:
        analytics_path = "data/analytics.json"
        if os.path.exists(analytics_path):
            try:
                with open(analytics_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        app.analytics_cache = {} 
                    else:
                        self.analytics_cache = data
            except Exception as e:
                logger.error(f"Failed to load initial analytics cache: {e}")

    def request_handler(self) -> Union[None, Response]:
        request.query_params = dict(request.args)

        if self.config.get("maintenance") and not request.path.startswith("/admin") and not request.path.startswith("/static") and not request.path.startswith("/uploads") and not session.get("username"):
            logger.warning("Maintenance mode is enabled.")
            response = Response(render_template("maintenance.jinja"), status=503)
            response.headers["Retry-After"] = "3600"
            return response

    @staticmethod
    def datetime_filter(value: int, format: str = "%B %d, %Y") -> str:
        if not value:
            return ""
        return datetime.fromtimestamp(value).strftime(format)

    @staticmethod
    def strftime_filter(value: int, format: str = "%Y-%m-%d %H:%M") -> str:
        if not value:
            return ""
        return datetime.fromtimestamp(value).strftime(format)

    @staticmethod
    def utility_processor() -> Dict[str, Any]:

        # Get current user info from session
        current_username: Optional[str] = session.get("username")
        current_user_permissions: List[str] = session.get("permissions", [])

        if current_username and not current_user_permissions:
            current_user_permissions = get_user_permissions(app, current_username)
            session["permissions"] = current_user_permissions
        # Try to include current user's profile picture URL if available
        current_user_profile: Optional[str] = None
        try:
            from utility.auth import get_users as _get_users
            users = _get_users(app)
            if current_username and isinstance(users, dict) and current_username in users:
                current_user_profile = users.get(current_username, {}).get("profile_picture_url")
        except Exception:
            current_user_profile = None

        return {
            "query_params": request.query_params,
            "session": session,
            "generate_token": generate_csrf,
            "current_user": current_username,
            "current_user_permissions": current_user_permissions,
            "current_user_profile": current_user_profile,
        }

# ========== APPLICATION INITIALIZATION ==========
app = CustomFlask(__name__, template_folder="templates", static_folder="static")
csrf = CSRFProtect(app)