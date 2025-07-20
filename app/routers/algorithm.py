from fastapi import APIRouter, HTTPException, Depends

from app.dependencies import get_algorithm
from app.models.requests import UpdateWeightsRequest
from team_matching.algorithm import TeamMatchingAlgorithm

router = APIRouter()

@router.get("/weights")
async def get_algorithm_weights(algo: TeamMatchingAlgorithm = Depends(get_algorithm)):
    """Get current algorithm scoring weights"""
    return algo.weights

@router.put("/weights")
async def update_algorithm_weights(
    weights: UpdateWeightsRequest, 
    algo: TeamMatchingAlgorithm = Depends(get_algorithm)
):
    """Update algorithm scoring weights"""
    updated_weights = {}
    
    for key, value in weights.dict(exclude_unset=True).items():
        if value is not None:
            algo.weights[key] = value
            updated_weights[key] = value
    
    # Validate weights sum to approximately 1.0
    total_weight = sum(algo.weights.values())
    if abs(total_weight - 1.0) > 0.01:
        raise HTTPException(
            status_code=400, 
            detail=f"Weights must sum to approximately 1.0, current sum: {total_weight}"
        )
    
    return {
        "message": "Algorithm weights updated successfully",
        "updated_weights": updated_weights,
        "current_weights": algo.weights
    }