from datetime import datetime
from fastapi import APIRouter, Depends

from app.dependencies import get_algorithm
from team_matching.algorithm import TeamMatchingAlgorithm

router = APIRouter()

@router.get("/health")
async def health_check(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "members_count": len(algo.members),
        "projects_count": len(algo.projects),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/skills/list")
async def get_all_skills(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get list of all skills across all team members"""
    skills = set()
    for member in algo.members:
        for skill in member.skills:
            skills.add(skill.name)
    return {"skills": sorted(list(skills))}

@router.get("/stats")
async def get_system_stats(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get system statistics"""
    total_skills = set()
    experience_levels = {}
    availability_status = {}
    departments = set()
    
    for member in algo.members:
        departments.add(member.department)
        
        exp_level = member.experience_level.name
        experience_levels[exp_level] = experience_levels.get(exp_level, 0) + 1
        
        avail_status = member.availability_status.name
        availability_status[avail_status] = availability_status.get(avail_status, 0) + 1
        
        for skill in member.skills:
            total_skills.add(skill.name)
    
    project_priorities = {}
    for project in algo.projects:
        priority = project.priority.name
        project_priorities[priority] = project_priorities.get(priority, 0) + 1
    
    return {
        "members": {
            "total": len(algo.members),
            "by_experience": experience_levels,
            "by_availability": availability_status,
            "departments": sorted(list(departments))
        },
        "projects": {
            "total": len(algo.projects),
            "by_priority": project_priorities
        },
        "skills": {
            "total_unique": len(total_skills),
            "list": sorted(list(total_skills))
        }
    }