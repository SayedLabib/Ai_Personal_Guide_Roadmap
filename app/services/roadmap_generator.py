from fastapi import Depends
from datetime import date, time, timedelta, datetime
import json

from app.models.roadmap import (
    PersonalRoadmap, DailyCard, Task, TimeSlot, 
    WeeklyTheme, Quest, Resource, Goal
)
from app.utils.gemini_client import GeminiClient

class RoadmapGeneratorService:
    def __init__(self, gemini_client: GeminiClient = Depends()):
        self.gemini_client = gemini_client
    
    async def generate_weekly_roadmap(self, persona_type: str, duration_months: int, user_id: str = None) -> PersonalRoadmap:
        """Generate a personalized roadmap with weekly themes and quests"""
        # Calculate date range
        start_date = date.today()
        end_date = start_date + timedelta(days=30*duration_months)
        
        # Create a prompt for Gemini
        prompt = f"""
        Create a personalized roadmap for someone with a {persona_type} personality type.
        The roadmap should cover {duration_months} month(s) starting from {start_date}.
        
        Please structure the roadmap with:
        1. Overall goals (short-term and long-term)
        2. Weekly themes, where each week has a different focus
        3. For each week, create 2-3 "quests" - specific learning tasks or activities
        4. Each quest should have: task type, name, time commitment, detailed activity description, and learning resources
        
        Return your response as a JSON with the following structure:
        {{
          "user_id": "{user_id if user_id else 'user123'}",
          "persona_type": "{persona_type}",
          "start_date": "{start_date.isoformat()}",
          "end_date": "{end_date.isoformat()}",
          "duration_months": {duration_months},
          "overall_goals": {{
            "short_term": [
              "Short term goal 1",
              "Short term goal 2",
              "Short term goal 3"
            ],
            "long_term": [
              "Long term goal 1",
              "Long term goal 2",
              "Long term goal 3"
            ]
          }},
          "weeks": [
            {{
              "week_number": 1,
              "theme": "Theme for Week 1",
              "quests": [
                {{
                  "task_type": "Learn/Build/Reflect/Collaborate/etc.",
                  "task_name": "Specific task name",
                  "resources": [
                    {{
                      "title": "Resource title",
                      "link": "https://resource.link"
                    }}
                  ],
                  "time_commitment": "Time needed (e.g., '1 hour/day (evening)')",
                  "activity": "Detailed description of what to do"
                }}
              ]
            }}
          ]
        }}
        
        Tailor the content specifically to the {persona_type} personality type.
        For the resources, include actual relevant websites, courses, or tutorials that exist.
        Make the activities specific, challenging but achievable, and appropriate for the persona type.
        For a {duration_months} month roadmap, create {duration_months * 4} weeks of content.
        """
        
        # Call Gemini API and parse response
        response_data = await self.gemini_client.generate_content(prompt)
        
        # Process the response to create the roadmap
        weeks = []
        for week_data in response_data.get("weeks", []):
            quests = []
            for quest_data in week_data.get("quests", []):
                resources = []
                for resource_data in quest_data.get("resources", []):
                    resource = Resource(
                        title=resource_data["title"],
                        link=resource_data["link"]
                    )
                    resources.append(resource)
                
                quest = Quest(
                    task_type=quest_data["task_type"],
                    task_name=quest_data["task_name"],
                    resources=resources,
                    time_commitment=quest_data["time_commitment"],
                    activity=quest_data["activity"]
                )
                quests.append(quest)
            
            week = WeeklyTheme(
                week_number=week_data["week_number"],
                theme=week_data["theme"],
                quests=quests
            )
            weeks.append(week)
        
        # Create overall goals
        goals_data = response_data.get("overall_goals", {})
        goals = Goal(
            short_term=goals_data.get("short_term", []),
            long_term=goals_data.get("long_term", [])
        )
        
        # Convert response to PersonalRoadmap
        roadmap = PersonalRoadmap(
            user_id=user_id,
            persona_type=persona_type,
            duration_months=duration_months,
            start_date=start_date,
            end_date=end_date,
            weeks=weeks,
            overall_goals=goals
        )
        
        return roadmap
    
    async def generate_daily_roadmap(self, persona_type: str, duration_months: int, user_id: str = None) -> PersonalRoadmap:
        """Generate a personalized roadmap based on persona type with daily tasks"""
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
            "overall_goals": {{
                "short_term": ["Short term goal 1", "Short term goal 2", "Short term goal 3"],
                "long_term": ["Long term goal 1", "Long term goal 2", "Long term goal 3"]
            }},
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
        for card in response_data.get("daily_cards", []):
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
        
        # Create overall goals
        goals_data = response_data.get("overall_goals", {})
        if isinstance(goals_data, list):
            # Handle legacy format
            goals = Goal(
                short_term=goals_data[:3] if len(goals_data) >= 3 else goals_data,
                long_term=goals_data[3:] if len(goals_data) > 3 else []
            )
        else:
            goals = Goal(
                short_term=goals_data.get("short_term", []),
                long_term=goals_data.get("long_term", [])
            )
        
        # Convert response to PersonalRoadmap
        roadmap = PersonalRoadmap(
            user_id=user_id,
            persona_type=persona_type,
            duration_months=duration_months,
            start_date=start_date,
            end_date=end_date,
            daily_cards=processed_cards,
            overall_goals=goals
        )
        
        return roadmap
        
    async def generate_roadmap(self, persona_type: str, duration_months: int, user_id: str = None, format_type: str = "weekly") -> PersonalRoadmap:
        """Generate a personalized roadmap based on persona type and format preference"""
        if format_type == "weekly":
            return await self.generate_weekly_roadmap(persona_type, duration_months, user_id)
        else:
            return await self.generate_daily_roadmap(persona_type, duration_months, user_id)