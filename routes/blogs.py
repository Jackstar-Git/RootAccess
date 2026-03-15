from flask import Blueprint, render_template, abort, request
from utility.logging_utility import logger
from utility import blogs, get_settings
from math import ceil
from urllib.parse import urlencode

blogs_blueprint = Blueprint("blogs", __name__)

BLOGS_PER_PAGE = 15


@blogs_blueprint.route("/blog", methods=["GET"])
def blogs_page():
    query = request.args.to_dict()
    search = query.get("search", "").strip()
    sort_by = query.get("sort", "newest").strip()

    try:
        page = int(query.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    if page < 1:
        page = 1


    raw_data = blogs.search_blogs(search) if search else blogs.query_blogs(status="visible")
    

    blog_list = raw_data if isinstance(raw_data, list) else [
        {**content, "id": b_id} for b_id in raw_data for b_id, content in raw_data.items()
    ]


    if query.get("category"):
        blog_list = [b for b in blog_list if query["category"] in b.get("categories", [])]

    if query.get("tags"):
        q_tags = {t.strip().lower() for t in query["tags"].split(",")}
        blog_list = [b for b in blog_list if q_tags.intersection(map(str.lower, b.get("tags", [])))]

    if query.get("type"):
        blog_list = [b for b in blog_list if b.get("type") == query["type"]]

    if query.get("start_date") or query.get("end_date"):
        blog_list = blogs.filter_by_date_range(blog_list, query.get("start_date"), query.get("end_date"))
    
    if query.get("reading_time"):
        blog_list = blogs.filter_by_reading_time(blog_list, query["reading_time"])

    blog_list = blogs.sort_blogs(blog_list, sort_by)


    total_count = len(blog_list)
    total_pages = ceil(total_count / BLOGS_PER_PAGE) if total_count else 1
    start = (page - 1) * BLOGS_PER_PAGE
    end = start + BLOGS_PER_PAGE
    paginated = blog_list[start:end]

    base_query = {k: v for k, v in query.items() if k != "page"}
    base_query_string = urlencode(base_query)

    return render_template(
        "blogs.jinja",
        blogs=paginated,
        settings=get_settings("blog_config"),
        total_count=total_count,
        page=page,
        total_pages=total_pages,
        base_query=base_query,
        base_query_string=base_query_string,
        search_query=search,
        **base_query
    )

@blogs_blueprint.route("/blog/<blog_id>", methods=["GET"])
def blog(blog_id):
    logger.info(f"Blog route accessed for blog ID: {blog_id}")
    if not blog_id:
        logger.warning("No blog ID provided, aborting with 400")
        abort(400, description="Blog ID is required")
    blog_data = blogs.get_item_by_id(blog_id)
    if not blog_data:
        logger.warning(f"Blog with ID {blog_id} not found, aborting with 404")
        abort(404, description="Blog not found")
    return render_template("blog.jinja", blog=blog_data, id=blog_id, suggestions=blogs.query_blogs(categories=blog_data.get("categories", []), status="visible", limit=3, exclude_id=blog_id))
