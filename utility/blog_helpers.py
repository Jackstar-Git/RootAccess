from datetime import datetime
from typing import List, Dict, Any, Tuple

from .data.blogs import BlogPost


def filter_by_date_range(blog_list: List[BlogPost], start_date: str | None, end_date: str | None) -> List[BlogPost]:
    """Return only blogs whose ``time_created`` falls within ``start_date``/``end_date``.

    Dates must use the ISO format YYYY-MM-DD.  If either boundary is ``None`` the
    corresponding check is skipped.
    """
    if not start_date and not end_date:
        return blog_list

    start_ts = None
    end_ts = None

    if start_date:
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        except ValueError:
            pass

    if end_date:
        try:
            dt = datetime.strptime(end_date, "%Y-%m-%d")
            dt = dt.replace(hour=23, minute=59, second=59)
            end_ts = int(dt.timestamp())
        except ValueError:
            pass

    filtered = []
    for blog in blog_list:
        t = blog.get("time_created", 0)
        if start_ts and t < start_ts:
            continue
        if end_ts and t > end_ts:
            continue
        filtered.append(blog)
    return filtered


def calculate_reading_time(content: str) -> int:
    """Estimate reading time (minutes) based on a 200 wpm average."""
    return max(1, len(content.split()) // 200)


def filter_by_reading_time(blog_list: List[BlogPost], reading_time: str) -> List[BlogPost]:
    """Return blogs matching a coarse reading-time bucket."""
    if not reading_time:
        return blog_list
    filtered = []
    for blog in blog_list:
        minutes = calculate_reading_time(blog.get("content_raw", ""))
        if reading_time == "short" and minutes < 5:
            filtered.append(blog)
        elif reading_time == "medium" and 5 <= minutes <= 15:
            filtered.append(blog)
        elif reading_time == "deep" and minutes > 15:
            filtered.append(blog)
    return filtered


def sort_blogs(blog_list: List[BlogPost], sort_by: str) -> List[BlogPost]:
    """Sort blogs newest-first (default) or oldest-first."""
    reverse = sort_by != "oldest"
    return sorted(blog_list, key=lambda x: x.get("time_created", 0), reverse=reverse)


def paginate_blogs(blog_list: List[BlogPost], offset: int, per_page: int) -> Tuple[List[BlogPost], bool, int, int]:
    """Return a slice of ``blog_list`` plus paging metadata.

    ``(page, has_more, next_offset, total)``
    """
    total = len(blog_list)
    page = blog_list[offset:offset + per_page]
    has_more = (offset + per_page) < total
    next_offset = offset + per_page
    return page, has_more, next_offset, total


