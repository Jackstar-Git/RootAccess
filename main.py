import os
from datetime import datetime
import sys
import threading
import requests
import time

from dotenv import load_dotenv
from flask import render_template, url_for, make_response, request, jsonify, session, send_from_directory, Response
from flask_wtf.csrf import generate_csrf, CSRFError
from waitress import serve
import urllib.parse

from FlaskClass import app
from utility.logging_utility import logger
from utility import projects, blogs, blog_helpers, get_settings

from routes import blueprints

load_dotenv()
logger.debug("Environment variables have been loaded successfully.")

# register blueprints
for route in blueprints:
    app.register_blueprint(route)
    logger.debug(f"Registered blueprint: {route.name}")

logger.debug("Registered routes:")
for rule in app.url_map.iter_rules():
    logger.debug(f"Route: {rule.rule}, Endpoint: {rule.endpoint}")

@app.template_filter("datetimeformat")
def datetime_filter(value: int, format: str = "%B %d, %Y") -> str:
    if not value:
        return ""
    return datetime.fromtimestamp(value).strftime(format)

@app.before_request
def request_handler():
    request.query_params = dict(request.args)
    if app.maintenance and not request.path.startswith("/admin") and not request.path.startswith("/static") and not request.path.startswith("/uploads") and not session.get("login"):
        logger.warning("Maintenance mode is enabled.")
        response = Response(render_template("maintenance.jinja-html"), status=503)
        response.headers["Retry-After"] = "3600"
        return response

@app.context_processor
def utility_processor():
    return {
        "query_params": request.query_params,
        "session": session,
        "generate_token": generate_csrf
    }


@app.route("/")
def home():
    logger.info("Home page accessed.")
    all_blogs = blogs.query_blogs(status="visible")
    sorted_blogs = blog_helpers.sort_blogs(all_blogs, "newest")
    preview_blogs = sorted_blogs[:3]

    all_projects = projects.load_projects()
    sorted_projects = blog_helpers.sort_blogs(all_projects, "newest")
    preview_projects = sorted_projects[:6]

    return render_template(
        "index.jinja-html",
        preview_blogs=preview_blogs,
        preview_projects=preview_projects
    )

@app.route("/sitemap.xml")
def sitemap():
    logger.info("Sitemap requested.")
    pages = []

    default_lastmod = datetime.now()

    excluded_paths = ["/admin", "/static", "/upload", "/download", "/google7825769118bcd42a.html"]

    for blog in blogs.query_blogs():
        blog_id = blog.get("id", 0)
        url = urllib.parse.urljoin(request.url_root, f"blogs/{blog_id}")
        
        pages.append({
            "loc": url,
            "lastmod": datetime.fromtimestamp(blog.get("last_modified", default_lastmod)).date().isoformat(), 
            "changefreq": "yearly",
            "priority": "0.5"
        })

    for project in projects.query_projects():
        project_id = project.get("id", 0)
        url = urllib.parse.urljoin(request.url_root, f"projects/{project_id}")
        
        pages.append({
            "loc": url,
            "lastmod": datetime.fromtimestamp(project.get("last_modified", default_lastmod)).date().isoformat(),
            "changefreq": "monthly",
            "priority": "0.5"
        })

    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods:
            if rule.arguments:
                continue

            if any(rule.rule.startswith(path) for path in excluded_paths):
                continue

            try:
                url = url_for(rule.endpoint, _external=True)
                pages.append({
                    "loc": url,
                    "lastmod": default_lastmod.date().isoformat(),
                    "changefreq": "monthly",
                    "priority": "0.8" if rule.rule == "/" else "0.5"
                })
            except Exception as e:
                logger.warning(f"Could not generate URL for endpoint {rule.endpoint}: {e}")

    response = make_response(render_template("meta/sitemap.xml", pages=pages))
    response.headers["Content-Type"] = "application/xml"
    logger.info("Sitemap generated with %d pages.", len(pages))
    return response



@app.route("/robots.txt")
def robots():
    return send_from_directory("./", "robots.txt")


@app.route("/google7825769118bcd42a.html")
def google_verification():
    return send_from_directory("/google7825769118bcd42a.html")

@app.errorhandler(405)
def method_not_allowed(error):
    logger.warning(f"405 Method Not Allowed: {request.path}; {error}")
    return jsonify({"error": str(error), "code": 405})

@app.errorhandler(404)
def page_not_found(error):
    logger.warning(f"A page was not found: {request.path}; {error}")
    return render_template("meta/404.jinja-html")

@app.errorhandler(403)
def access_denied(error):
    logger.warning(f"403 Access Denied: {request.path}; {error}")
    return render_template("meta/403.jinja-html")

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    if "missing" in str(e):
        return jsonify({"error": "CSRF token missing", "code": 400})
    return jsonify({"error": "CSRF error", "code": 400})

@app.errorhandler(Exception)
def handle_general_errors(e):
    logger.critical(f"An unexpected error occurred: {str(e)}", exc_info=True)
    return jsonify({"error": "Internal Server Error", "code": 500})


def stay_alive():
    """Background thread periodically pings a URL to keep the host awake."""
    def send_request(server_url):
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

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    logger.info("*" * 50)
    logger.info("Application Server started!")    
    if len(sys.argv) > 1 and sys.argv[1] == "--development":
        logger.info("Running in development mode.")
        app.run(host="localhost", port=8080, debug=True)
    else:   
        stay_alive()    
        serve(app, port=8080, threads=64, url_scheme="https")
