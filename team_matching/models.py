from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict

from .enums import ExperienceLevel, AvailabilityStatus, ProjectPriority

@dataclass
class Skill:
    name: str
    proficiency: int
    years_experience: float
    last_used: datetime

@dataclass
class TeamMember:
    id: str
    name: str
    email: str
    department: str
    skills: List[Skill]
    experience_level: ExperienceLevel
    availability_status: AvailabilityStatus
    current_workload: float
    hourly_rate: Optional[float] = None
    preferred_project_types: List[str] = field(default_factory=list)
    location: str = ""
    timezone: str = ""
    certifications: List[str] = field(default_factory=list)

    def get_skill_proficiency(self, skill_name: str) -> int:
        for skill in self.skills:
            if skill.name.lower() == skill_name.lower():
                return skill.proficiency
        return 0

    def has_certification(self, certification: str) -> bool:
        return certification.lower() in [cert.lower() for cert in self.certifications]

@dataclass
class ProjectRequirement:
    skill_name: str
    required_proficiency: int
    min_experience_level: ExperienceLevel
    is_mandatory: bool = True
    weight: float = 1.0

@dataclass
class Project:
    id: str
    name: str
    description: str
    requirements: List[ProjectRequirement]
    start_date: datetime
    end_date: datetime
    priority: ProjectPriority
    budget: Optional[float] = None
    team_size: int = 5
    required_certifications: List[str] = field(default_factory=list)
    preferred_locations: List[str] = field(default_factory=list)
    project_type: str = ""
    estimated_hours: int = 0

@dataclass
class MatchScore:
    member_id: str
    total_score: float
    skill_match_score: float
    availability_score: float
    experience_score: float
    cost_score: float
    location_score: float
    certification_score: float
    detailed_breakdown: Dict[str, float] = field(default_factory=dict)
