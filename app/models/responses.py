from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class SkillResponse(BaseModel):
    name: str
    proficiency: int
    years_experience: float
    last_used: str

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