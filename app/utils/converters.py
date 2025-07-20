from datetime import datetime
from typing import List

from app.models.requests import TeamMemberRequest, ProjectRequest
from app.models.responses import SkillResponse, TeamMemberResponse, ProjectResponse
from team_matching.models import TeamMember, Project, Skill, ProjectRequirement
from team_matching.enums import ExperienceLevel, AvailabilityStatus, ProjectPriority

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

def convert_team_member_to_response(member: TeamMember) -> TeamMemberResponse:
    """Convert internal model to API response"""
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

def convert_project_to_response(project: Project) -> ProjectResponse:
    """Convert internal model to API response"""
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