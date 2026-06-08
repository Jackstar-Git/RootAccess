# ========== IMPORTS ==========
from typing import List
from flask import render_template
from flask.typing import ResponseReturnValue

from CustomFlaskClass import app
from utility.blogs import BlogPost, query_blogs, sort_blogs
from utility.projects import Project, sort_projects, load_projects
from utility.logging_utility import logger, log_with_user, logger
from utility.users import get_user_by_id

# ========== ROUTES ==========
@app.route("/")
def home() -> ResponseReturnValue:
    logger.info("Home page accessed.")
    all_blogs: List[BlogPost] = query_blogs(status="visible")
    sorted_blogs: List[BlogPost] = sort_blogs(all_blogs, "newest")
    preview_blogs: List[BlogPost] = sorted_blogs[:3]


    if not preview_blogs:
        logger.info("No visible blogs found for preview on home page.")
        preview_blogs_data = []
    else:
        preview_blogs_data = list(map(lambda blog_data: {
            **blog_data,
            "author_names": [
                get_user_by_id(author_id).get("username", "") #type: ignore
                for author_id in blog_data.get("authors", [])
            ]
        }, preview_blogs))
    

    all_projects: List[Project] = load_projects()
    sorted_projects: List[Project] = sort_projects(all_projects, "newest")
    preview_projects: List[Project] = sorted_projects[:6]

    if not preview_projects:
        logger.info("No visible projects found for preview on home page.")
        preview_projects = []
    else:
        preview_projects = list(map(lambda project_data: {
            **project_data,
            "author_names": [
                get_user_by_id(author_id).get("username", "") #type: ignore
                for author_id in project_data.get("authors", [])
            ]
        }, preview_projects))

    return render_template(
        "index.jinja",
        preview_blogs=preview_blogs_data,
        preview_projects=preview_projects
    )
