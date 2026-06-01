# ========== IMPORTS ==========
from typing import Any, Dict, List

from math import ceil
from urllib.parse import urlencode

from flask import Blueprint, render_template, abort, request, session, current_app
from flask.typing import ResponseReturnValue

from utility.blogs import BlogPost, search_blogs, sort_blogs, query_blogs, get_item_by_id, filter_by_date_range
from utility.settings import get_settings
from utility.logging_utility import logger, log_with_user
from utility.users import get_user_by_username, load_users
from utility.auth import AuthManager, Permission

# ========== BLUEPRINT INITIALIZATION ==========
blogs_blueprint = Blueprint("blogs", __name__)

# ========== CONSTANTS ==========
BLOGS_PER_PAGE = 10

# ========== ROUTES ==========
@blogs_blueprint.route("/blog", methods=["GET"])
def blogs_page() -> ResponseReturnValue:
    query: Dict[str, Any] = request.args.to_dict()
    
    search: str = query.pop("search", "").strip()
    sort_by: str = query.pop("sort", "newest").strip()

    try:
        page: int = int(query.pop("page", 1))
    except (TypeError, ValueError):
        page = 1
    if page < 1:
        page = 1

    if "tags" in query:
        query["tags"] = [tag.strip() for tag in query["tags"].split(",") if tag.strip()]

    if "category" in query:
        query["categories"] = query.pop("category")

    blog_list: List[BlogPost] = search_blogs(search) if search else query_blogs(limit=None, status="visible", **query)

    start_date = query.pop("start_date", None)
    end_date = query.pop("end_date", None)
    if start_date or end_date:
        blog_list = filter_by_date_range(blog_list, start_date, end_date)

    blog_list = sort_blogs(blog_list, sort_by)

    total_count: int = len(blog_list)
    total_pages: int = ceil(total_count / BLOGS_PER_PAGE) if total_count else 1
    start: int = (page - 1) * BLOGS_PER_PAGE
    end: int = start + BLOGS_PER_PAGE
    paginated = blog_list[start:end]

    base_query = {k: v for k, v in request.args.items() if k != "page"}
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
def blog(blog_id: str) -> ResponseReturnValue:
    logger.info(f"Blog route accessed for blog ID: {blog_id}")
    if not blog_id:
        logger.warning("No blog ID provided, aborting with 400")
        abort(400, description="Blog ID is required")
    blog_data = get_item_by_id(blog_id)
    if not blog_data:
        logger.warning(f"Blog with ID {blog_id} not found, aborting with 404")
        abort(404, description="Blog not found")

    status = (blog_data.get("status") or "").lower()
    if status in ("draft", "hidden"):
        user_id = session.get("user_id")
        if not user_id or not AuthManager.has_permission(user_id, Permission.BLOGS_READ):
            logger.warning(f"Unauthorized access to {blog_id} - requires blogs:read")
            abort(403, description="Forbidden")

    author_profiles: Dict[str, str | None] = {}
    for name in blog_data.get("authors", []):
        author_profiles[name] = get_user_by_username(name).get("profile_picture_url") if name else None #type: ignore
    return render_template(
        "blog.jinja",
        blog=blog_data,
        id=blog_id,
        author_profiles=author_profiles,
        suggestions=query_blogs(
            categories=blog_data.get("categories", []),
            status="visible",
            limit=3,
            exclude_id=blog_id
        )
    )