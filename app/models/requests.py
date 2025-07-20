from typing import List, Optional
from pydantic import BaseModel, Field

class SkillRequest(BaseModel):
    name: str
    proficiency: int = Field(ge=1, le=10, description="Skill proficiency from 1-10")
    years_experience: float = Field(ge=0, description="Years of experience")
    last_used: str = Field(description="Last used date in YYYY-MM-DD format")

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

class UpdateWeightsRequest(BaseModel):
    skill_match: Optional[float] = Field(ge=0, le=1, default=None)
    availability: Optional[float] = Field(ge=0, le=1, default=None)
    experience: Optional[float] = Field(ge=0, le=1, default=None)
    cost: Optional[float] = Field(ge=0, le=1, default=None)
    location: Optional[float] = Field(ge=0, le=1, default=None)
    certification: Optional[float] = Field(ge=0, le=1, default=None)