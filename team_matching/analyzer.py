from .algorithm import TeamMatchingAlgorithm

def analyze_all_projects(algorithm: TeamMatchingAlgorithm):
    for project in algorithm.projects:
        print("="*60)
        print(f"PROJECT: {project.name}")
        print(f"Priority: {project.priority.name}")
        print(f"Team Size: {project.team_size}")
        print(f"Budget: ${project.budget:,.2f}" if project.budget else "Budget: Not specified")
        print(f"Duration: {project.start_date.strftime('%Y-%m-%d')} to {project.end_date.strftime('%Y-%m-%d')}")
        print("="*60)
        try:
            best_team = algorithm.find_best_team_for_project(project.id)
            report = algorithm.generate_team_report(project.id, best_team)
            print("\n--- SELECTED TEAM ---")
            for i, member in enumerate(report['team_members'], 1):
                print(f"\n{i}. {member['name']} ({member['experience_level']})")
                print(f"   Match Score: {member['match_score']}/100")
                print(f"   Email: {member['email']}")
                print(f"   Availability: {member['availability']['status']} ({member['availability']['workload']}% workload)")
                print("   Top Skills:")
                top_skills = sorted(member['skills'], key=lambda x: x['proficiency'], reverse=True)[:5]
                for skill in top_skills:
                    print(f"     • {skill['name']}: {skill['proficiency']}/10")
            print("\n--- TEAM STATISTICS ---")
            stats = report['team_statistics']
            print(f"Average Match Score: {stats['average_match_score']}/100")
            if stats['estimated_total_cost']:
                print(f"Estimated Total Cost: ${stats['estimated_total_cost']:,.2f}")
            print("\n--- REQUIREMENT COVERAGE ---")
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
                    print("    ⚠ No team members have this skill")
        except Exception as e:
            print(f"Error analyzing project {project.id}: {e}")
        print("="*60)
