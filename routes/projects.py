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

    if search:
        project_list = projects.search_projects(search)
    else:
        project_list = projects.load_projects()


    if query.get("category"):
        project_list = [p for p in project_list if p.get("category") == query["category"]]

    if query.get("tech_stack"):
        q_tech = {t.strip().lower() for t in query["tech_stack"].split(",")}
        project_list = [
            p for p in project_list 
            if q_tech.intersection(map(str.lower, p.get("tech_stack", [])))
        ]

    if query.get("activity"):
        q_activity = {a.strip() for a in query["activity"].split(",")}
        project_list = [p for p in project_list if p.get("activity") in q_activity]

    if query.get("maturity"):
        q_maturity = {m.strip() for m in query["maturity"].split(",")}
        project_list = [p for p in project_list if p.get("maturity") in q_maturity]

    import datetime
    try:
        if query.get("start_date"):
            start_ts = datetime.datetime.strptime(query["start_date"], "%Y-%m-%d").timestamp()
            project_list = [p for p in project_list if p.get("time_created", 0) >= start_ts]
        if query.get("end_date"):
            end_ts = datetime.datetime.strptime(query["end_date"], "%Y-%m-%d").timestamp()
            project_list = [p for p in project_list if p.get("time_created", 0) <= end_ts]
    except ValueError:
        pass 

    reverse = (sort_by == "newest")
    project_list.sort(key=lambda x: x.get("time_created", 0), reverse=reverse)

    return render_template(
        "projects.jinja-html",
        projects=project_list,
        search_query=search,
        settings=get_settings("project_config"),
        **query
    )

@projects_blueprint.route("/projects/<project_id>", methods=["GET"])
def project(project_id):
    logger.info(f"Accessing project: {project_id}")
    
    project_data = projects.get_project_by_id(project_id)
    if not project_data:
        logger.warning(f"Project {project_id} not found")
        abort(404)

    return render_template("project.jinja-html", project=project_data, suggestions=projects.query_projects(topic=project_data.get("topic", ""), limit=2, exclude_id=project_id))