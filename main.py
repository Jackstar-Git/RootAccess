# ========== IMPORTS ==========
import os
import sys
import threading
import time
from typing import Any, List

import requests
from dotenv import load_dotenv
from waitress import serve

from CustomFlaskClass import app
from utility.logging_utility import logger
from utility.scheduler import start_scheduler
from routes import blueprints

# ========== INITIALIZATION ==========
load_dotenv()
logger.debug("Environment variables have been loaded successfully.")

for route in blueprints:
    app.register_blueprint(route)
    logger.debug(f"Registered blueprint: {route.name}")

logger.debug("Registered routes:")
for rule in app.url_map.iter_rules():
    logger.debug(f"Route: {rule.rule}, Endpoint: {rule.endpoint}")

# ========== BACKGROUND THREAD ==========
def stay_alive() -> None:
    def send_request(server_url: str) -> None:
        while True:
            try:
                if server_url:
                    requests.get(server_url)
            except Exception:
                pass
            time.sleep(300)

    server_url = "https://rootaccess.onrender.com"
    if server_url:
        thread = threading.Thread(target=send_request, args=(server_url,))
        thread.daemon = True
        thread.start()

# ========== MAIN ==========
if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    logger.info("*" * 50)
    logger.info("Application Server started!")
    #start_scheduler()
    if len(sys.argv) > 1 and sys.argv[1] == "--development":
        logger.info("Running in development mode.")
        app.run(host="localhost", port=8080, debug=True)
    else:
        stay_alive()
        serve(app, port=8080, threads=64, url_scheme="https")
