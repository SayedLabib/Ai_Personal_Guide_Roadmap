from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import date, time
from enum import Enum

class TimeSlot(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"

class Task(BaseModel):
    title: str
    description: str
    start_time: time
    end_time: time
    time_slot: TimeSlot
    estimated_time: str  # e.g., "30 minutes", "1 hour"
    priority: int = Field(..., ge=1, le=5)  # Priority from 1-5
    resources: Optional[List[str]] = None  # Optional resources links

class Resource(BaseModel):
    title: str
    link: str

class Quest(BaseModel):
    task_type: str  # "Learn", "Build", "Reflect", "Collaborate", etc.
    task_name: str
    resources: List[Resource] = []
    time_commitment: str  # e.g., "1 hour/day (evening)", "30 mins on Sunday"
    activity: str

class WeeklyTheme(BaseModel):
    week_number: int
    theme: str
    quests: List[Quest]

class Goal(BaseModel):
    short_term: List[str]
    long_term: List[str]

class DailyCard(BaseModel):
    date: date
    focus_area: str
    tasks: List[Task] = Field(..., min_items=1, max_items=5)
    reflection_prompt: str

class PersonalRoadmap(BaseModel):
    user_id: Optional[str] = None
    persona_type: str
    start_date: date
    end_date: date
    duration_months: int = Field(..., ge=1, le=12)
    overall_goals: Goal
    weeks: List[WeeklyTheme] = []
    daily_cards: Optional[List[DailyCard]] = None