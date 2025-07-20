from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json
import os
from contextlib import asynccontextmanager

# Import your existing models and algorithm
from team_matching.algorithm import TeamMatchingAlgorithm
from team_matching.models import TeamMember, Project, Skill, ProjectRequirement, MatchScore
from team_matching.enums import ExperienceLevel, AvailabilityStatus, ProjectPriority
from team_matching.data_loader import create_sample_data_from_file

# Pydantic models for API requests/responses
class SkillRequest(BaseModel):
    name: str
    proficiency: int = Field(ge=1, le=10, description="Skill proficiency from 1-10")
    years_experience: float = Field(ge=0, description="Years of experience")
    last_used: str = Field(description="Last used date in YYYY-MM-DD format")

class SkillResponse(BaseModel):
    name: str
    proficiency: int
    years_experience: float
    last_used: str

class TeamMemberRequest(BaseModel):
    id: str
    name: str
    email: str
    department: str
    skills: List[SkillRequest]
    experience_level: str = Field(description="JUNIOR, MID, SENIOR, LEAD, or ARCHITECT")
    availability_status: str = Field(description="AVAILABLE, PARTIALLY_AVAILABLE, BUSY, or UNAVAILABLE")
    current_workload: float = Field(ge=0, le=100, description="Current workload percentage")
    hourly_rate: Optional[float] = None
    preferred_project_types: List[str] = []
    location: str = ""
    timezone: str = ""
    certifications: List[str] = []

class TeamMemberResponse(BaseModel):
    id: str
    name: str
    email: str
    department: str
    skills: List[SkillResponse]
    experience_level: str
    availability_status: str
    current_workload: float
    hourly_rate: Optional[float]
    preferred_project_types: List[str]
    location: str
    timezone: str
    certifications: List[str]

class ProjectRequirementRequest(BaseModel):
    skill_name: str
    required_proficiency: int = Field(ge=1, le=10)
    min_experience_level: str = Field(description="JUNIOR, MID, SENIOR, LEAD, or ARCHITECT")
    is_mandatory: bool = True
    weight: float = Field(ge=0, default=1.0)

class ProjectRequest(BaseModel):
    id: str
    name: str
    description: str
    requirements: List[ProjectRequirementRequest]
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    end_date: str = Field(description="End date in YYYY-MM-DD format")
    priority: str = Field(description="LOW, MEDIUM, HIGH, or CRITICAL")
    budget: Optional[float] = None
    team_size: int = Field(ge=1, default=5)
    required_certifications: List[str] = []
    preferred_locations: List[str] = []
    project_type: str = ""
    estimated_hours: int = Field(ge=0, default=0)

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    requirements: List[Dict[str, Any]]
    start_date: str
    end_date: str
    priority: str
    budget: Optional[float]
    team_size: int
    required_certifications: List[str]
    preferred_locations: List[str]
    project_type: str
    estimated_hours: int

class MatchScoreResponse(BaseModel):
    member_id: str
    member_name: str
    total_score: float
    skill_match_score: float
    availability_score: float
    experience_score: float
    cost_score: float
    location_score: float
    certification_score: float
    detailed_breakdown: Dict[str, Any]

class TeamReportResponse(BaseModel):
    project: Dict[str, Any]
    team_members: List[Dict[str, Any]]
    team_statistics: Dict[str, Any]

class UpdateWeightsRequest(BaseModel):
    skill_match: Optional[float] = Field(ge=0, le=1, default=None)
    availability: Optional[float] = Field(ge=0, le=1, default=None)
    experience: Optional[float] = Field(ge=0, le=1, default=None)
    cost: Optional[float] = Field(ge=0, le=1, default=None)
    location: Optional[float] = Field(ge=0, le=1, default=None)
    certification: Optional[float] = Field(ge=0, le=1, default=None)

# Global algorithm instance
algorithm = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global algorithm
    try:
        if os.path.exists('data.json'):
            algorithm = create_sample_data_from_file('data.json')
        else:
            algorithm = TeamMatchingAlgorithm()
        print("Team Matching Algorithm initialized successfully")
    except Exception as e:
        print(f"Warning: Could not load data.json: {e}")
        algorithm = TeamMatchingAlgorithm()
    
    yield
    
    # Shutdown
    print("Team Matching API shutting down")

# Create FastAPI app
app = FastAPI(
    title="Team Matching API",
    description="API for intelligent team member matching and project assignment",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def get_algorithm():
    if algorithm is None:
        raise HTTPException(status_code=500, detail="Algorithm not initialized")
    return algorithm

def convert_team_member_to_model(member_data: TeamMemberRequest) -> TeamMember:
    """Convert API request to internal model"""
    skills = []
    for skill_data in member_data.skills:
        skill = Skill(
            name=skill_data.name,
            proficiency=skill_data.proficiency,
            years_experience=skill_data.years_experience,
            last_used=datetime.strptime(skill_data.last_used, '%Y-%m-%d')
        )
        skills.append(skill)
    
    return TeamMember(
        id=member_data.id,
        name=member_data.name,
        email=member_data.email,
        department=member_data.department,
        skills=skills,
        experience_level=ExperienceLevel[member_data.experience_level.upper()],
        availability_status=AvailabilityStatus[member_data.availability_status.upper()],
        current_workload=member_data.current_workload,
        hourly_rate=member_data.hourly_rate,
        preferred_project_types=member_data.preferred_project_types,
        location=member_data.location,
        timezone=member_data.timezone,
        certifications=member_data.certifications
    )

def convert_project_to_model(project_data: ProjectRequest) -> Project:
    """Convert API request to internal model"""
    requirements = []
    for req_data in project_data.requirements:
        requirement = ProjectRequirement(
            skill_name=req_data.skill_name,
            required_proficiency=req_data.required_proficiency,
            min_experience_level=ExperienceLevel[req_data.min_experience_level.upper()],
            is_mandatory=req_data.is_mandatory,
            weight=req_data.weight
        )
        requirements.append(requirement)
    
    return Project(
        id=project_data.id,
        name=project_data.name,
        description=project_data.description,
        requirements=requirements,
        start_date=datetime.strptime(project_data.start_date, '%Y-%m-%d'),
        end_date=datetime.strptime(project_data.end_date, '%Y-%m-%d'),
        priority=ProjectPriority[project_data.priority.upper()],
        budget=project_data.budget,
        team_size=project_data.team_size,
        required_certifications=project_data.required_certifications,
        preferred_locations=project_data.preferred_locations,
        project_type=project_data.project_type,
        estimated_hours=project_data.estimated_hours
    )

# API Routes

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Team Matching API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    algo = get_algorithm()
    return {
        "status": "healthy",
        "members_count": len(algo.members),
        "projects_count": len(algo.projects),
        "timestamp": datetime.now().isoformat()
    }

# Team Member endpoints
@app.post("/members", response_model=dict, status_code=201)
async def add_team_member(member: TeamMemberRequest, algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
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

@app.get("/members", response_model=List[TeamMemberResponse])
async def get_all_members(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get all team members"""
    members = []
    for member in algo.members:
        skills = [
            SkillResponse(
                name=skill.name,
                proficiency=skill.proficiency,
                years_experience=skill.years_experience,
                last_used=skill.last_used.strftime('%Y-%m-%d')
            ) for skill in member.skills
        ]
        
        member_response = TeamMemberResponse(
            id=member.id,
            name=member.name,
            email=member.email,
            department=member.department,
            skills=skills,
            experience_level=member.experience_level.name,
            availability_status=member.availability_status.name,
            current_workload=member.current_workload,
            hourly_rate=member.hourly_rate,
            preferred_project_types=member.preferred_project_types,
            location=member.location,
            timezone=member.timezone,
            certifications=member.certifications
        )
        members.append(member_response)
    
    return members

@app.get("/members/{member_id}", response_model=TeamMemberResponse)
async def get_member_by_id(member_id: str = Path(..., description="Member ID"), 
                          algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get a specific team member by ID"""
    member = next((m for m in algo.members if m.id == member_id), None)
    if not member:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
    
    skills = [
        SkillResponse(
            name=skill.name,
            proficiency=skill.proficiency,
            years_experience=skill.years_experience,
            last_used=skill.last_used.strftime('%Y-%m-%d')
        ) for skill in member.skills
    ]
    
    return TeamMemberResponse(
        id=member.id,
        name=member.name,
        email=member.email,
        department=member.department,
        skills=skills,
        experience_level=member.experience_level.name,
        availability_status=member.availability_status.name,
        current_workload=member.current_workload,
        hourly_rate=member.hourly_rate,
        preferred_project_types=member.preferred_project_types,
        location=member.location,
        timezone=member.timezone,
        certifications=member.certifications
    )

@app.put("/members/{member_id}")
async def update_member(member_id: str, member: TeamMemberRequest, 
                       algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
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

@app.delete("/members/{member_id}")
async def delete_member(member_id: str = Path(..., description="Member ID"), 
                       algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Delete a team member"""
    member_index = next((i for i, m in enumerate(algo.members) if m.id == member_id), None)
    if member_index is None:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
    
    removed_member = algo.members.pop(member_index)
    return {"message": f"Member {removed_member.name} deleted successfully"}

# Project endpoints
@app.post("/projects", response_model=dict, status_code=201)
async def add_project(project: ProjectRequest, algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
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

@app.get("/projects", response_model=List[ProjectResponse])
async def get_all_projects(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get all projects"""
    projects = []
    for project in algo.projects:
        requirements = [
            {
                "skill_name": req.skill_name,
                "required_proficiency": req.required_proficiency,
                "min_experience_level": req.min_experience_level.name,
                "is_mandatory": req.is_mandatory,
                "weight": req.weight
            } for req in project.requirements
        ]
        
        project_response = ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            requirements=requirements,
            start_date=project.start_date.strftime('%Y-%m-%d'),
            end_date=project.end_date.strftime('%Y-%m-%d'),
            priority=project.priority.name,
            budget=project.budget,
            team_size=project.team_size,
            required_certifications=project.required_certifications,
            preferred_locations=project.preferred_locations,
            project_type=project.project_type,
            estimated_hours=project.estimated_hours
        )
        projects.append(project_response)
    
    return projects

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(project_id: str = Path(..., description="Project ID"), 
                           algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get a specific project by ID"""
    project = next((p for p in algo.projects if p.id == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    
    requirements = [
        {
            "skill_name": req.skill_name,
            "required_proficiency": req.required_proficiency,
            "min_experience_level": req.min_experience_level.name,
            "is_mandatory": req.is_mandatory,
            "weight": req.weight
        } for req in project.requirements
    ]
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        requirements=requirements,
        start_date=project.start_date.strftime('%Y-%m-%d'),
        end_date=project.end_date.strftime('%Y-%m-%d'),
        priority=project.priority.name,
        budget=project.budget,
        team_size=project.team_size,
        required_certifications=project.required_certifications,
        preferred_locations=project.preferred_locations,
        project_type=project.project_type,
        estimated_hours=project.estimated_hours
    )

# Team Matching endpoints
@app.get("/projects/{project_id}/matches", response_model=List[MatchScoreResponse])
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

@app.get("/projects/{project_id}/best-team", response_model=List[MatchScoreResponse])
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

@app.get("/projects/{project_id}/team-report", response_model=TeamReportResponse)
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

# Algorithm configuration endpoints
@app.get("/algorithm/weights")
async def get_algorithm_weights(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get current algorithm scoring weights"""
    return algo.weights

@app.put("/algorithm/weights")
async def update_algorithm_weights(weights: UpdateWeightsRequest, 
                                  algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Update algorithm scoring weights"""
    updated_weights = {}
    
    for key, value in weights.dict(exclude_unset=True).items():
        if value is not None:
            algo.weights[key] = value
            updated_weights[key] = value
    
    # Validate weights sum to approximately 1.0
    total_weight = sum(algo.weights.values())
    if abs(total_weight - 1.0) > 0.01:
        raise HTTPException(
            status_code=400, 
            detail=f"Weights must sum to approximately 1.0, current sum: {total_weight}"
        )
    
    return {
        "message": "Algorithm weights updated successfully",
        "updated_weights": updated_weights,
        "current_weights": algo.weights
    }

# Utility endpoints
@app.get("/skills/list")
async def get_all_skills(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get list of all skills across all team members"""
    skills = set()
    for member in algo.members:
        for skill in member.skills:
            skills.add(skill.name)
    return {"skills": sorted(list(skills))}

@app.get("/stats")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)