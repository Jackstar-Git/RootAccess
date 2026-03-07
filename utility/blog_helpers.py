from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from .blogs import BlogPost

def filter_by_date_range(blog_list: List[BlogPost], start_date: Optional[str], end_date: Optional[str]) -> List[BlogPost]:
    if not start_date and not end_date:
        return blog_list

    start_ts: Optional[int] = None
    end_ts: Optional[int] = None

    if start_date:
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        except ValueError:
            pass

    if end_date:
        try:
            dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            end_ts = int(dt.timestamp())
        except ValueError:
            pass

    filtered: List[BlogPost] = []
    for blog in blog_list:
        t: int = blog.get("time_created", 0)
        if start_ts and t < start_ts:
            continue
        if end_ts and t > end_ts:
            continue
        filtered.append(blog)

    return filtered

def calculate_reading_time(content: str) -> int:
    words_per_minute: int = 200
    word_count: int = len(content.split())
    return max(1, word_count // words_per_minute)

def filter_by_reading_time(blog_list: List[BlogPost], reading_time: Optional[str]) -> List[BlogPost]:
    if not reading_time:
        return blog_list

    filtered: List[BlogPost] = []
    for blog in blog_list:
        content: str = blog.get("content_raw", "")
        minutes: int = calculate_reading_time(content)
        
        is_short: bool = reading_time == "short" and minutes < 5
        is_medium: bool = reading_time == "medium" and 5 <= minutes <= 15
        is_deep: bool = reading_time == "deep" and minutes > 15
        
        if is_short or is_medium or is_deep:
            filtered.append(blog)
            
    return filtered

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