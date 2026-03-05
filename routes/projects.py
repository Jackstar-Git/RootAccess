from urllib.parse import urlencode
from flask import Blueprint, render_template, abort, request
from utility.settings import get_settings
from utility.logging_utility import logger
from utility import projects as projects

projects_blueprint = Blueprint("projects", __name__)

@projects_blueprint.route("/projects", methods=["GET"])
def projects_page():
    query = request.args.to_dict()
    search = query.get("search", "").strip()
    sort_by = query.get("sort", "newest").strip()

    # 1. Get Data
    if search:
        project_list = projects.search_projects(search)
    else:
        project_list = projects.load_projects()

    # 2. Filter by Category
    if query.get("category"):
        project_list = [p for p in project_list if p.get("category") == query["category"]]

    # 3. Filter by Tech Stack
    if query.get("tech_stack"):
        q_tech = {t.strip().lower() for t in query["tech_stack"].split(",")}
        project_list = [
            p for p in project_list 
            if q_tech.intersection(map(str.lower, p.get("tech_stack", [])))
        ]

    # 4. Sort
    reverse = True if sort_by == "newest" else False
    project_list.sort(key=lambda x: x.get("time_created", 0), reverse=reverse)

    base_query = {k: v for k, v in query.items()}
    
    return render_template(
        "projects.jinja-html",
        projects=project_list,
        search_query=search,
        settings=get_settings("project_config"),
        **base_query
    )

@projects_blueprint.route("/projects/<project_id>", methods=["GET"])
def project(project_id):
    logger.info(f"Accessing project: {project_id}")
    
    project_data = projects.get_project_by_id(project_id)
    if not project_data:
        logger.warning(f"Project {project_id} not found")
        abort(404)
        
    return render_template("project.jinja-html", project=project_data)