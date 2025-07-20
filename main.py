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


def create_sample_data_from_file(json_file_path='data.json'):
    """Load team members and projects from a JSON file"""
    algorithm = TeamMatchingAlgorithm()

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Load members
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

        member = TeamMember(**member_data)
        algorithm.add_member(member)

    # Load projects - Handle both array and single project formats
    projects_data = data['project'] if isinstance(data['project'], list) else [data['project']]
    
    for proj_data in projects_data:
        # Create a copy to avoid modifying original data
        proj_copy = proj_data.copy()
        
        requirements = []
        for r in proj_copy.pop('requirements'):
            # Handle different field name variations
            proficiency = r.get('required_proficiency', r.get('min_proficiency', 5))
            experience_level = r.get('experience_level', r.get('min_experience_level', 'JUNIOR'))
            mandatory = r.get('mandatory', r.get('is_mandatory', True))
            weight = r.get('weight', r.get('estimated_hours', 1.0))
            
            requirement = ProjectRequirement(
                skill_name=r['skill_name'],
                required_proficiency=proficiency,
                min_experience_level=ExperienceLevel[experience_level],
                is_mandatory=mandatory,
                weight=weight
            )
            requirements.append(requirement)
        
        proj_copy['requirements'] = requirements
        proj_copy['start_date'] = datetime.strptime(proj_copy['start_date'], '%Y-%m-%d')
        proj_copy['end_date'] = datetime.strptime(proj_copy['end_date'], '%Y-%m-%d')
        proj_copy['priority'] = ProjectPriority[proj_copy['priority']]

        project = Project(**proj_copy)
        algorithm.add_project(project)

    return algorithm


def analyze_all_projects(algorithm: TeamMatchingAlgorithm):
    """Analyze all projects and find best teams for each"""
    print("=== ANALYZING ALL PROJECTS ===\n")
    
    for project in algorithm.projects:
        print(f"{'='*60}")
        print(f"PROJECT: {project.name}")
        print(f"Priority: {project.priority.name}")
        print(f"Team Size: {project.team_size}")
        print(f"Budget: ${project.budget:,.2f}" if project.budget else "Budget: Not specified")
        print(f"Duration: {project.start_date.strftime('%Y-%m-%d')} to {project.end_date.strftime('%Y-%m-%d')}")
        print(f"{'='*60}")
        
        # Find best team for this project
        try:
            best_team = algorithm.find_best_team_for_project(project.id)
            report = algorithm.generate_team_report(project.id, best_team)
            
            print("\n--- SELECTED TEAM ---")
            for i, member in enumerate(report['team_members'], 1):
                print(f"\n{i}. {member['name']} ({member['experience_level']})")
                print(f"   Match Score: {member['match_score']}/100")
                print(f"   Email: {member['email']}")
                print(f"   Availability: {member['availability']['status']} ({member['availability']['workload']}% workload)")
                print(f"   Top Skills:")
                # Show top 5 skills
                top_skills = sorted(member['skills'], key=lambda x: x['proficiency'], reverse=True)[:5]
                for skill in top_skills:
                    print(f"     • {skill['name']}: {skill['proficiency']}/10")
            
            print(f"\n--- TEAM STATISTICS ---")
            stats = report['team_statistics']
            print(f"Average Match Score: {stats['average_match_score']}/100")
            if stats['estimated_total_cost']:
                print(f"Estimated Total Cost: ${stats['estimated_total_cost']:,.2f}")
            
            print(f"\n--- REQUIREMENT COVERAGE ---")
            for req in stats['requirement_coverage']:
                status = "✅ COVERED" if req['is_covered'] else "❌ NOT COVERED"
                mandatory = "(MANDATORY)" if req['is_mandatory'] else "(Optional)"
                print(f"{status} {req['skill']} {mandatory}")
                print(f"  Required: {req['required_proficiency']}/10")
                if req['covered_by']:
                    for member in req['covered_by']:
                        icon = "✓" if member['proficiency'] >= req['required_proficiency'] else "⚠"
                        print(f"    {icon} {member['member']}: {member['proficiency']}/10")
                else:
                    print(f"    ⚠ No team members have this skill")
                    
        except Exception as e:
            print(f"Error analyzing project {project.id}: {e}")
        
        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Load data and analyze all projects
    algorithm = create_sample_data_from_file('data.json')
    
    # Analyze all projects
    analyze_all_projects(algorithm)
    
    print("\n" + "="*80)
    print("INDIVIDUAL PROJECT ANALYSIS")
    print("="*80)
    
    # Example: Detailed analysis for a specific project
    project_id = 'PROJ002'  # AI Chatbot project
    print(f"\n=== DETAILED ANALYSIS FOR {project_id} ===")
    
    try:
        best_team = algorithm.find_best_team_for_project(project_id)
        report = algorithm.generate_team_report(project_id, best_team)
        
        print(f"Project: {report['project']['name']}")
        print(f"Priority: {report['project']['priority']}")
        print(f"Duration: {report['project']['duration']}")
        
        print("\n=== DETAILED MEMBER BREAKDOWN ===")
        for i, score in enumerate(best_team, 1):
            member = next((m for m in algorithm.members if m.id == score.member_id), None)
            if member:
                print(f"\n{i}. {member.name}")
                print(f"   Overall Score: {score.total_score:.1f}/100")
                print(f"   Skill Match: {score.skill_match_score:.1f}/100")
                print(f"   Availability: {score.availability_score:.1f}/100")
                print(f"   Experience: {score.experience_score:.1f}/100")
                print(f"   Cost Score: {score.cost_score:.1f}/100")
                print(f"   Location: {score.location_score:.1f}/100")
                print(f"   Certification: {score.certification_score:.1f}/100")
                
    except Exception as e:
        print(f"Error: {e}")