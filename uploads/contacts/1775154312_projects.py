# ========== IMPORTS ==========
import datetime

from flask import Blueprint, render_template, abort, request

from utility import projects
from utility.logging_utility import logger
from utility.settings import get_settings

# ========== BLUEPRINT INITIALIZATION ==========
projects_blueprint = Blueprint("projects", __name__)

# ========== ROUTES ==========
@projects_blueprint.route("/projects", methods=["GET"])
def projects_page() -> render_template:
    query = request.args.to_dict()
    search: str = query.get("search", "").strip()
    sort_by: str = query.get("sort", "newest").strip()

    if search:
        project_list = projects.search_projects(search)
    else:
        project_list = projects.load_projects()

    if query.get("category"):
        project_list = [p for p in project_list if p.get("category") == query.get("category")]

    if query.get("tech_stack"):
        q_tech = {t.strip().lower() for t in query.get("tech_stack", "").split(",")}
        project_list = [
            p for p in project_list
            if q_tech.intersection(map(str.lower, p.get("tech_stack", [])))
        ]

    if query.get("activity"):
        q_activity = {a.strip() for a in query.get("activity", "").split(",")}
        project_list = [p for p in project_list if p.get("activity") in q_activity]

    if query.get("maturity"):
        q_maturity = {m.strip() for m in query.get("maturity", "").split(",")}
        project_list = [p for p in project_list if p.get("maturity") in q_maturity]

    try:
        if query.get("start_date"):
            start_ts = datetime.datetime.strptime(query.get("start_date", ""), "%Y-%m-%d").timestamp()
            project_list = [p for p in project_list if p.get("time_created", 0) >= start_ts]
        if query.get("end_date"):
            end_ts = datetime.datetime.strptime(query.get("end_date", ""), "%Y-%m-%d").timestamp()
            project_list = [p for p in project_list if p.get("time_created", 0) <= end_ts]
    except ValueError:
        pass

    reverse = (sort_by == "newest")
    project_list.sort(key=lambda x: x.get("time_created", 0), reverse=reverse)

    return render_template(
        "projects.jinja",
        projects=project_list,
        search_query=search,
        settings=get_settings("project_config"),
        **query
    )

@projects_blueprint.route("/projects/<project_id>", methods=["GET"])
def project(project_id: str) -> render_template:
    logger.info(f"Accessing project: {project_id}")

    project_data = projects.get_project_by_id(project_id)
    if not project_data:
        logger.warning(f"Project {project_id} not found")
        abort(404)

    return render_template("project.jinja", project=project_data, suggestions=projects.query_projects(topic=project_data.get("topic", ""), limit=2, exclude_id=project_id))
