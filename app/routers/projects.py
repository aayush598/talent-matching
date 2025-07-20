from typing import List
from fastapi import APIRouter, HTTPException, Path, Depends

from app.dependencies import get_algorithm
from app.models.requests import ProjectRequest
from app.models.responses import ProjectResponse
from app.utils.converters import (
    convert_project_to_model, 
    convert_project_to_response
)
from team_matching.algorithm import TeamMatchingAlgorithm

router = APIRouter()

@router.post("", response_model=dict, status_code=201)
async def add_project(
    project: ProjectRequest, 
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Add a new project"""
    try:
        # Check if project already exists
        existing_project = next((p for p in algo.projects if p.id == project.id), None)
        if existing_project:
            raise HTTPException(status_code=400, detail=f"Project with ID {project.id} already exists")
        
        project_model = convert_project_to_model(project)
        algo.add_project(project_model)
        
        return {"message": f"Project {project.name} added successfully", "project_id": project.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[ProjectResponse])
async def get_all_projects(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get all projects"""
    return [convert_project_to_response(project) for project in algo.projects]

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(
    project_id: str = Path(..., description="Project ID"), 
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Get a specific project by ID"""
    project = next((p for p in algo.projects if p.id == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    
    return convert_project_to_response(project)