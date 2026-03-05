import json
import os
from typing import List, Union, Optional, TypedDict
from functools import lru_cache

class BlogPost(TypedDict):
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
def load_blogs() -> list[BlogPost]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

@lru_cache(maxsize=128)
def get_item_by_id(blog_id: Union[int, str]) -> Optional[BlogPost]:
    blogs = load_blogs()
    str_id = str(blog_id)
    for post in blogs:
        if str(post.get("id")) == str_id:
            return post
    return None

def search_blogs(search_query: str) -> List[BlogPost]:
    blogs = load_blogs()
    if not search_query or not search_query.strip():
        return blogs
    query_lower = search_query.lower()
    results: List[BlogPost] = []
    for blog in blogs:
        if query_lower in blog.get("title", "").lower() or \
           query_lower in blog.get("content_raw", "").lower():
            results.append(blog)
    return results

def query_blogs(**criteria) -> List[BlogPost]:
    blog_list: List[BlogPost] = load_blogs()
    
    if not criteria:
        return blog_list

    filtered_results: List[BlogPost] = []
    
    for blog in blog_list:
        is_match: bool = True
        for key, target_value in criteria.items():
            if key not in blog:
                is_match = False
                break
                
            current_val = blog[key]
            
            if isinstance(current_val, list):
                if isinstance(target_value, list):
                    if not any(item in current_val for item in target_value):
                        is_match = False
                else:
                    if target_value not in current_val:
                        is_match = False
            elif current_val != target_value:
                is_match = False
                
            if not is_match:
                break
        
        if is_match:
            filtered_results.append(blog)
            
    return filtered_results


