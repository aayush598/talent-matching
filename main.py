from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import re
import json
import math
from groq import Groq
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

app = FastAPI()

# GROQ client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Constants
ALLOWED_DOMAINS = [
    "frontend", "backend", "devops", "ai/ml", "qa",
    "data engineering", "cloud engineering", "database administration",
    "ci/cd", "ux/ui"
]

candidates = [
    {
        "name": "Alice",
        "availability": True,
        "domain": "frontend",
        "skills": ["React", "TypeScript", "Jest", "Prettier", "Next.js", "Storybook"],
        "manager_score": 4.5
    },
    {
        "name": "Bob",
        "availability": True,
        "domain": "backend",
        "skills": ["Python", "Django", "PostgreSQL", "Docker"],
        "manager_score": 3.9
    },
    {
        "name": "Charlie",
        "availability": True,
        "domain": "devops",
        "skills": ["Docker", "Kubernetes", "Git", "Jenkins", "Terraform", "Redis", "Elasticsearch", "Solr"],
        "manager_score": 4.2
    },
    {
        "name": "David",
        "availability": True,
        "domain": "frontend",
        "skills": ["Angular", "Webpack", "ESLint", "Prettier", "Gatsby"],
        "manager_score": 3.5
    },
    {
        "name": "Eve",
        "availability": True,
        "domain": "ai/ml",
        "skills": ["Python", "scikit-learn", "TensorFlow", "Keras"],
        "manager_score": 4.8
    },
]

# Input model
class TeamRequest(BaseModel):
    tech_stack: str
    avg_team_size: float
    manager_score_threshold: float

# Output model
class CandidateOutput(BaseModel):
    name: str
    domain: str
    skills: List[str]
    manager_score: float
@app.post("/generate-team", response_model=List[CandidateOutput])
def generate_team(data: TeamRequest):
    tech_stack = data.tech_stack
    avg_team_size = data.avg_team_size
    manager_score_threshold = data.manager_score_threshold
    max_team_size = math.ceil(avg_team_size)

    # GROQ Prompt
    prompt = f"""
    From the following tech stack, generate a JSON list of recommended software development roles.

    Use only these allowed domains:
    {ALLOWED_DOMAINS}

    For each role, include:
    - "role": descriptive job title (string)
    - "domain": one from the list
    - "skills_required": list of required skills
    - "required_count": number of people needed, based on team size: {avg_team_size}

    Respond in raw JSON only. No markdown or ``` blocks.

    Tech Stack:
    {tech_stack}
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )

        raw_response = chat_completion.choices[0].message.content
        cleaned_response = re.sub(r"```(?:json|markdown)?", "", raw_response).strip("` \n")

        print("\n=== RAW RESPONSE FROM GROQ ===\n", raw_response)
        print("\n=== CLEANED RESPONSE ===\n", cleaned_response)

        parsed_json = json.loads(cleaned_response)

        roles = parsed_json.get("recommended_roles", [])
        if not isinstance(roles, list) or not all(isinstance(role, dict) for role in roles):
            raise ValueError("Expected 'recommended_roles' to be a list of dictionaries")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing GROQ response: {str(e)}")

    # Extract required skills
    all_required_skills = set()
    for role in roles:
        all_required_skills.update(role["skills_required"])

    # Filter available candidates only
    available_candidates = [c for c in candidates if c["availability"]]

    # Score candidates
    for candidate in available_candidates:
        covered = set(candidate["skills"]) & all_required_skills
        candidate["covered_skills"] = covered
        candidate["coverage_score"] = len(covered)
        candidate["meets_manager_score"] = candidate["manager_score"] >= manager_score_threshold

    # Select team
    selected = []
    covered_skills = set()

    while len(selected) < max_team_size and available_candidates:
        available_candidates.sort(
            key=lambda c: (
                len(set(c["skills"]) - covered_skills),
                c["manager_score"]
            ),
            reverse=True
        )
        
        best_candidate = available_candidates.pop(0)
        new_skills = set(best_candidate["skills"]) - covered_skills

        if new_skills:
            covered_skills.update(new_skills)
            selected.append({
                "name": best_candidate["name"],
                "domain": best_candidate["domain"],
                "skills": best_candidate["skills"],
                "manager_score": best_candidate["manager_score"]
            })

    return selected
