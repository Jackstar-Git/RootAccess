from flask import Blueprint, render_template, abort
from logging_utility import logger

blogs_blueprint = Blueprint("blogs", __name__)


@blogs_blueprint.route("/blog", methods=["GET", "POST"])
def blogs():
    logger.info("Blogs route accessed")
    return render_template("blog.jinja-html")


# This function handles the logout process
@blogs_blueprint.route("/blogs/<blog_id>", methods=["GET"])
def blog(blog_id):
    logger.info(f"Blog route accessed for blog ID: {blog_id}")
    if not blog_id:
        logger.warning("No blog ID provided, aborting with 400")
        abort(400, description="Blog ID is required")
    return render_template("blog.jinja-html", blog=blog_id)
 