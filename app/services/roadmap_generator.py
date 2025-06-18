from fastapi import Depends
from datetime import date, time, timedelta, datetime
import json

from app.models.roadmap import PersonalRoadmap, DailyCard, Task, TimeSlot
from app.utils.gemini_client import GeminiClient

class RoadmapGeneratorService:
    def __init__(self, gemini_client: GeminiClient = Depends()):
        self.gemini_client = gemini_client
        
    async def generate_roadmap(self, persona_type: str, duration_months: int, user_id: str = None) -> PersonalRoadmap:
        """Generate a personalized roadmap based on persona type"""
        # Calculate date range
        start_date = date.today()
        end_date = start_date + timedelta(days=30*duration_months)
        
        # Create a prompt for Gemini
        prompt = f"""
        Create a personalized daily roadmap for a person with the personality type: {persona_type}.
        The roadmap should cover {duration_months} months starting from {start_date}.
        
        For each day, create a card with 4-5 specific activities or tasks focused on skills, growth, and learning.
        Each task should have a specific time scheduled from morning to night, with start_time and end_time.
        
        Return your response as a JSON with the following structure:
        {{
            "overall_goals": ["goal 1", "goal 2", "goal 3"],
            "daily_cards": [
                {{
                    "date": "YYYY-MM-DD",
                    "focus_area": "Focus area for the day",
                    "tasks": [
                        {{
                            "title": "Task title",
                            "description": "Detailed task description",
                            "start_time": "08:00",
                            "end_time": "09:30",
                            "time_slot": "morning", 
                            "estimated_time": "90 minutes",
                            "priority": 1,
                            "resources": ["https://resource1.com", "https://resource2.com"]
                        }},
                        ...
                    ],
                    "reflection_prompt": "A question for reflection at the end of the day"
                }},
                ...
            ]
        }}
        
        Note: For demonstration purposes, please generate cards for 3 days. In production, we would generate cards for each day in the {duration_months}-month period.
        Make each task specific, actionable, and tailored to the {persona_type} personality type.
        Time slots should be one of: "morning", "afternoon", "evening", or "night".
        """
        
        # Call Gemini API and parse response
        response_data = await self.gemini_client.generate_content(prompt)
        
        # Process the response to convert string dates and times to proper objects
        processed_cards = []
        for card in response_data["daily_cards"]:
            processed_tasks = []
            for task in card["tasks"]:
                # Convert time strings to time objects
                start_time_parts = task["start_time"].split(":")
                end_time_parts = task["end_time"].split(":")
                
                processed_task = Task(
                    title=task["title"],
                    description=task["description"],
                    start_time=time(int(start_time_parts[0]), int(start_time_parts[1])),
                    end_time=time(int(end_time_parts[0]), int(end_time_parts[1])),
                    time_slot=task["time_slot"],
                    estimated_time=task["estimated_time"],
                    priority=task["priority"],
                    resources=task.get("resources", [])
                )
                processed_tasks.append(processed_task)
            
            # Convert date string to date object
            card_date = datetime.strptime(card["date"], "%Y-%m-%d").date()
            
            processed_card = DailyCard(
                date=card_date,
                focus_area=card["focus_area"],
                tasks=processed_tasks,
                reflection_prompt=card["reflection_prompt"]
            )
            processed_cards.append(processed_card)
        
        # Convert response to PersonalRoadmap
        roadmap = PersonalRoadmap(
            user_id=user_id,
            persona_type=persona_type,
            duration_months=duration_months,
            start_date=start_date,
            end_date=end_date,
            daily_cards=processed_cards,
            overall_goals=response_data["overall_goals"]
        )
        
        return roadmap