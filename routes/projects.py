from flask import Blueprint, render_template, abort
from logging_utility import logger

projects_blueprint = Blueprint("projects", __name__)


@projects_blueprint.route("/projects", methods=["GET", "POST"])
def projects():
    logger.info("Projects route accessed")
    return render_template("projects.jinja-html")


@projects_blueprint.route("/projects/<project_id>", methods=["GET"])
def project(project_id):
    logger.info(f"Project route accessed for project ID: {project_id}")
    if not project_id:
        logger.warning("No project ID provided, aborting with 400")
        abort(400, description="Project ID is required")
    return render_template("project.jinja-html", project=project_id)
 