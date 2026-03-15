from flask import render_template
from utility.logging_utility import logger
from FlaskClass import app
from utility import projects, blogs, blog_helpers, get_settings


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
        "index.jinja",
        preview_blogs=preview_blogs,
        preview_projects=preview_projects
    )