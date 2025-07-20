from fastapi import HTTPException
from team_matching.algorithm import TeamMatchingAlgorithm

# Global algorithm instance - will be set during app startup
algorithm: TeamMatchingAlgorithm = None

def get_algorithm() -> TeamMatchingAlgorithm:
    """Dependency to get the algorithm instance"""
    if algorithm is None:
        raise HTTPException(status_code=500, detail="Algorithm not initialized")
    return algorithm