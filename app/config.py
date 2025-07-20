"""Configuration settings for the Team Matching API"""

import os
from typing import List

class Settings:
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "Team Matching API"
    API_DESCRIPTION: str = "API for intelligent team member matching and project assignment"
    API_VERSION: str = "1.0.0"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    # Data Configuration
    DATA_FILE_PATH: str = os.getenv("DATA_FILE_PATH", "data.json")
    
    # Algorithm Configuration
    DEFAULT_WEIGHTS = {
        "skill_match": 0.3,
        "availability": 0.25,
        "experience": 0.2,
        "cost": 0.1,
        "location": 0.1,
        "certification": 0.05
    }

settings = Settings()