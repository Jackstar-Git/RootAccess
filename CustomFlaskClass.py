# ========== IMPORTS ==========
import json
import os
import secrets
from datetime import datetime
from typing import Any, Dict, Union

from flask import Flask, request, session, render_template, Response
from flask_wtf.csrf import CSRFProtect, generate_csrf

from utility.logging_utility import logger

# ========== CUSTOM FLASK CLASS ==========
class CustomFlask(Flask):
    def __init__(self, import_name: str, *args, **kwargs) -> None:
        super().__init__(import_name, *args, **kwargs)
        self.load_server_config()
        self.logger.disabled = True
        self.secret_key = secrets.token_hex(64)

        self.add_template_filter(self.datetime_filter, name="datetimeformat")
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

    def request_handler(self) -> Union[None, Response]:
        request.query_params = dict(request.args)

        if self.config.get("maintenance") and not request.path.startswith("/admin") and not request.path.startswith("/static") and not request.path.startswith("/uploads") and not session.get("login"):
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
    def utility_processor() -> Dict[str, Any]:
        return {
            "query_params": request.query_params,
            "session": session,
            "generate_token": generate_csrf
        }

# ========== APPLICATION INITIALIZATION ==========
app = CustomFlask(__name__, template_folder="templates", static_folder="static")
csrf = CSRFProtect(app)
