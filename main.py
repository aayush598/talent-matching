from team_matching.data_loader import create_sample_data_from_file
from team_matching.analyzer import analyze_all_projects

if __name__ == "__main__":
    algorithm = create_sample_data_from_file('data.json')
    analyze_all_projects(algorithm)

    print("\n" + "="*80)
    print("INDIVIDUAL PROJECT ANALYSIS")
    print("="*80)

    project_id = 'PROJ002'
    try:
        best_team = algorithm.find_best_team_for_project(project_id)
        report = algorithm.generate_team_report(project_id, best_team)
        print(f"\n=== DETAILED ANALYSIS FOR {project_id} ===")
        print(f"Project: {report['project']['name']}")
        print(f"Priority: {report['project']['priority']}")
        print(f"Duration: {report['project']['duration']}")
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
