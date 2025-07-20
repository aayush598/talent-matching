# Team Matching API Documentation

## Overview

The Team Matching API is a FastAPI-based service designed for intelligent team member matching and project assignment. It provides endpoints for managing team members, projects, and finding optimal team compositions based on skills, availability, experience, and other factors.

**Base URL:** `http://localhost:8000`  
**API Version:** 1.0.0  
**Framework:** FastAPI with automatic OpenAPI documentation

## Architecture & Dependencies

### Core Components
- **FastAPI Framework:** Modern, fast web framework for building APIs
- **Pydantic Models:** Data validation and serialization
- **Team Matching Algorithm:** Custom algorithm for team optimization
- **CORS Middleware:** Cross-origin resource sharing support

### Key Imports
```python
from team_matching.algorithm import TeamMatchingAlgorithm
from team_matching.models import TeamMember, Project, Skill, ProjectRequirement, MatchScore
from team_matching.enums import ExperienceLevel, AvailabilityStatus, ProjectPriority
from team_matching.data_loader import create_sample_data_from_file
```

## Data Models

### Team Member Models

#### SkillRequest/SkillResponse
```json
{
  "name": "Python",
  "proficiency": 8,
  "years_experience": 3.5,
  "last_used": "2024-01-15"
}
```

#### TeamMemberRequest/TeamMemberResponse
```json
{
  "id": "TM001",
  "name": "John Doe",
  "email": "john.doe@company.com",
  "department": "Engineering",
  "skills": [/* Array of SkillRequest objects */],
  "experience_level": "SENIOR",
  "availability_status": "AVAILABLE",
  "current_workload": 75.0,
  "hourly_rate": 85.0,
  "preferred_project_types": ["Web Development", "API Design"],
  "location": "New York",
  "timezone": "EST",
  "certifications": ["AWS Solutions Architect"]
}
```

### Project Models

#### ProjectRequirementRequest
```json
{
  "skill_name": "Python",
  "required_proficiency": 7,
  "min_experience_level": "MID",
  "is_mandatory": true,
  "weight": 1.0
}
```

#### ProjectRequest/ProjectResponse
```json
{
  "id": "PRJ001",
  "name": "E-commerce Platform",
  "description": "Building a new e-commerce platform",
  "requirements": [/* Array of ProjectRequirementRequest objects */],
  "start_date": "2024-03-01",
  "end_date": "2024-08-31",
  "priority": "HIGH",
  "budget": 150000.0,
  "team_size": 5,
  "required_certifications": ["AWS", "React"],
  "preferred_locations": ["New York", "Remote"],
  "project_type": "Web Development",
  "estimated_hours": 2000
}
```

### Match Score Models

#### MatchScoreResponse
```json
{
  "member_id": "TM001",
  "member_name": "John Doe",
  "total_score": 87.5,
  "skill_match_score": 90.0,
  "availability_score": 85.0,
  "experience_score": 88.0,
  "cost_score": 75.0,
  "location_score": 95.0,
  "certification_score": 100.0,
  "detailed_breakdown": {/* Detailed scoring information */}
}
```

## API Endpoints

### System Endpoints

#### GET `/`
**Description:** Root endpoint with API information  
**Response:**
```json
{
  "message": "Team Matching API",
  "version": "1.0.0",
  "docs": "/docs",
  "status": "active"
}
```

#### GET `/health`
**Description:** Health check endpoint  
**Response:**
```json
{
  "status": "healthy",
  "members_count": 25,
  "projects_count": 5,
  "timestamp": "2024-01-20T10:30:00"
}
```

### Team Member Management

#### POST `/members`
**Description:** Add a new team member  
**Request Body:** TeamMemberRequest  
**Response:** 201 Created
```json
{
  "message": "Team member John Doe added successfully",
  "member_id": "TM001"
}
```
**Error Responses:**
- 400: Member already exists or validation error
- 500: Server error

#### GET `/members`
**Description:** Get all team members  
**Response:** Array of TeamMemberResponse objects

#### GET `/members/{member_id}`
**Description:** Get a specific team member by ID  
**Parameters:**
- `member_id` (path): Member ID
**Response:** TeamMemberResponse object  
**Error Responses:**
- 404: Member not found

#### PUT `/members/{member_id}`
**Description:** Update an existing team member  
**Parameters:**
- `member_id` (path): Member ID
**Request Body:** TeamMemberRequest  
**Response:**
```json
{
  "message": "Member John Doe updated successfully"
}
```
**Error Responses:**
- 404: Member not found
- 400: Validation error

#### DELETE `/members/{member_id}`
**Description:** Delete a team member  
**Parameters:**
- `member_id` (path): Member ID
**Response:**
```json
{
  "message": "Member John Doe deleted successfully"
}
```
**Error Responses:**
- 404: Member not found

### Project Management

#### POST `/projects`
**Description:** Add a new project  
**Request Body:** ProjectRequest  
**Response:** 201 Created
```json
{
  "message": "Project E-commerce Platform added successfully",
  "project_id": "PRJ001"
}
```
**Error Responses:**
- 400: Project already exists or validation error

#### GET `/projects`
**Description:** Get all projects  
**Response:** Array of ProjectResponse objects

#### GET `/projects/{project_id}`
**Description:** Get a specific project by ID  
**Parameters:**
- `project_id` (path): Project ID
**Response:** ProjectResponse object  
**Error Responses:**
- 404: Project not found

### Team Matching & Analytics

#### GET `/projects/{project_id}/matches`
**Description:** Get all potential team members for a project with match scores  
**Parameters:**
- `project_id` (path): Project ID
- `limit` (query, optional): Limit number of results (≥1)
- `min_score` (query, optional): Minimum match score (0-100)

**Response:** Array of MatchScoreResponse objects sorted by total score  
**Error Responses:**
- 404: Project not found
- 500: Error calculating matches

**Example Usage:**
```
GET /projects/PRJ001/matches?limit=10&min_score=70
```

#### GET `/projects/{project_id}/best-team`
**Description:** Get the optimal team composition for a project  
**Parameters:**
- `project_id` (path): Project ID
- `team_size` (query, optional): Override project team size

**Response:** Array of MatchScoreResponse objects representing the best team  
**Error Responses:**
- 404: Project not found
- 500: Error finding best team

#### GET `/projects/{project_id}/team-report`
**Description:** Generate a comprehensive team report  
**Parameters:**
- `project_id` (path): Project ID
- `team_size` (query, optional): Override project team size

**Response:** TeamReportResponse object
```json
{
  "project": {/* Project details */},
  "team_members": [/* Array of selected team members */],
  "team_statistics": {/* Aggregated team stats */}
}
```

### Algorithm Configuration

#### GET `/algorithm/weights`
**Description:** Get current algorithm scoring weights  
**Response:**
```json
{
  "skill_match": 0.3,
  "availability": 0.25,
  "experience": 0.2,
  "cost": 0.1,
  "location": 0.1,
  "certification": 0.05
}
```

#### PUT `/algorithm/weights`
**Description:** Update algorithm scoring weights  
**Request Body:** UpdateWeightsRequest
```json
{
  "skill_match": 0.35,
  "availability": 0.25,
  "experience": 0.2,
  "cost": 0.1,
  "location": 0.08,
  "certification": 0.02
}
```
**Response:**
```json
{
  "message": "Algorithm weights updated successfully",
  "updated_weights": {/* Changed weights */},
  "current_weights": {/* All current weights */}
}
```
**Error Responses:**
- 400: Weights don't sum to approximately 1.0

### Utility Endpoints

#### GET `/skills/list`
**Description:** Get list of all unique skills across team members  
**Response:**
```json
{
  "skills": ["Python", "JavaScript", "React", "AWS", "Docker"]
}
```

#### GET `/stats`
**Description:** Get comprehensive system statistics  
**Response:**
```json
{
  "members": {
    "total": 25,
    "by_experience": {
      "JUNIOR": 5,
      "MID": 8,
      "SENIOR": 10,
      "LEAD": 2
    },
    "by_availability": {
      "AVAILABLE": 15,
      "PARTIALLY_AVAILABLE": 8,
      "BUSY": 2
    },
    "departments": ["Engineering", "Design", "Product"]
  },
  "projects": {
    "total": 5,
    "by_priority": {
      "HIGH": 2,
      "MEDIUM": 2,
      "LOW": 1
    }
  },
  "skills": {
    "total_unique": 25,
    "list": ["AWS", "Docker", "JavaScript", "Python", "React"]
  }
}
```

## Enumerations

### ExperienceLevel
- `JUNIOR`
- `MID`
- `SENIOR`
- `LEAD`
- `ARCHITECT`

### AvailabilityStatus
- `AVAILABLE`
- `PARTIALLY_AVAILABLE`
- `BUSY`
- `UNAVAILABLE`

### ProjectPriority
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

## Validation Rules

### Skill Proficiency
- Range: 1-10 (integer)
- Description: Skill proficiency level

### Experience Years
- Minimum: 0 (float)
- Description: Years of experience with the skill

### Current Workload
- Range: 0-100 (float)
- Description: Current workload percentage

### Team Size
- Minimum: 1 (integer)
- Description: Required team size for project

### Estimated Hours
- Minimum: 0 (integer)
- Description: Estimated project hours

## Error Handling

The API uses standard HTTP status codes:

- **200:** Success
- **201:** Created successfully
- **400:** Bad request (validation errors, duplicates)
- **404:** Resource not found
- **500:** Internal server error

Error responses follow this format:
```json
{
  "detail": "Error description message"
}
```

## Authentication & Security

Currently, the API does not implement authentication. For production use, consider adding:
- JWT token authentication
- Rate limiting
- Input sanitization
- HTTPS enforcement

## CORS Configuration

The API includes CORS middleware with permissive settings:
```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**Note:** Restrict origins in production environments.

## Startup & Initialization

The API uses an async context manager for lifecycle management:

1. **Startup:** Attempts to load data from `data.json`, falls back to empty algorithm
2. **Runtime:** Maintains global algorithm instance
3. **Shutdown:** Graceful cleanup

## Development Setup

### Running the API
```bash
# Direct execution
python main.py

# Using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Adding a Team Member
```python
import requests

member_data = {
    "id": "TM001",
    "name": "Alice Johnson",
    "email": "alice@company.com",
    "department": "Engineering",
    "skills": [
        {
            "name": "Python",
            "proficiency": 9,
            "years_experience": 5.0,
            "last_used": "2024-01-15"
        }
    ],
    "experience_level": "SENIOR",
    "availability_status": "AVAILABLE",
    "current_workload": 60.0
}

response = requests.post("http://localhost:8000/members", json=member_data)
print(response.json())
```

### Finding Best Team for Project
```python
import requests

response = requests.get("http://localhost:8000/projects/PRJ001/best-team")
team = response.json()

for member in team:
    print(f"{member['member_name']}: {member['total_score']:.2f}")
```

### Updating Algorithm Weights
```python
import requests

new_weights = {
    "skill_match": 0.4,
    "availability": 0.3,
    "experience": 0.2,
    "cost": 0.1
}

response = requests.put("http://localhost:8000/algorithm/weights", json=new_weights)
print(response.json())
```

## Best Practices for Future Development

### 1. Data Consistency
- Always validate input data using Pydantic models
- Handle date formats consistently (YYYY-MM-DD)
- Maintain referential integrity between members and projects

### 2. Error Handling
- Use appropriate HTTP status codes
- Provide meaningful error messages
- Log errors for debugging

### 3. Performance Considerations
- Consider pagination for large datasets
- Implement caching for frequently accessed data
- Optimize matching algorithm for large member pools

### 4. Testing
- Write unit tests for all endpoints
- Test edge cases (empty datasets, invalid IDs)
- Performance test with realistic data volumes

### 5. Documentation
- Keep API documentation updated
- Provide clear examples for complex endpoints
- Document algorithm behavior and scoring logic

## Future Enhancement Opportunities

1. **Database Integration:** Replace in-memory storage with persistent database
2. **Authentication:** Implement secure user authentication
3. **Batch Operations:** Support bulk member/project operations
4. **Advanced Filtering:** Add more sophisticated search and filtering
5. **Notifications:** Email/webhook notifications for team assignments
6. **Analytics Dashboard:** Visual analytics and reporting features
7. **Export Features:** CSV/PDF export for reports and data
8. **Audit Logging:** Track all changes and operations
9. **Multi-tenant Support:** Support multiple organizations
10. **Real-time Updates:** WebSocket support for real-time notifications

This documentation serves as a comprehensive guide for understanding, using, and extending the Team Matching API. Refer to the interactive documentation at `/docs` for real-time API exploration and testing.