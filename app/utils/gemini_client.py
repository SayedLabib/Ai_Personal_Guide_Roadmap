import json
import google.generativeai as genai
from typing import Dict, Any

from app.core.config import settings

class GeminiClient:
    def __init__(self):
        # Configure the Gemini client
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
    async def generate_content(self, prompt: str) -> Dict[str, Any]:
        """Generate content using Gemini AI"""
        try:
            response = self.model.generate_content(prompt)
            
            # Parse the response as JSON
            response_text = response.text
            # Handle potential formatting issues
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.rfind("```")
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
        except Exception as e:
            # Log the error and return a simplified error response
            print(f"Error generating content: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}")