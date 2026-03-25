import json
import os
import time
from flask import current_app
from utility.logging_utility import logger
from utility.settings import get_settings


ANALYTICS_FILE = "data/analytics.json"
FLUSH_INTERVAL = get_settings("analytics_config").get("update_interval", 600) #seconds = 10 minutes by default

def track_visit(url: str, visitor_id: str, time_spent: float, is_heartbeat: bool) -> None:
    app = current_app
    with app.analytics_lock:
        cache = app.analytics_cache
        
        if url not in cache:
            cache[url] = {
                "url": url, "visits": 0, "unique_visits": 0, "visitors": [], 
                "total_time_spent": 0.0, "average_time_spent": 0.0
            }

        data = cache[url]
        
        if not is_heartbeat:
            data["visits"] += 1
            if visitor_id not in data["visitors"]:
                data["unique_visits"] += 1
                data["visitors"].append(visitor_id)
        
        data["total_time_spent"] += float(time_spent)

        if data["visits"] > 0:
            data["average_time_spent"] = round(data["total_time_spent"] / data["visits"], 2)

        if time.time() - app.last_analytics_flush > FLUSH_INTERVAL:
            _save_analytics(app)

def _save_analytics(app) -> None:
    os.makedirs(os.path.dirname(ANALYTICS_FILE), exist_ok=True)
    try:
        with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
            json.dump(app.analytics_cache, f, indent=4)
        app.last_analytics_flush = time.time()
    except Exception as e:
        logger.error(f"Failed to save analytics to disk: {e}")

def get_all_analytics() -> dict:
    return current_app.analytics_cache

def clear_analytics(url: str = None) -> None:
    app = current_app
    with app.analytics_lock:
        if url and url in app.analytics_cache:
            del app.analytics_cache[url]
        elif not url:
            app.analytics_cache.clear()
        _save_analytics(app)