from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.models.roadmap import PersonalRoadmap
from app.services.roadmap_generator import RoadmapGeneratorService

router = APIRouter()

@router.post("/generate", response_model=PersonalRoadmap)
async def generate_roadmap(
    persona_type: str,
    duration_months: int = 3,
    user_id: Optional[str] = None,
    roadmap_generator: RoadmapGeneratorService = Depends()
):
    """Generate a personalized roadmap based on persona type"""
    try:
        if duration_months not in [3, 6]:
            raise HTTPException(status_code=400, detail="Duration must be either 3 or 6 months")
            
        roadmap = await roadmap_generator.generate_roadmap(persona_type, duration_months, user_id)
        return roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))