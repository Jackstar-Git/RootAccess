import json
import os
import time
from typing import List, Union, Optional, TypedDict, Any, Dict, Literal, Tuple
from functools import lru_cache
import uuid
from .converter import MarkdownConverter

class BlogPost(TypedDict):
    id: str
    status: Literal["visible", "draft", "hidden"]
    type: str
    title: str
    description: Optional[str]
    authors: List[str]
    image_url: Optional[str]
    content_raw: str
    content_html: str
    categories: List[str]
    tags: List[str]
    reading_time: Literal["short", "medium", "deep"]
    time_created: int
    last_modified: int
    scheduled_time: Optional[int]

DATA_FILE: str = "data/blogs.json"


# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def _build_default_blog_payload(blog: Dict[str, Any] | BlogPost) -> BlogPost:
    return {
        "id": str(blog["id"]) if blog.get("id") is not None else "",
        "status": blog.get("status", "draft"),
        "type": blog.get("type", "post"),
        "title": blog.get("title", ""),
        "description": blog.get("description", None),
        "authors": blog.get("authors", []),
        "image_url": blog.get("image_url", None),
        "content_raw": blog.get("content_raw", ""),
        "content_html": blog.get("content_html", ""),
        "categories": blog.get("categories", []),
        "tags": blog.get("tags", []),
        "reading_time": blog.get("reading_time", "short"),
        "time_created": blog.get("time_created", 0),
        "last_modified": blog.get("last_modified", 0),
        "scheduled_time": blog.get("scheduled_time", None)
    }

def _save_and_refresh_cache(blogs: List[BlogPost]) -> None:
    normalized_blogs = [_build_default_blog_payload(blog) for blog in blogs]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(normalized_blogs, f, indent=4, ensure_ascii=False)
    
    load_blogs.cache_clear()
    get_item_by_id.cache_clear()

def calculate_reading_time(content: str) -> Literal["short", "medium", "deep"]:
    words_per_minute: int = 150
    word_count: int = len(content.split())
    estimated_minutes = word_count / words_per_minute
    
    if estimated_minutes < 3:
        return "short"
    elif estimated_minutes <= 7:
        return "medium"
    else:
        return "deep"


# ==========================================
# 2. CORE CRUD OPERATIONS
# ==========================================

@lru_cache(maxsize=1)       
def load_blogs() -> List[BlogPost]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [_build_default_blog_payload(item) for item in data]
            return []
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []

@lru_cache(maxsize=128)
def get_item_by_id(blog_id: Union[int, str]) -> Optional[BlogPost]:
    blogs: List[BlogPost] = load_blogs()
    str_id: str = str(blog_id)
    return next((post for post in blogs if str(post.get("id")) == str_id), None)

def add_blog(new_blog: Dict[str, Any]) -> BlogPost:
    blogs: List[BlogPost] = load_blogs()
    now = int(time.time())

    # ID validation/generation
    if not new_blog.get("id"):
        existing_ids = {str(b.get("id")) for b in blogs}
        while (candidate := uuid.uuid4().hex[:8]) in existing_ids:
            pass
        new_blog["id"] = candidate
    else:
        new_blog["id"] = str(new_blog["id"])

    authors_input = new_blog.get("authors", new_blog.get("author", []))
    if isinstance(authors_input, str):
        new_blog["authors"] = [authors_input]
    elif isinstance(authors_input, list):
        new_blog["authors"] = [str(a) for a in authors_input]
    else:
        new_blog["authors"] = []
    
    raw_content = new_blog.get("content_raw", "")
    new_blog["content_html"] = MarkdownConverter.quick_convert(raw_content)
    new_blog["reading_time"] = calculate_reading_time(raw_content)
    
    full_blog_payload: Dict[str, Any] = {
        "id": new_blog["id"],
        "status": new_blog.get("status", "draft"),
        "type": new_blog.get("type", "post"),
        "title": new_blog.get("title", ""),
        "description": new_blog.get("description", None),
        "authors": new_blog["authors"],
        "image_url": new_blog.get("image_url", None),
        "content_raw": raw_content,
        "content_html": new_blog["content_html"],
        "categories": new_blog.get("categories", []),
        "tags": new_blog.get("tags", []),
        "reading_time": new_blog["reading_time"],
        "time_created": new_blog.get("time_created", now),
        "last_modified": now,
        "scheduled_time": new_blog.get("scheduled_time", None)
    }

    final_blog = _build_default_blog_payload(full_blog_payload)
    blogs.append(final_blog) 
    _save_and_refresh_cache(blogs)
    return final_blog

def update_blog(blog_id: Union[int, str], updated_data: Dict[str, Any]) -> bool:
    blogs: List[BlogPost] = load_blogs()
    str_id: str = str(blog_id)
    
    for i, post in enumerate(blogs):
        if str(post.get("id")) == str_id:
            updated_data.pop("id", None)
            updated_data.pop("time_created", None)
            
            if "authors" in updated_data and isinstance(updated_data["authors"], str):
                updated_data["authors"] = [updated_data["authors"]]

            if "content_raw" in updated_data:
                updated_data["content_html"] = MarkdownConverter.quick_convert(updated_data["content_raw"])
                updated_data["reading_time"] = calculate_reading_time(updated_data["content_raw"])

            merged_payload = dict(post)
            merged_payload.update(updated_data)
            merged_payload["last_modified"] = int(time.time())
            
            blogs[i] = _build_default_blog_payload(merged_payload)
            _save_and_refresh_cache(blogs)
            return True
    return False

def delete_blog(blog_id: Union[int, str]) -> bool:
    blogs: List[BlogPost] = load_blogs()
    str_id: str = str(blog_id)
    
    new_list = [p for p in blogs if str(p.get("id")) != str_id]
    if len(new_list) < len(blogs):
        _save_and_refresh_cache(new_list)
        return True
    return False


# ==========================================
# 3. OTHER OPERATIONS (SEARCH, FILTER, UTILS)
# ==========================================

def search_blogs(search_query: str) -> List[BlogPost]:
    blogs: List[BlogPost] = load_blogs()
    if not search_query or not search_query.strip():
        return blogs
    
    query: str = search_query.lower()
    def is_visible_for_search(b: BlogPost) -> bool:
        status = b.get("status") or "draft"
        return status.lower() not in ("draft", "hidden")

    return [
        b for b in blogs 
        if is_visible_for_search(b) and (query in b.get("title", "").lower() or query in b.get("content_raw", "").lower())
    ]

def query_blogs(limit: Optional[int] = 10, exclude_id: Optional[Any] = None, match_mode: Literal["AND", "OR"] = "AND", **criteria: Any) -> List[BlogPost]:
    blog_list: List[BlogPost] = load_blogs()
    filtered_results: List[BlogPost] = []

    for blog in blog_list:
        if exclude_id is not None and blog.get("id") == exclude_id:
            continue

        if not criteria:
            filtered_results.append(blog)
            continue

        matches = []
        for key, target in criteria.items():
            current = blog.get(key)
            item_match = False
            
            if isinstance(current, list):
                if isinstance(target, list):
                    item_match = any(item in current for item in target)
                else:
                    item_match = target in current
            else:
                item_match = (current == target)
            
            matches.append(item_match)

        is_match = all(matches) if match_mode == "AND" else any(matches)

        if is_match:
            filtered_results.append(blog)

    return filtered_results[:limit]

def sort_blogs(blog_list: List[BlogPost], sort_by: str) -> List[BlogPost]:
    reverse_order: bool = sort_by != "oldest"
    return sorted(
        blog_list, 
        key=lambda x: x.get("time_created", 0), 
        reverse=reverse_order
    )

def paginate_blogs(blog_list: List[BlogPost], offset: int, per_page: int) -> Tuple[List[BlogPost], bool, int, int]:
    total: int = len(blog_list)
    page_slice: List[BlogPost] = blog_list[offset : offset + per_page]
    has_more: bool = (offset + per_page) < total
    next_offset: int = offset + per_page
    
    return page_slice, has_more, next_offset, total

def filter_by_date_range(*args) -> Any:
    pass