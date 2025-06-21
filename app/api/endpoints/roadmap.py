from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Literal
from enum import Enum

from app.models.roadmap import PersonalRoadmap
from app.services.roadmap_generator import RoadmapGeneratorService

router = APIRouter()

class RoadmapFormat(str, Enum):
    WEEKLY = "weekly"
    DAILY = "daily"

@router.post("/generate", response_model=PersonalRoadmap)
async def generate_roadmap(
    persona_type: str,
    duration_months: int = 1,
    user_id: Optional[str] = None,
    format_type: RoadmapFormat = RoadmapFormat.WEEKLY,
    roadmap_generator: RoadmapGeneratorService = Depends()
):
    """Generate a personalized roadmap based on persona type"""
    try:
        if duration_months < 1 or duration_months > 12:
            raise HTTPException(status_code=400, detail="Duration must be between 1 and 12 months")
            
        roadmap = await roadmap_generator.generate_roadmap(
            persona_type=persona_type, 
            duration_months=duration_months, 
            user_id=user_id,
            format_type=format_type
        )
        return roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))