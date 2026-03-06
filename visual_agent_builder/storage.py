import json
import os
from typing import List, Dict, Any

STORAGE_FILE = "projects.json"

def load_projects() -> List[Dict[str, Any]]:
    """Loads all projects from the storage file."""
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_projects(projects: List[Dict[str, Any]]):
    """Saves all projects to the storage file."""
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=4)

def get_project(project_id: str) -> Dict[str, Any]:
    projects = load_projects()
    for p in projects:
        if p["id"] == project_id:
            return p
    return None

def create_project(name: str, description: str):
    projects = load_projects()
    new_id = str(len(projects) + 1)
    new_project = {
        "id": new_id,
        "name": name,
        "description": description,
        "nodes": [],
        "edges": []
    }
    projects.append(new_project)
    save_projects(projects)
    return new_project

def delete_project(project_id: str):
    projects = load_projects()
    projects = [p for p in projects if p["id"] != project_id]
    save_projects(projects)

def save_flow(project_id: str, nodes: List[Dict], edges: List[Dict]):
    projects = load_projects()
    for p in projects:
        if p["id"] == project_id:
            p["nodes"] = nodes
            p["edges"] = edges
            break
    save_projects(projects)
