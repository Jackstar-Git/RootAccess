# ========== IMPORTS ==========
import urllib.parse
from datetime import datetime
from typing import Any, Dict, List, Union

from flask import Blueprint, render_template, url_for, request, send_from_directory, make_response, current_app
from flask.typing import ResponseReturnValue

from utility import blogs, projects
from utility.logging_utility import logger, log_with_user
from utility.quotes import get_quote_of_the_day
from utility.auth import generate_captcha
from CustomFlaskClass import app

# ========== BLUEPRINT INITIALIZATION ==========
others_blueprint = Blueprint("others", __name__)

# ========== ROUTES ==========
@others_blueprint.route("/about", methods=["GET", "POST"])
def about() -> ResponseReturnValue:
    logger.info("About route accessed")
    daily_quote = get_quote_of_the_day()
    return render_template("about.jinja", quote=daily_quote)

@others_blueprint.route("/contact", methods=["GET", "POST"])
def contact() -> ResponseReturnValue:
    captcha = generate_captcha()
    return render_template("contact.jinja", captcha=captcha)

@others_blueprint.route("/imprint", methods=["GET", "POST"])
def imprint() -> ResponseReturnValue:
    logger.info("Imprint route accessed")
    return render_template("legal/imprint.jinja")

@others_blueprint.route("/privacy", methods=["GET", "POST"])
def privacy() -> ResponseReturnValue:
    logger.info("Privacy route accessed")
    return render_template("legal/privacy.jinja")

# ========== SITE MAP ROUTE ==========
@app.route("/sitemap.xml")
def sitemap() -> ResponseReturnValue:
    logger.info("Sitemap requested.")
    pages: List[Dict[str, Any]] = []
    
    now = datetime.now()
    default_lastmod_str = now.date().isoformat()
    
    def parse_lastmod(val: Any) -> str:
        if isinstance(val, (int, float)):
            return datetime.fromtimestamp(val).date().isoformat()
        if isinstance(val, datetime):
            return val.date().isoformat()
        return default_lastmod_str

    latest_blog_date = None
    for blog in blogs.query_blogs():
        blog_id = blog.get("id", 0)
        url = urllib.parse.urljoin(request.url_root, f"blog/{blog_id}")
        
        mod_date = parse_lastmod(blog.get("last_modified"))
        if not latest_blog_date or mod_date > latest_blog_date:
            latest_blog_date = mod_date

        pages.append({
            "loc": url,
            "lastmod": mod_date,
            "changefreq": "monthly",  
            "priority": "0.7"
        })

    latest_project_date = None
    for project in projects.query_projects():
        project_id = project.get("id", 0)
        url = urllib.parse.urljoin(request.url_root, f"projects/{project_id}")

        mod_date = parse_lastmod(project.get("last_updated"))
        if not latest_project_date or mod_date > latest_project_date:
            latest_project_date = mod_date

        pages.append({
            "loc": url,
            "lastmod": mod_date,
            "changefreq": "monthly",  
            "priority": "0.8"
        })

    excluded_paths = [
        "/admin", 
        "/static", 
        "/upload", 
        "/download", 
        "/google7825769118bcd42a.html", 
        "/.well-known"
    ]

    for rule in current_app.url_map.iter_rules():
        if rule.methods and "GET" in rule.methods:
            if rule.arguments:
                continue

            if any(rule.rule.startswith(path) for path in excluded_paths):
                continue

            try:
                url = url_for(rule.endpoint, _external=True)
                
                priority = "0.5"
                changefreq = "monthly"
                lastmod = default_lastmod_str

                if rule.rule == "/":
                    priority = "1.0"
                    changefreq = "weekly"
                    lastmod = max(filter(None, [latest_blog_date, latest_project_date, default_lastmod_str]))

                elif rule.rule == "/blog":
                    priority = "0.9"
                    changefreq = "weekly"
                    lastmod = latest_blog_date or default_lastmod_str

                elif rule.rule == "/projects":
                    priority = "0.9"
                    changefreq = "monthly"
                    lastmod = latest_project_date or default_lastmod_str

                elif rule.rule == "/about":
                    priority = "0.6"
                    changefreq = "daily"
                    lastmod = now.date().isoformat()
                elif rule.rule.startswith("/api"):
                    priority = "0.6"
                    changefreq = "weekly"

                pages.append({
                    "loc": url,
                    "lastmod": lastmod,
                    "changefreq": changefreq,
                    "priority": priority
                })
            except Exception as e:
                logger.warning(f"Could not generate URL for endpoint {rule.endpoint}: {e}")

    response = make_response(render_template("meta/sitemap.xml", pages=pages))
    response.headers["Content-Type"] = "application/xml"
    logger.info("Sitemap generated with %d pages.", len(pages))
    return response

# ========== ROBOTS ROUTE ==========
@app.route("/robots.txt")
def robots() -> ResponseReturnValue:
    return send_from_directory("./", "robots.txt")

# ========== GOOGLE VERIFICATION ROUTE ==========
@app.route("/google7825769118bcd42a.html")
def google_verification() -> ResponseReturnValue:
    return send_from_directory("./","google7825769118bcd42a.html")

@app.route("/.well-known/discord")
def discord_verification() -> ResponseReturnValue:
    return send_from_directory("./", "discord-verification.txt")

