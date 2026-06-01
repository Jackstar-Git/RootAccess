import json
import os
import time
from typing import List, Union, Optional, TypedDict, Any, Dict, Tuple, Literal
from functools import lru_cache
import uuid
from .converter import MarkdownConverter

class Project(TypedDict):
    id: str
    title: str
    version: str
    description_short: str
    content_raw: str
    content_html: str
    image_url: Optional[str]
    github_url: Optional[str]
    demo_url: Optional[str]
    tech_stack: List[str]
    time_created: int
    last_updated: int
    tags: List[str]
    maturity: str
    activity: str
    topic: str
    download_file: Optional[str]

DATA_FILE: str = "data/projects.json"


# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def _build_default_project_payload(project: Dict[str, Any] | Project) -> Project:
    return {
        "id": str(project["id"]) if project.get("id") is not None else "",
        "title": project.get("title", ""),
        "version": project.get("version", "1.0.0"),
        "description_short": project.get("description_short", ""),
        "content_raw": project.get("content_raw", ""),
        "content_html": project.get("content_html", ""),
        "image_url": project.get("image_url", None),
        "github_url": project.get("github_url", None),
        "demo_url": project.get("demo_url", None),
        "tech_stack": project.get("tech_stack", []),
        "time_created": project.get("time_created", 0),
        "last_updated": project.get("last_updated", 0),
        "tags": project.get("tags", []),
        "maturity": project.get("maturity", "MVP"),
        "activity": project.get("activity", "Active"),
        "topic": project.get("topic", "Personal"),
        "download_file": project.get("download_file", None)
    }

def _save_and_refresh_cache(projects: List[Project]) -> None:
    normalized_projects = [_build_default_project_payload(project) for project in projects]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(normalized_projects, f, indent=4, ensure_ascii=False)
    
    load_projects.cache_clear()
    get_project_by_id.cache_clear()


# ==========================================
# 2. CORE CRUD OPERATIONS
# ==========================================

@lru_cache(maxsize=1)
def load_projects() -> List[Project]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [_build_default_project_payload(item) for item in data]
            return []
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []

@lru_cache(maxsize=128)
def get_project_by_id(project_id: Union[int, str]) -> Optional[Project]:
    projects: List[Project] = load_projects()
    str_id: str = str(project_id)
    return next((p for p in projects if str(p.get("id")) == str_id), None)

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
    new_project["content_html"] = MarkdownConverter.quick_convert(raw_content)
    
    full_project_payload: Dict[str, Any] = {
        "id": new_project["id"],
        "title": new_project.get("title", ""),
        "version": new_project.get("version", "1.0.0"),
        "description_short": new_project.get("description_short", ""),
        "content_raw": raw_content,
        "content_html": new_project["content_html"],
        "image_url": new_project.get("image_url", None),
        "github_url": new_project.get("github_url", None),
        "demo_url": new_project.get("demo_url", None),
        "tech_stack": new_project.get("tech_stack", []),
        "time_created": new_project.get("time_created", now),
        "last_updated": now,
        "tags": new_project.get("tags", []),
        "maturity": new_project.get("maturity", "MVP"),
        "activity": new_project.get("activity", "Active"),
        "topic": new_project.get("topic", "Personal"),
        "download_file": new_project.get("download_file", None)
    }

    final_project = _build_default_project_payload(full_project_payload)
    projects.append(final_project)
    _save_and_refresh_cache(projects)
    return final_project

def update_project(project_id: Union[int, str], updated_data: Dict[str, Any]) -> bool:
    projects: List[Project] = load_projects()
    str_id: str = str(project_id)
    
    for i, project in enumerate(projects):
        if str(project.get("id")) == str_id:
            updated_data.pop("id", None)
            updated_data.pop("time_created", None)
            
            if "content_raw" in updated_data:
                updated_data["content_html"] = MarkdownConverter.quick_convert(updated_data["content_raw"])

            merged_payload = dict(project)
            merged_payload.update(updated_data)
            merged_payload["last_updated"] = int(time.time())
            
            projects[i] = _build_default_project_payload(merged_payload)
            _save_and_refresh_cache(projects)
            return True
    
    return False

def delete_project(project_id: Union[int, str]) -> bool:
    projects: List[Project] = load_projects()
    str_id: str = str(project_id)
    
    new_list = [p for p in projects if str(p.get("id")) != str_id]
    if len(new_list) < len(projects):
        _save_and_refresh_cache(new_list)
        return True
    return False


# ==========================================
# 3. OTHER OPERATIONS (SEARCH, FILTER, UTILS)
# ==========================================

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