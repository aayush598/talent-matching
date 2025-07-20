from typing import List
from fastapi import APIRouter, HTTPException, Path, Depends

from app.dependencies import get_algorithm
from app.models.requests import TeamMemberRequest
from app.models.responses import TeamMemberResponse
from app.utils.converters import (
    convert_team_member_to_model, 
    convert_team_member_to_response
)
from team_matching.algorithm import TeamMatchingAlgorithm

router = APIRouter()

@router.post("", response_model=dict, status_code=201)
async def add_team_member(
    member: TeamMemberRequest, 
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Add a new team member"""
    try:
        # Check if member already exists
        existing_member = next((m for m in algo.members if m.id == member.id), None)
        if existing_member:
            raise HTTPException(status_code=400, detail=f"Member with ID {member.id} already exists")
        
        member_model = convert_team_member_to_model(member)
        algo.add_member(member_model)
        
        return {"message": f"Team member {member.name} added successfully", "member_id": member.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[TeamMemberResponse])
async def get_all_members(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get all team members"""
    return [convert_team_member_to_response(member) for member in algo.members]

@router.get("/{member_id}", response_model=TeamMemberResponse)
async def get_member_by_id(
    member_id: str = Path(..., description="Member ID"), 
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Get a specific team member by ID"""
    member = next((m for m in algo.members if m.id == member_id), None)
    if not member:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
    
    return convert_team_member_to_response(member)

@router.put("/{member_id}")
async def update_member(
    member_id: str, 
    member: TeamMemberRequest, 
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Update an existing team member"""
    existing_member_index = next((i for i, m in enumerate(algo.members) if m.id == member_id), None)
    if existing_member_index is None:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
    
    try:
        member_model = convert_team_member_to_model(member)
        algo.members[existing_member_index] = member_model
        return {"message": f"Member {member.name} updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{member_id}")
async def delete_member(
    member_id: str = Path(..., description="Member ID"), 
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Delete a team member"""
    member_index = next((i for i, m in enumerate(algo.members) if m.id == member_id), None)
    if member_index is None:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
    
    removed_member = algo.members.pop(member_index)
    return {"message": f"Member {removed_member.name} deleted successfully"}