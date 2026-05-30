# ========== IMPORTS ==========
from typing import List
from flask import render_template
from flask.typing import ResponseReturnValue

from CustomFlaskClass import app
from utility.blogs import BlogPost, query_blogs, sort_blogs
from utility.projects import Project, sort_projects, load_projects
from utility.logging_utility import logger, log_with_user

# ========== ROUTES ==========
@app.route("/")
def home() -> ResponseReturnValue:
    logger.info("Home page accessed.")
    all_blogs = query_blogs(status="visible")
    sorted_blogs = sort_blogs(all_blogs, "newest")
    preview_blogs = sorted_blogs[:3]

    all_projects: List[Project] = load_projects()
    sorted_projects = sort_projects(all_projects, "newest")
    preview_projects = sorted_projects[:6]

    return render_template(
        "index.jinja",
        preview_blogs=preview_blogs,
        preview_projects=preview_projects
    )
