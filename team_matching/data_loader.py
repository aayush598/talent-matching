import json
from datetime import datetime
from .algorithm import TeamMatchingAlgorithm
from .models import Skill, TeamMember, ProjectRequirement, Project
from .enums import ExperienceLevel, AvailabilityStatus, ProjectPriority

def create_sample_data_from_file(json_file_path='data.json') -> TeamMatchingAlgorithm:
    algorithm = TeamMatchingAlgorithm()
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    for member_data in data['members']:
        skills = [
            Skill(
                s['name'],
                s['proficiency'],
                s['experience_years'],
                datetime.strptime(s['last_used'], '%Y-%m-%d')
            ) for s in member_data.pop('skills')
        ]
        member_data['skills'] = skills
        member_data['experience_level'] = ExperienceLevel[member_data['experience_level']]
        member_data['availability_status'] = AvailabilityStatus[member_data['availability_status']]
        algorithm.add_member(TeamMember(**member_data))

    projects_data = data['project'] if isinstance(data['project'], list) else [data['project']]
    for proj_data in projects_data:
        proj_copy = proj_data.copy()
        requirements = []
        for r in proj_copy.pop('requirements'):
            proficiency = r.get('required_proficiency', r.get('min_proficiency', 5))
            experience_level = r.get('experience_level', r.get('min_experience_level', 'JUNIOR'))
            mandatory = r.get('mandatory', r.get('is_mandatory', True))
            weight = r.get('weight', r.get('estimated_hours', 1.0))
            requirements.append(ProjectRequirement(
                skill_name=r['skill_name'],
                required_proficiency=proficiency,
                min_experience_level=ExperienceLevel[experience_level],
                is_mandatory=mandatory,
                weight=weight
            ))

        proj_copy['requirements'] = requirements
        proj_copy['start_date'] = datetime.strptime(proj_copy['start_date'], '%Y-%m-%d')
        proj_copy['end_date'] = datetime.strptime(proj_copy['end_date'], '%Y-%m-%d')
        proj_copy['priority'] = ProjectPriority[proj_copy['priority']]
        algorithm.add_project(Project(**proj_copy))
    return algorithm
