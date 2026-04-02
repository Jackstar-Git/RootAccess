import json
import os
import time
from typing import List, Union, Optional, TypedDict, Any, Dict, Tuple, Literal
from functools import lru_cache
import uuid
import math
from .others import convert_markdown_to_html

class Project(TypedDict):
    id: str
    title: str
    version: str
    description_short: str
    content_raw: str
    content_html: str
    image_url: str
    github_url: Optional[str]
    demo_url: Optional[str]
    download_file: Optional[str]
    time_created: int
    last_updated: int
    tags: List[str]
    tech_stack: List[str]
    topic: str
    maturity: str
    activity: str

DATA_FILE: str = "data/projects.json"


@lru_cache(maxsize=1)
def load_projects() -> List[Project]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []


@lru_cache(maxsize=128)
def get_project_by_id(project_id: Union[int, str]) -> Optional[Project]:
    projects: List[Project] = load_projects()
    str_id: str = str(project_id)
    return next((p for p in projects if str(p.get("id")) == str_id), None)


def _save_and_refresh_cache(projects: List[Project]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=4, ensure_ascii=False)
    
    load_projects.cache_clear()
    get_project_by_id.cache_clear()


def add_project(new_project: Dict[str, Any]) -> Project:
    projects: List[Project] = load_projects()
    now = int(time.time())

    # Generate unique ID if not provided
    if not new_project.get("id"):
        existing_ids = {str(p.get("id")) for p in projects}
        while (candidate := uuid.uuid4().hex[:8]) in existing_ids:
            pass
        new_project["id"] = candidate
    else:
        new_project["id"] = str(new_project["id"])

    # Convert markdown content to HTML
    raw_content = new_project.get("content_raw", "")
    new_project["content_html"] = convert_markdown_to_html(raw_content)

    # Set defaults
    new_project.setdefault("tags", [])
    new_project.setdefault("tech_stack", [])
    new_project.setdefault("topic", "Personal")
    new_project.setdefault("maturity", "MVP")
    new_project.setdefault("activity", "Active")
    new_project.setdefault("version", "1.0.0")
    new_project.setdefault("time_created", now)
    new_project["last_updated"] = now

    projects.append(new_project)
    _save_and_refresh_cache(projects)
    return new_project


def update_project(project_id: Union[int, str], updated_data: Dict[str, Any]) -> bool:
    """Update an existing project with markdown to HTML conversion"""
    projects: List[Project] = load_projects()
    str_id: str = str(project_id)
    
    for i, project in enumerate(projects):
        if str(project.get("id")) == str_id:
            # Remove protected fields
            updated_data.pop("id", None)
            updated_data.pop("time_created", None)
            
            # Convert markdown if content is being updated
            if "content_raw" in updated_data:
                updated_data["content_html"] = convert_markdown_to_html(updated_data["content_raw"])

            projects[i].update(updated_data)
            projects[i]["last_updated"] = int(time.time())
            
            _save_and_refresh_cache(projects)
            return True
    
    return False


def delete_project(project_id: Union[int, str]) -> bool:
    """Delete a project by ID"""
    projects: List[Project] = load_projects()
    str_id: str = str(project_id)
    
    new_list = [p for p in projects if str(p.get("id")) != str_id]
    if len(new_list) < len(projects):
        _save_and_refresh_cache(new_list)
        return True
    return False


def search_projects(search_query: str) -> List[Project]:
    projects: List[Project] = load_projects()
    if not search_query or not search_query.strip():
        return projects
    
    query: str = search_query.lower()
    return [
        p for p in projects 
        if query in p.get("title", "").lower() 
        or query in p.get("description_short", "").lower()
        or query in p.get("content_raw", "").lower()
        or any(query in tech.lower() for tech in p.get("tech_stack", []))
    ]


def query_projects(limit: int = 10, exclude_id: Optional[Any] = None, match_mode: Literal["AND", "OR"] = "AND", **criteria: Any) -> List[Project]:
    project_list: List[Project] = load_projects()
    filtered_results: List[Project] = []

    for project in project_list:
        if exclude_id is not None and project.get("id") == exclude_id:
            continue

        if not criteria:
            filtered_results.append(project)
            continue

        matches = []
        for key, target in criteria.items():
            current = project.get(key)
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
            filtered_results.append(project)

    return filtered_results[:limit]


def sort_projects(projects_list: List[Project], sort_by: str) -> List[Project]:
    reverse_order: bool = sort_by != "oldest"
    return sorted(
        projects_list, 
        key=lambda x: x.get("time_created", 0), 
        reverse=reverse_order
    )


def paginate_projects(project_list: List[Project], offset: int, per_page: int) -> Tuple[List[Project], bool, int, int]:
    total: int = len(project_list)
    page_slice: List[Project] = project_list[offset : offset + per_page]
    has_more: bool = (offset + per_page) < total
    next_offset: int = offset + per_page
    
    return page_slice, has_more, next_offset, total
