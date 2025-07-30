from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import re
import json
import math
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Set, Optional

# Load environment variables
load_dotenv()

app = FastAPI()

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

# Output model
class CandidateOutput(BaseModel):
    name: str
    domain: str
    skills: List[str]
    manager_score: float

async def parse_specfile(file: UploadFile) -> dict:
    """Parse the uploaded JSON spec file"""
    try:
        contents = await file.read()
        spec_data = json.loads(contents)
        return spec_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

def extract_requirements_from_spec(spec_data: dict) -> dict:
    """Extract tech stack and team requirements from project specification"""
    # Hardcoded GROQ API key
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    
    prompt = f"""
PROJECT SPECIFICATION DOCUMENT (JSON):
{json.dumps(spec_data, indent=2)}

INSTRUCTIONS:
1. Analyze the technical architecture and technology stack sections
2. Extract all mentioned technologies and group them by domain
3. Estimate team size based on project scope and timeline
4. Return JSON with tech stack and team requirements

OUTPUT FORMAT (raw JSON only, no markdown):
{{
    "tech_stack": {{
        "frontend": ["React", "TypeScript"],
        "backend": ["Node.js", "Express"],
        "database": ["PostgreSQL"],
        "devops": ["Docker", "Kubernetes"]
    }},
    "avg_team_size": 4.5,
    "manager_score_threshold": 4.0
}}

RULES:
- Only include technologies explicitly mentioned
- Map technologies to standard domains (frontend, backend, database, devops, etc.)
- Estimate team size based on project complexity and timeline
- Set manager_score_threshold to 4.0 unless specified otherwise
- Be conservative with team size estimates
"""
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "You are a technical requirements extraction expert. Analyze project specs and extract tech stack and team requirements."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=2000
        )

        raw_response = chat_completion.choices[0].message.content
        cleaned_response = re.sub(r"```(?:json|markdown)?", "", raw_response).strip("` \n")
        return json.loads(cleaned_response)
    
    except Exception as e:
        print(f"Error extracting requirements: {str(e)}")
        # Fallback to default values if extraction fails
        return {
            "tech_stack": {
                "frontend": ["Node.js"],
                "backend": ["Node.js", "Express.js"],
                "database": ["MySQL"]
            },
            "avg_team_size": 3.0,
            "manager_score_threshold": 4.0
        }

def map_tech_stack_to_candidate_domains(tech_stack: Dict[str, List[str]]) -> Dict[str, str]:
    """Map tech stack domains to candidate domains with strict mapping"""
    domain_mapping = {
        # Frontend mappings
        "frontend": "frontend",
        "ui": "frontend",
        "ux": "frontend",
        "client": "frontend",
        
        # Backend mappings  
        "backend": "backend",
        "api": "backend",
        "server": "backend",
        "database": "backend",
        "db": "backend",
        
        # DevOps mappings
        "devops": "devops",
        "infrastructure": "devops",
        "deployment": "devops",
        "containerization": "devops",
        "containers": "devops",
        "orchestration": "devops",
        "ci/cd": "devops",
        "cicd": "devops",
        
        # AI/ML mappings
        "ai/ml": "ai/ml",
        "ai": "ai/ml",
        "ml": "ai/ml",
        "machine_learning": "ai/ml",
        "artificial_intelligence": "ai/ml",
        "data_science": "ai/ml",
        
        # QA mappings
        "qa": "qa",
        "testing": "qa",
        "quality_assurance": "qa",
    }
    
    mapped_domains = {}
    for tech_domain in tech_stack.keys():
        tech_domain_lower = tech_domain.lower().replace(" ", "_").replace("-", "_")
        if tech_domain_lower in domain_mapping:
            mapped_domains[tech_domain] = domain_mapping[tech_domain_lower]
        else:
            mapped_domains[tech_domain] = tech_domain
    
    return mapped_domains

def extract_available_candidates_by_domain(requested_domains: Set[str]) -> Dict[str, List[Dict]]:
    """Extract available candidates ONLY from requested domains"""
    available_by_domain = {}
    for candidate in candidates:
        if candidate["availability"] and candidate["domain"] in requested_domains:
            domain = candidate["domain"]
            if domain not in available_by_domain:
                available_by_domain[domain] = []
            available_by_domain[domain].append(candidate)
    return available_by_domain

def create_smart_domain_prompt(tech_stack: Dict[str, List[str]], avg_team_size: float, 
                              manager_score_threshold: float, available_by_domain: Dict[str, List[Dict]],
                              domain_mapping: Dict[str, str]) -> str:
    """Create a smart prompt that ONLY considers requested domains"""
    
    candidates_context = ""
    requested_domains = set(domain_mapping.values())
    
    if not available_by_domain:
        candidates_context = "NO CANDIDATES AVAILABLE for the requested domains."
    else:
        for domain, domain_candidates in available_by_domain.items():
            candidates_context += f"\n{domain.upper()} DOMAIN:\n"
            for candidate in domain_candidates:
                candidates_context += f"  - {candidate['name']}: Skills={candidate['skills']}, Manager Score={candidate['manager_score']}\n"
    
    tech_requirements = ""
    for tech_domain, technologies in tech_stack.items():
        mapped_domain = domain_mapping.get(tech_domain, "UNMAPPED")
        tech_requirements += f"  - {tech_domain} (maps to: {mapped_domain}): {technologies}\n"
    
    prompt = f"""
CRITICAL INSTRUCTIONS: You are a STRICT domain-first team selection expert. You MUST follow these rules:

1. ONLY select candidates from domains that are EXPLICITLY REQUESTED in the tech stack
2. NEVER select candidates from domains that are NOT in the request
3. If no candidates are available for a requested domain, do NOT substitute with other domains

REQUESTED DOMAINS ONLY: {list(requested_domains)}

TECH STACK REQUIREMENTS (with domain mapping):
{tech_requirements}

AVAILABLE CANDIDATES (ONLY from requested domains):
{candidates_context}

SELECTION CRITERIA (in strict priority order):
1. DOMAIN MATCH (MANDATORY) - Candidate domain MUST match requested domain
2. MANAGER SCORE - Prefer candidates with score >= {manager_score_threshold}
3. TECH STACK ALIGNMENT - Prefer candidates with matching technologies

TEAM SIZE TARGET: {math.ceil(avg_team_size)} people maximum

SELECTION ALGORITHM:
1. For each requested domain in {list(requested_domains)}:
   a) Find all available candidates in that domain
   b) If candidates exist, select the BEST one based on:
      - Manager score >= {manager_score_threshold} (preferred)
      - Highest tech stack match with required technologies
      - Highest overall manager score as tiebreaker
   c) If NO candidates exist in that domain, skip it (don't substitute)

2. Stop when team size reaches {math.ceil(avg_team_size)} or all requested domains are covered

OUTPUT FORMAT (raw JSON only, no markdown):
{{
    "team_selection": [
        {{
            "name": "candidate_name",
            "domain": "candidate_domain",
            "skills": ["skill1", "skill2"],
            "manager_score": 4.5,
            "selection_reason": "Domain: [domain] | Manager Score: [score] >= {manager_score_threshold} | Tech Match: [matched_techs]",
            "tech_stack_match": ["matched_tech1", "matched_tech2"],
            "requested_for_domain": "original_tech_stack_domain"
        }}
    ],
    "selection_summary": {{
        "total_selected": 2,
        "requested_domains": {list(requested_domains)},
        "covered_domains": ["frontend", "backend"],
        "uncovered_domains": [],
        "avg_manager_score": 4.2,
        "manager_threshold_met": 2
    }}
}}

STRICT RULES:
- NEVER select from domains not in: {list(requested_domains)}
- NEVER substitute domains (e.g., don't pick devops if only frontend is requested)
- NEVER exceed team size of {math.ceil(avg_team_size)}
- ALWAYS prioritize: Domain Match → Manager Score → Tech Alignment
- If a requested domain has no candidates, leave it uncovered rather than substituting
"""
    
    return prompt

@app.post("/generate-team", response_model=List[CandidateOutput])
async def generate_team(spec_data: dict):
    # Parse the uploaded JSON file
    spec_data = spec_data["specsheet"]
    
    # Extract requirements from project spec
    requirements = extract_requirements_from_spec(spec_data)
    tech_stack = requirements.get("tech_stack", {})
    avg_team_size = requirements.get("avg_team_size", 3.0)
    manager_score_threshold = requirements.get("manager_score_threshold", 4.0)
    max_team_size = math.ceil(avg_team_size)

    print(f"\n=== EXTRACTED REQUIREMENTS ===")
    print(f"Tech Stack: {tech_stack}")
    print(f"Avg Team Size: {avg_team_size}")
    print(f"Manager Score Threshold: {manager_score_threshold}")

    # Map tech stack domains to candidate domains
    domain_mapping = map_tech_stack_to_candidate_domains(tech_stack)
    
    # Filter out unmapped domains and get only valid requested domains
    requested_candidate_domains = set()
    valid_domain_mapping = {}
    
    for tech_domain, candidate_domain in domain_mapping.items():
        if candidate_domain in ALLOWED_DOMAINS:
            requested_candidate_domains.add(candidate_domain)
            valid_domain_mapping[tech_domain] = candidate_domain
        else:
            print(f"WARNING: Tech domain '{tech_domain}' could not be mapped to any valid candidate domain")
    
    if not requested_candidate_domains:
        raise HTTPException(
            status_code=400, 
            detail=f"No valid domains found in tech stack. Available domains: {ALLOWED_DOMAINS}"
        )

    print(f"\n=== DOMAIN MAPPING ===")
    print(f"Original tech stack domains: {list(tech_stack.keys())}")
    print(f"Mapped to candidate domains: {list(requested_candidate_domains)}")
    print(f"Domain mapping: {valid_domain_mapping}")

    # Get available candidates ONLY from requested domains
    available_by_domain = extract_available_candidates_by_domain(requested_candidate_domains)
    
    print(f"\n=== AVAILABLE CANDIDATES BY REQUESTED DOMAIN ===")
    for domain, candidates_list in available_by_domain.items():
        print(f"{domain}: {[c['name'] for c in candidates_list]}")

    # Create smart domain-restricted prompt
    smart_prompt = create_smart_domain_prompt(tech_stack, avg_team_size, 
                                            manager_score_threshold, available_by_domain,
                                            valid_domain_mapping)

    # Hardcoded GROQ API key
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "You are a strict domain-first talent matching expert. You ONLY select candidates from explicitly requested domains. Never substitute or add candidates from unrequested domains."
                },
                {
                    "role": "user", 
                    "content": smart_prompt
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=2000
        )

        raw_response = chat_completion.choices[0].message.content
        cleaned_response = re.sub(r"```(?:json|markdown)?", "", raw_response).strip("` \n")

        print("\n=== RAW RESPONSE FROM GROQ ===\n", raw_response)
        print("\n=== CLEANED RESPONSE ===\n", cleaned_response)

        parsed_json = json.loads(cleaned_response)
        team_selection = parsed_json.get("team_selection", [])
        
        if not isinstance(team_selection, list):
            raise ValueError("Expected 'team_selection' to be a list")

    except Exception as e:
        print(f"Error with GROQ API: {str(e)}")
        team_selection = []

    # Smart domain-restricted validation and processing
    final_team = []
    used_candidates = set()
    
    # First, validate AI selections are from requested domains only
    valid_ai_selections = []
    for selection in team_selection:
        candidate_name = selection.get("name", "")
        candidate_domain = selection.get("domain", "")
        
        if candidate_domain in requested_candidate_domains:
            candidate_match = None
            for candidate in candidates:
                if (candidate["name"] == candidate_name and 
                    candidate["domain"] == candidate_domain and 
                    candidate["availability"] and
                    candidate_name not in used_candidates):
                    candidate_match = candidate
                    break
            
            if candidate_match:
                valid_ai_selections.append(candidate_match)
                used_candidates.add(candidate_name)
        else:
            print(f"WARNING: AI selected {candidate_name} from unrequested domain {candidate_domain}. Ignoring.")

    final_team.extend([{
        "name": c["name"],
        "domain": c["domain"],
        "skills": c["skills"],
        "manager_score": c["manager_score"]
    } for c in valid_ai_selections[:max_team_size]])

    # If AI didn't provide enough valid selections, use smart fallback
    if len(final_team) < max_team_size:
        print("Using smart domain-restricted fallback selection...")
        
        for requested_domain in requested_candidate_domains:
            if len(final_team) >= max_team_size:
                break
            
            domain_candidates = []
            if requested_domain in available_by_domain:
                for candidate in available_by_domain[requested_domain]:
                    if candidate["name"] not in used_candidates:
                        domain_candidates.append(candidate)
            
            if domain_candidates:
                domain_tech_requirements = []
                for tech_domain, candidate_domain in valid_domain_mapping.items():
                    if candidate_domain == requested_domain:
                        domain_tech_requirements.extend(tech_stack[tech_domain])
                
                required_techs = set(domain_tech_requirements)
                
                for candidate in domain_candidates:
                    candidate_techs = set(candidate["skills"])
                    tech_overlap = len(required_techs & candidate_techs)
                    candidate["tech_alignment"] = tech_overlap
                
                domain_candidates.sort(key=lambda c: (
                    c["manager_score"] >= manager_score_threshold,
                    c["tech_alignment"],
                    c["manager_score"]
                ), reverse=True)
                
                best_candidate = domain_candidates[0]
                final_team.append({
                    "name": best_candidate["name"],
                    "domain": best_candidate["domain"],
                    "skills": best_candidate["skills"],
                    "manager_score": best_candidate["manager_score"]
                })
                used_candidates.add(best_candidate["name"])
            else:
                print(f"No available candidates found for requested domain: {requested_domain}")

    # Final validation
    validated_team = []
    for member in final_team:
        if member["domain"] in requested_candidate_domains:
            validated_team.append(member)
        else:
            print(f"ERROR: Removing {member['name']} - domain {member['domain']} not requested")

    print(f"\n=== SMART DOMAIN-RESTRICTED TEAM SELECTION SUMMARY ===")
    print(f"Requested domains: {list(requested_candidate_domains)}")
    print(f"Team composition by domain: {[member['domain'] for member in validated_team]}")
    print(f"Manager scores: {[member['manager_score'] for member in validated_team]}")
    print(f"Manager threshold compliance: {sum(1 for m in validated_team if m['manager_score'] >= manager_score_threshold)}/{len(validated_team)}")
    print(f"Team size: {len(validated_team)}/{max_team_size}")
    
    covered_domains = set(member['domain'] for member in validated_team)
    uncovered_domains = requested_candidate_domains - covered_domains
    if uncovered_domains:
        print(f"Uncovered requested domains: {list(uncovered_domains)}")

    return validated_team

# Health check endpoints
@app.get("/")
def read_root():
    return {"message": "Smart Domain-First Team Generation API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "groq_api_key": "hardcoded_in_application",
        "selection_strategy": "smart_domain_first_restricted"
    }