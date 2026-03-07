import json
import os
from typing import List, Union, Optional, TypedDict, Any
from functools import lru_cache

class BlogPost(TypedDict):
    id: Union[int, str]
    author: Union[str, List[str]]
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
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@lru_cache(maxsize=128)
def get_item_by_id(blog_id: Union[int, str]) -> Optional[BlogPost]:
    blogs: List[BlogPost] = load_blogs()
    str_id: str = str(blog_id)
    return next((post for post in blogs if str(post.get("id")) == str_id), None)

def search_blogs(search_query: str) -> List[BlogPost]:
    blogs: List[BlogPost] = load_blogs()
    if not search_query or not search_query.strip():
        return blogs
    
    query: str = search_query.lower()
    return [
        b for b in blogs 
        if query in b.get("title", "").lower() or query in b.get("content_raw", "").lower()
    ]

def query_blogs(limit: int = 10, exclude_id: Optional[Any] = None, **criteria: Any) -> List[BlogPost]:
    blog_list: List[BlogPost] = load_blogs()
    filtered_results: List[BlogPost] = []

    for blog in blog_list:
        if exclude_id is not None and blog.get("id") == exclude_id:
            continue

        is_match: bool = True
        for key, target in criteria.items():
            current = blog.get(key)
            
            if isinstance(current, list):
                if isinstance(target, list):
                    if not any(item in current for item in target):
                        is_match = False
                elif target not in current:
                    is_match = False
            elif current != target:
                is_match = False

            if not is_match:
                break

        if is_match:
            filtered_results.append(blog)

    return filtered_results[:limit]