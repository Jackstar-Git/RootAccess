import json
import os
from datetime import datetime
from flask import Flask, request, session, render_template, Response
from utility.logging_utility import logger
from flask_wtf.csrf import CSRFProtect, generate_csrf

# =====================================
# Configure the Flask app and session settings
# =====================================

class CustomFlask(Flask):
    def __init__(self, import_name, *args, **kwargs):
        super().__init__(import_name, *args, **kwargs)
        self.load_server_config()
        self.logger.disabled = True
        self.secret_key = "1"

        self.add_template_filter(self.datetime_filter, name="datetimeformat")
        self.before_request(self.request_handler)
        self.context_processor(self.utility_processor)

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def update_config(self, config_dict):
        self.config.update(config_dict)

    def __repr__(self):
        return f"<CustomFlask name={self.name}, server_name={self.config.get('SERVER_NAME')} >"

    def load_server_config(self):
        settings = self._read_settings_file()
        server_config = settings.get("server_config", {})
        self.config.update(server_config)
        self.maintenance = server_config.get("maintenance", False)

    def _read_settings_file(self):
        settings_path = "data/settings.json"
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def request_handler(self):
        request.query_params = dict(request.args)
        
        if self.maintenance and not request.path.startswith("/admin") and not request.path.startswith("/static") and not request.path.startswith("/uploads") and not session.get("login"):
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
    def utility_processor():
        return {
            "query_params": request.query_params,
            "session": session,
            "generate_token": generate_csrf
        }
    

app = CustomFlask(__name__, template_folder="templates", static_folder="static")
csrf = CSRFProtect(app)
