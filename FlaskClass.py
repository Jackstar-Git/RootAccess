import json
import os
from datetime import timedelta

from flask import Flask
from flask_wtf.csrf import CSRFProtect

# =====================================
# Configure the Flask app and session settings
# =====================================

class CustomFlask(Flask):
    def __init__(self, import_name, *args, **kwargs):
        super().__init__(import_name, *args, **kwargs)
        self.load_formats()
        self.load_server_config()
        self.logger.disabled = True
        self.secret_key = "1"

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def update_config(self, config_dict):
        self.config.update(config_dict)

    def __repr__(self):
        return f"<CustomFlask name={self.name}, server_name={self.config.get('SERVER_NAME')} >"

    def load_formats(self):
        settings = self._read_settings_file()
        self._format = settings.get("format", "#.##0,00")



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


app = CustomFlask(__name__, template_folder="templates", static_folder="static")
csrf = CSRFProtect(app)