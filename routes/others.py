# ========== IMPORTS ==========
import urllib
from datetime import datetime
from typing import Any, Dict, List, Union

from flask import Blueprint, render_template, render_template_string, url_for, request, send_from_directory, make_response, flash, redirect, Response

from CustomFlaskClass import app
from utility import blogs, projects
from utility.logging_utility import logger
from utility.quotes import get_quote_of_the_day
from utility.auth import generate_captcha, pw_protected

# ========== BLUEPRINT INITIALIZATION ==========
others_blueprint = Blueprint("others", __name__)

# ========== ROUTES ==========
@others_blueprint.route("/about", methods=["GET", "POST"])
def about() -> render_template:
    logger.info("About route accessed")
    daily_quote = get_quote_of_the_day()
    return render_template("about.jinja", quote=daily_quote)

@others_blueprint.route("/contact", methods=["GET", "POST"])
def contact() -> render_template:
    captcha = generate_captcha()
    return render_template("contact.jinja", captcha=captcha)

@others_blueprint.route("/imprint", methods=["GET", "POST"])
def imprint() -> render_template:
    logger.info("Imprint route accessed")
    return render_template("legal/imprint.jinja")

@others_blueprint.route("/privacy", methods=["GET", "POST"])
def privacy() -> render_template:
    logger.info("Privacy route accessed")
    return render_template("legal/privacy.jinja")

# ========== SITE MAP ROUTE ==========
@app.route("/sitemap.xml")
def sitemap() -> Response:
    logger.info("Sitemap requested.")
    pages: List[Dict[str, Any]] = []

    default_lastmod = datetime.now()

    excluded_paths = ["/admin", "/static", "/upload", "/download", "/google7825769118bcd42a.html", "/api"]

    for blog in blogs.query_blogs():
        blog_id = blog.get("id", 0)
        url = urllib.parse.urljoin(request.url_root, f"blog/{blog_id}")

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
            "lastmod": datetime.fromtimestamp(project.get("last_updated", default_lastmod)).date().isoformat(),
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

# ========== ROBOTS ROUTE ==========
@app.route("/robots.txt")
def robots() -> Response:
    return send_from_directory("./", "robots.txt")

# ========== GOOGLE VERIFICATION ROUTE ==========
@app.route("/google7825769118bcd42a.html")
def google_verification() -> Response:
    return send_from_directory("./","google7825769118bcd42a.html")
