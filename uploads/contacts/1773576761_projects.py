import json
import os
from typing import Any, List, Union, Optional, TypedDict
from functools import lru_cache

class Project(TypedDict):
    id: Union[int, str]
    title: str
    description_short: str
    description_full: str
    image_url: str
    github_url: Optional[str]
    live_url: Optional[str]
    time_created: int
    tags: List[str]
    tech_stack: List[str]
    category: str

DATA_FILE: str = "data/projects.json"

@lru_cache(maxsize=1)
def load_projects() -> List[Project]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

@lru_cache(maxsize=128)
def get_project_by_id(project_id: Union[int, str]) -> Optional[Project]:
    projects = load_projects()
    str_id = str(project_id)
    return next((p for p in projects if str(p.get("id")) == str_id), None)

def search_projects(search_query: str) -> List[Project]:
    projects = load_projects()
    if not search_query or not search_query.strip():
        return projects

    query_lower = search_query.lower().strip()
    results: List[Project] = []

    for project in projects:
        searchable_fields = [
            project.get("title", ""),
            project.get("description_short", ""),
            project.get("description_full", ""),
            " ".join(project.get("tech_stack", []))
        ]
        
        if any(query_lower in field.lower() for field in searchable_fields):
            results.append(project)
            
    return results


def query_projects(limit: int = 10, exclude_id: Optional[Any] = None, **criteria) -> List[Project]:
    project_list: List[Project] = load_projects()

    filtered_results: List[Project] = []
    
    for project in project_list:
        if exclude_id is not None and project.get("id") == exclude_id:
            continue

        is_match: bool = True
        for key, target_value in criteria.items():
            if key not in project:
                is_match = False
                break
                
            current_val = project[key]
            
            if isinstance(current_val, list):
                if isinstance(target_value, list):
                    if not any(item in current_val for item in target_value):
                        is_match = False
                else:
                    if target_value not in current_val:
                        is_match = False
            elif str(current_val) != str(target_value):
                is_match = False
                
            if not is_match:
                break
        
        if is_match:
            filtered_results.append(project)

    return filtered_results[:limit]