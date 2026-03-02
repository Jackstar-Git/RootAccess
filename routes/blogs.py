from flask import Blueprint, render_template, abort, request
from utility.logging_utility import logger
from utility import blogs as blog_utils, blog_helpers, get_settings

blogs_blueprint = Blueprint("blogs", __name__)

BLOGS_PER_PAGE = 10

@blogs_blueprint.route("/blog", methods=["GET"])
def blogs_page():
    query = request.args.to_dict()
    search = query.get("search", "").strip()
    sort_by = query.get("sort", "newest").strip()


    raw_data = blog_utils.search_blogs(search) if search else blog_utils.load_blogs()
    

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

    # 4. Apply Helpers
    if query.get("start_date") or query.get("end_date"):
        blog_list = blog_helpers.filter_by_date_range(blog_list, query.get("start_date"), query.get("end_date"))
    
    if query.get("reading_time"):
        blog_list = blog_helpers.filter_by_reading_time(blog_list, query["reading_time"])

    # 5. Final Sort
    blog_list = blog_helpers.sort_blogs(blog_list, sort_by)


    return render_template(
        "blogs.jinja-html",
        blogs=blog_list,
        settings = get_settings("blog_config"),
        total_count=len(blog_list),
        **query 
    )

@blogs_blueprint.route("/blog/<blog_id>", methods=["GET"])
def blog(blog_id):
    logger.info(f"Blog route accessed for blog ID: {blog_id}")
    if not blog_id:
        logger.warning("No blog ID provided, aborting with 400")
        abort(400, description="Blog ID is required")
    blog_data = blog_utils.get_item_by_id(blog_id)
    if not blog_data:
        logger.warning(f"Blog with ID {blog_id} not found, aborting with 404")
        abort(404, description="Blog not found")
    return render_template("blog.jinja-html", blog=blog_data, id=blog_id)
