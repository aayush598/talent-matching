# app/__init__.py
"""Team Matching API application package"""

# app/models/__init__.py
"""Pydantic models for API requests and responses"""

from .requests import (
    SkillRequest,
    TeamMemberRequest,
    ProjectRequirementRequest,
    ProjectRequest,
    UpdateWeightsRequest,
)

from .responses import (
    SkillResponse,
    TeamMemberResponse,
    ProjectResponse,
    MatchScoreResponse,
    TeamReportResponse,
)

__all__ = [
    "SkillRequest",
    "TeamMemberRequest",
    "ProjectRequirementRequest",
    "ProjectRequest",
    "UpdateWeightsRequest",
    "SkillResponse",
    "TeamMemberResponse",
    "ProjectResponse",
    "MatchScoreResponse",
    "TeamReportResponse",
]
