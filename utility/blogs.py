import json
import os
import time
from typing import List, Union, Optional, TypedDict, Any, Dict
from functools import lru_cache
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from .others import convert_markdown_to_html
import math

class BlogPost(TypedDict):
    id: str
    author: List[str] 
    title: str
    content_raw: str
    image_url: str
    time_created: int
    last_modified: int
    tags: List[str]
    categories: List[str]

DATA_FILE: str = "data/blogs.json"


@lru_cache(maxsize=1)
def load_blogs() -> List[BlogPost]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []

@lru_cache(maxsize=128)
def get_item_by_id(blog_id: Union[int, str]) -> Optional[BlogPost]:
    blogs: List[BlogPost] = load_blogs()
    str_id: str = str(blog_id)
    return next((post for post in blogs if str(post.get("id")) == str_id), None)

def _save_and_refresh_cache(blogs: List[BlogPost]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(blogs, f, indent=4, ensure_ascii=False)
    
    load_blogs.cache_clear()
    get_item_by_id.cache_clear()

def add_blog(new_blog: Dict[str, Any]) -> BlogPost:
    blogs: List[BlogPost] = load_blogs()
    now = int(time.time())

    if not new_blog.get("id"):
        existing_ids = {str(b.get("id")) for b in blogs}
        while (candidate := uuid.uuid4().hex[:8]) in existing_ids:
            pass
        new_blog["id"] = candidate
    else:
        new_blog["id"] = str(new_blog["id"])

    if isinstance(new_blog.get("author"), str):
        new_blog["author"] = [new_blog["author"]]
    
    raw_content = new_blog.get("content_raw", "")
    new_blog["content_html"] = convert_markdown_to_html(raw_content)

    new_blog.setdefault("tags", [])
    new_blog.setdefault("categories", [])
    new_blog.setdefault("time_created", now)
    new_blog["last_modified"] = now
    new_blog["calc_read_time"] = calculate_reading_time(new_blog["content_raw"])


    blogs.append(new_blog) 
    _save_and_refresh_cache(blogs)
    return new_blog

def update_blog(blog_id: Union[int, str], updated_data: Dict[str, Any]) -> bool:
    blogs: List[BlogPost] = load_blogs()
    str_id: str = str(blog_id)
    
    for i, post in enumerate(blogs):
        if str(post.get("id")) == str_id:
            updated_data.pop("id", None)
            updated_data.pop("time_created", None)
            
            if "author" in updated_data and isinstance(updated_data["author"], str):
                updated_data["author"] = [updated_data["author"]]

            # Automatically update HTML if the raw content is being changed
            if "content_raw" in updated_data:
                updated_data["content_html"] = convert_markdown_to_html(updated_data["content_raw"])
                updated_data["calc_read_time"] = calculate_reading_time(updated_data["content_raw"])

                

            blogs[i].update(updated_data)
            blogs[i]["last_modified"] = int(time.time())
            
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


def search_blogs(search_query: str) -> List[BlogPost]:
    blogs: List[BlogPost] = load_blogs()
    if not search_query or not search_query.strip():
        return blogs
    
    query: str = search_query.lower()
    return [
        b for b in blogs 
        if query in b.get("title", "").lower() or query in b.get("content_raw", "").lower()
    ]

from typing import List, Optional, Any, Literal

def query_blogs(limit: int = 10, exclude_id: Optional[Any] = None, match_mode: Literal["AND", "OR"] = "AND",**criteria: Any) -> List[BlogPost]:
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

def calculate_reading_time(content: str) -> int:
    words_per_minute: int = 150
    word_count: int = len(content.split())
    return int(max(1, math.ceil(word_count / words_per_minute)))


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


