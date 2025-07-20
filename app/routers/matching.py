from typing import List, Optional
from fastapi import APIRouter, HTTPException, Path, Query, Depends

from app.dependencies import get_algorithm
from app.models.responses import MatchScoreResponse, TeamReportResponse
from team_matching.algorithm import TeamMatchingAlgorithm

router = APIRouter()

@router.get("/{project_id}/matches", response_model=List[MatchScoreResponse])
async def get_project_matches(
    project_id: str = Path(..., description="Project ID"),
    limit: Optional[int] = Query(None, ge=1, description="Limit number of results"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum match score"),
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Get all potential team members for a project with their match scores"""
    project = next((p for p in algo.projects if p.id == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    
    try:
        # Calculate scores for all members
        member_scores = []
        for member in algo.members:
            match_score = algo.calculate_member_match_score(member, project)
            if min_score is None or match_score.total_score >= min_score:
                member_scores.append((match_score, member))
        
        # Sort by total score
        member_scores.sort(key=lambda x: x[0].total_score, reverse=True)
        
        # Apply limit if specified
        if limit:
            member_scores = member_scores[:limit]
        
        # Convert to response format
        matches = []
        for match_score, member in member_scores:
            match_response = MatchScoreResponse(
                member_id=match_score.member_id,
                member_name=member.name,
                total_score=round(match_score.total_score, 2),
                skill_match_score=round(match_score.skill_match_score, 2),
                availability_score=round(match_score.availability_score, 2),
                experience_score=round(match_score.experience_score, 2),
                cost_score=round(match_score.cost_score, 2),
                location_score=round(match_score.location_score, 2),
                certification_score=round(match_score.certification_score, 2),
                detailed_breakdown=match_score.detailed_breakdown
            )
            matches.append(match_response)
        
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating matches: {str(e)}")

@router.get("/{project_id}/best-team", response_model=List[MatchScoreResponse])
async def get_best_team_for_project(
    project_id: str = Path(..., description="Project ID"),
    team_size: Optional[int] = Query(None, ge=1, description="Override project team size"),
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Get the best team for a specific project"""
    try:
        best_team = algo.find_best_team_for_project(project_id, team_size)
        
        # Convert to response format
        team_matches = []
        for match_score in best_team:
            member = next((m for m in algo.members if m.id == match_score.member_id), None)
            if member:
                match_response = MatchScoreResponse(
                    member_id=match_score.member_id,
                    member_name=member.name,
                    total_score=round(match_score.total_score, 2),
                    skill_match_score=round(match_score.skill_match_score, 2),
                    availability_score=round(match_score.availability_score, 2),
                    experience_score=round(match_score.experience_score, 2),
                    cost_score=round(match_score.cost_score, 2),
                    location_score=round(match_score.location_score, 2),
                    certification_score=round(match_score.certification_score, 2),
                    detailed_breakdown=match_score.detailed_breakdown
                )
                team_matches.append(match_response)
        
        return team_matches
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding best team: {str(e)}")

@router.get("/{project_id}/team-report", response_model=TeamReportResponse)
async def get_team_report(
    project_id: str = Path(..., description="Project ID"),
    team_size: Optional[int] = Query(None, ge=1, description="Override project team size"),
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Get a detailed team report for a project"""
    try:
        best_team = algo.find_best_team_for_project(project_id, team_size)
        report = algo.generate_team_report(project_id, best_team)
        
        return TeamReportResponse(**report)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating team report: {str(e)}")