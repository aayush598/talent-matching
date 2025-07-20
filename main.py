import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math


class ExperienceLevel(Enum):
    JUNIOR = 1
    MID = 2
    SENIOR = 3
    LEAD = 4
    ARCHITECT = 5


class ProjectPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AvailabilityStatus(Enum):
    AVAILABLE = 1
    PARTIALLY_AVAILABLE = 2
    BUSY = 3
    UNAVAILABLE = 4


@dataclass
class Skill:
    name: str
    proficiency: int  # 1-10 scale
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
    current_workload: float  # 0-100 percentage
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
    required_proficiency: int  # 1-10 scale
    min_experience_level: ExperienceLevel
    is_mandatory: bool = True
    weight: float = 1.0  # Importance weight


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


class TeamMatchingAlgorithm:
    def __init__(self):
        self.members: List[TeamMember] = []
        self.projects: List[Project] = []
        
        # Scoring weights (can be adjusted based on company preferences)
        self.weights = {
            'skill_match': 0.35,
            'availability': 0.25,
            'experience': 0.20,
            'cost': 0.10,
            'location': 0.05,
            'certification': 0.05
        }
    
    def add_member(self, member: TeamMember):
        """Add a team member to the system"""
        self.members.append(member)
    
    def add_project(self, project: Project):
        """Add a project to the system"""
        self.projects.append(project)
    
    def calculate_skill_match_score(self, member: TeamMember, project: Project) -> Tuple[float, Dict[str, float]]:
        """Calculate how well member's skills match project requirements"""
        if not project.requirements:
            return 0.0, {}
        
        total_weight = sum(req.weight for req in project.requirements)
        weighted_score = 0.0
        skill_details = {}
        
        for requirement in project.requirements:
            member_proficiency = member.get_skill_proficiency(requirement.skill_name)
            
            if requirement.is_mandatory and member_proficiency == 0:
                # Missing mandatory skill - heavily penalize
                skill_score = 0.0
            else:
                # Calculate skill match percentage
                if member_proficiency >= requirement.required_proficiency:
                    skill_score = 100.0  # Perfect match or better
                else:
                    skill_score = (member_proficiency / requirement.required_proficiency) * 100
            
            weighted_score += skill_score * requirement.weight
            skill_details[requirement.skill_name] = skill_score
        
        final_score = (weighted_score / total_weight) if total_weight > 0 else 0.0
        return final_score, skill_details
    
    def calculate_availability_score(self, member: TeamMember, project: Project) -> float:
        """Calculate availability score based on current workload and status"""
        status_scores = {
            AvailabilityStatus.AVAILABLE: 100,
            AvailabilityStatus.PARTIALLY_AVAILABLE: 60,
            AvailabilityStatus.BUSY: 30,
            AvailabilityStatus.UNAVAILABLE: 0
        }
        
        base_score = status_scores.get(member.availability_status, 0)
        
        # Adjust based on workload
        workload_factor = max(0, (100 - member.current_workload) / 100)
        
        return base_score * workload_factor
    
    def calculate_experience_score(self, member: TeamMember, project: Project) -> float:
        """Calculate experience level match score"""
        if not project.requirements:
            return 100.0
        
        # Find the highest required experience level
        max_required_level = max([req.min_experience_level.value for req in project.requirements])
        member_level = member.experience_level.value
        
        if member_level >= max_required_level:
            # Award perfect score if member meets or exceeds requirements
            # Small bonus for higher experience
            bonus = min(10, (member_level - max_required_level) * 2)
            return min(100, 90 + bonus)
        else:
            # Penalize for insufficient experience
            return max(0, (member_level / max_required_level) * 70)
    
    def calculate_cost_score(self, member: TeamMember, project: Project) -> float:
        """Calculate cost effectiveness score"""
        if not member.hourly_rate or not project.budget:
            return 50.0  # Neutral score if no cost data
        
        estimated_total_cost = member.hourly_rate * project.estimated_hours
        
        if estimated_total_cost <= project.budget:
            # Cost within budget - higher score for lower cost
            cost_ratio = estimated_total_cost / project.budget
            return 100 * (1 - cost_ratio * 0.5)  # Max score when cost is 0, min 50 when at budget
        else:
            # Over budget - penalize
            overage_ratio = estimated_total_cost / project.budget
            return max(0, 50 - (overage_ratio - 1) * 30)
    
    def calculate_location_score(self, member: TeamMember, project: Project) -> float:
        """Calculate location compatibility score"""
        if not project.preferred_locations:
            return 100.0  # No location preference
        
        if member.location.lower() in [loc.lower() for loc in project.preferred_locations]:
            return 100.0
        else:
            return 30.0  # Remote work penalty
    
    def calculate_certification_score(self, member: TeamMember, project: Project) -> float:
        """Calculate certification match score"""
        if not project.required_certifications:
            return 100.0
        
        matched_certs = sum(1 for cert in project.required_certifications 
                           if member.has_certification(cert))
        
        return (matched_certs / len(project.required_certifications)) * 100
    
    def calculate_member_match_score(self, member: TeamMember, project: Project) -> MatchScore:
        """Calculate overall match score for a member-project pair"""
        skill_score, skill_details = self.calculate_skill_match_score(member, project)
        availability_score = self.calculate_availability_score(member, project)
        experience_score = self.calculate_experience_score(member, project)
        cost_score = self.calculate_cost_score(member, project)
        location_score = self.calculate_location_score(member, project)
        certification_score = self.calculate_certification_score(member, project)
        
        # Calculate weighted total score
        total_score = (
            skill_score * self.weights['skill_match'] +
            availability_score * self.weights['availability'] +
            experience_score * self.weights['experience'] +
            cost_score * self.weights['cost'] +
            location_score * self.weights['location'] +
            certification_score * self.weights['certification']
        )
        
        detailed_breakdown = {
            'skill_details': skill_details,
            'availability_breakdown': {
                'status': member.availability_status.name,
                'workload': member.current_workload
            },
            'experience_breakdown': {
                'member_level': member.experience_level.name,
                'meets_requirements': experience_score >= 70
            }
        }
        
        return MatchScore(
            member_id=member.id,
            total_score=total_score,
            skill_match_score=skill_score,
            availability_score=availability_score,
            experience_score=experience_score,
            cost_score=cost_score,
            location_score=location_score,
            certification_score=certification_score,
            detailed_breakdown=detailed_breakdown
        )
    
    def find_best_team_for_project(self, project_id: str, max_team_size: Optional[int] = None) -> List[MatchScore]:
        """Find the best team members for a specific project"""
        project = next((p for p in self.projects if p.id == project_id), None)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        team_size = max_team_size or project.team_size
        
        # Calculate scores for all members
        member_scores = []
        for member in self.members:
            score = self.calculate_member_match_score(member, project)
            member_scores.append(score)
        
        # Sort by total score and return top candidates
        member_scores.sort(key=lambda x: x.total_score, reverse=True)
        
        # Ensure diversity in skills if possible
        selected_team = self._optimize_team_composition(member_scores, project, team_size)
        
        return selected_team[:team_size]
    
    def _optimize_team_composition(self, member_scores: List[MatchScore], 
                                  project: Project, team_size: int) -> List[MatchScore]:
        """Optimize team composition to ensure skill coverage"""
        if len(member_scores) <= team_size:
            return member_scores
        
        # Identify mandatory skills
        mandatory_skills = [req.skill_name for req in project.requirements if req.is_mandatory]
        
        selected_team = []
        covered_skills = set()
        
        # First, ensure all mandatory skills are covered
        for skill in mandatory_skills:
            best_candidate = None
            best_score = -1
            
            for score in member_scores:
                if score.member_id not in [s.member_id for s in selected_team]:
                    member = next(m for m in self.members if m.id == score.member_id)
                    if member.get_skill_proficiency(skill) > 0 and score.total_score > best_score:
                        best_candidate = score
                        best_score = score.total_score
            
            if best_candidate and len(selected_team) < team_size:
                selected_team.append(best_candidate)
                member = next(m for m in self.members if m.id == best_candidate.member_id)
                covered_skills.update(skill.name for skill in member.skills if skill.proficiency > 0)
        
        # Fill remaining positions with highest scoring members
        for score in member_scores:
            if len(selected_team) >= team_size:
                break
            
            if score.member_id not in [s.member_id for s in selected_team]:
                selected_team.append(score)
        
        return selected_team
    
    def generate_team_report(self, project_id: str, team_scores: List[MatchScore]) -> Dict:
        """Generate a detailed report for the selected team"""
        project = next((p for p in self.projects if p.id == project_id), None)
        if not project:
            return {}
        
        team_members = []
        total_cost = 0
        skill_coverage = {}
        
        for score in team_scores:
            member = next((m for m in self.members if m.id == score.member_id), None)
            if member:
                member_info = {
                    'id': member.id,
                    'name': member.name,
                    'email': member.email,
                    'experience_level': member.experience_level.name,
                    'match_score': round(score.total_score, 2),
                    'skills': [{'name': skill.name, 'proficiency': skill.proficiency} 
                              for skill in member.skills],
                    'availability': {
                        'status': member.availability_status.name,
                        'workload': member.current_workload
                    }
                }
                team_members.append(member_info)
                
                if member.hourly_rate and project.estimated_hours:
                    total_cost += member.hourly_rate * project.estimated_hours
                
                # Track skill coverage
                for skill in member.skills:
                    if skill.name not in skill_coverage:
                        skill_coverage[skill.name] = []
                    skill_coverage[skill.name].append({
                        'member': member.name,
                        'proficiency': skill.proficiency
                    })
        
        # Check requirement coverage
        requirement_coverage = []
        for req in project.requirements:
            covered_by = skill_coverage.get(req.skill_name, [])
            requirement_coverage.append({
                'skill': req.skill_name,
                'required_proficiency': req.required_proficiency,
                'is_mandatory': req.is_mandatory,
                'covered_by': covered_by,
                'is_covered': any(member['proficiency'] >= req.required_proficiency 
                                for member in covered_by)
            })
        
        return {
            'project': {
                'id': project.id,
                'name': project.name,
                'priority': project.priority.name,
                'duration': f"{project.start_date.strftime('%Y-%m-%d')} to {project.end_date.strftime('%Y-%m-%d')}"
            },
            'team_members': team_members,
            'team_statistics': {
                'team_size': len(team_members),
                'average_match_score': round(sum(score.total_score for score in team_scores) / len(team_scores), 2),
                'estimated_total_cost': round(total_cost, 2) if total_cost > 0 else None,
                'skill_coverage': skill_coverage,
                'requirement_coverage': requirement_coverage
            }
        }


# Example usage and test data
def create_sample_data():
    """Create sample data for testing"""
    algorithm = TeamMatchingAlgorithm()
    
    # Sample team members
    members_data = [
        {
            'id': 'TM001',
            'name': 'Alice Johnson',
            'email': 'alice.johnson@company.com',
            'department': 'Engineering',
            'skills': [
                Skill('Python', 9, 5.0, datetime(2024, 1, 1)),
                Skill('React', 8, 3.0, datetime(2024, 2, 1)),
                Skill('Docker', 7, 2.0, datetime(2024, 1, 15)),
                Skill('AWS', 8, 4.0, datetime(2024, 1, 30))
            ],
            'experience_level': ExperienceLevel.SENIOR,
            'availability_status': AvailabilityStatus.AVAILABLE,
            'current_workload': 20.0,
            'hourly_rate': 75.0,
            'location': 'New York',
            'certifications': ['AWS Certified Developer', 'Scrum Master']
        },
        {
            'id': 'TM002',
            'name': 'Bob Smith',
            'email': 'bob.smith@company.com',
            'department': 'Engineering',
            'skills': [
                Skill('Java', 9, 8.0, datetime(2024, 1, 1)),
                Skill('Spring Boot', 8, 6.0, datetime(2024, 1, 10)),
                Skill('Kubernetes', 7, 3.0, datetime(2024, 2, 1)),
                Skill('PostgreSQL', 8, 5.0, datetime(2024, 1, 20))
            ],
            'experience_level': ExperienceLevel.LEAD,
            'availability_status': AvailabilityStatus.PARTIALLY_AVAILABLE,
            'current_workload': 60.0,
            'hourly_rate': 90.0,
            'location': 'San Francisco',
            'certifications': ['Oracle Java Certified', 'PMP']
        },
        {
            'id': 'TM003',
            'name': 'Carol Davis',
            'email': 'carol.davis@company.com',
            'department': 'Design',
            'skills': [
                Skill('UI/UX Design', 9, 4.0, datetime(2024, 1, 1)),
                Skill('Figma', 9, 3.0, datetime(2024, 1, 5)),
                Skill('React', 6, 2.0, datetime(2024, 2, 1)),
                Skill('User Research', 8, 4.0, datetime(2024, 1, 15))
            ],
            'experience_level': ExperienceLevel.MID,
            'availability_status': AvailabilityStatus.AVAILABLE,
            'current_workload': 10.0,
            'hourly_rate': 65.0,
            'location': 'New York',
            'certifications': ['Google UX Design']
        }
    ]
    
    for member_data in members_data:
        member = TeamMember(**member_data)
        algorithm.add_member(member)
    
    # Sample project
    project = Project(
        id='PROJ001',
        name='E-commerce Platform Redesign',
        description='Modernize the existing e-commerce platform with new UI and backend improvements',
        requirements=[
            ProjectRequirement('Python', 7, ExperienceLevel.MID, True, 2.0),
            ProjectRequirement('React', 8, ExperienceLevel.MID, True, 2.0),
            ProjectRequirement('AWS', 6, ExperienceLevel.MID, True, 1.5),
            ProjectRequirement('UI/UX Design', 8, ExperienceLevel.MID, True, 1.5),
            ProjectRequirement('Docker', 5, ExperienceLevel.JUNIOR, False, 1.0)
        ],
        start_date=datetime(2025, 8, 1),
        end_date=datetime(2025, 12, 31),
        priority=ProjectPriority.HIGH,
        budget=50000.0,
        team_size=3,
        required_certifications=['AWS Certified Developer'],
        preferred_locations=['New York', 'San Francisco'],
        project_type='Web Development',
        estimated_hours=600
    )
    
    algorithm.add_project(project)
    return algorithm


if __name__ == "__main__":
    # Example usage
    algorithm = create_sample_data()
    
    # Find best team for project
    project_id = 'PROJ001'
    best_team = algorithm.find_best_team_for_project(project_id)
    
    # Generate detailed report
    report = algorithm.generate_team_report(project_id, best_team)
    
    # Print results
    print("=== TEAM MATCHING RESULTS ===")
    print(f"Project: {report['project']['name']}")
    print(f"Priority: {report['project']['priority']}")
    print(f"Duration: {report['project']['duration']}")
    print("\n=== SELECTED TEAM ===")
    
    for member in report['team_members']:
        print(f"\nMember: {member['name']} ({member['experience_level']})")
        print(f"Match Score: {member['match_score']}/100")
        print(f"Email: {member['email']}")
        print(f"Availability: {member['availability']['status']} ({member['availability']['workload']}% workload)")
        print("Skills:")
        for skill in member['skills']:
            print(f"  - {skill['name']}: {skill['proficiency']}/10")
    
    print(f"\n=== TEAM STATISTICS ===")
    stats = report['team_statistics']
    print(f"Team Size: {stats['team_size']}")
    print(f"Average Match Score: {stats['average_match_score']}/100")
    if stats['estimated_total_cost']:
        print(f"Estimated Total Cost: ${stats['estimated_total_cost']:,.2f}")
    
    print("\n=== REQUIREMENT COVERAGE ===")
    for req in stats['requirement_coverage']:
        status = "✓" if req['is_covered'] else "✗"
        mandatory = "(Mandatory)" if req['is_mandatory'] else "(Optional)"
        print(f"{status} {req['skill']} {mandatory} - Required: {req['required_proficiency']}/10")
        for member in req['covered_by']:
            print(f"    {member['member']}: {member['proficiency']}/10")