import json
import re
import google.generativeai as genai
from typing import Dict, Any

from app.core.config import settings

class GeminiClient:
    def __init__(self):
        # Configure the Gemini client
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Configure the model with structured output
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ]
        
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
        
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
                if json_end > json_start:
                    response_text = response_text[json_start:json_end].strip()
            
            # Sometimes the model includes plain ```
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.rfind("```")
                if json_end > json_start:
                    response_text = response_text[json_start:json_end].strip()
            
            # Clean the JSON string, removing common issues
            # Fix trailing commas in arrays and objects
            clean_text = re.sub(r',\s*}', '}', response_text)
            clean_text = re.sub(r',\s*\]', ']', clean_text)
            
            # Fix missing commas
            clean_text = re.sub(r'"\s*"', '", "', clean_text)
            clean_text = re.sub(r'}\s*{', '}, {', clean_text)
            clean_text = re.sub(r']\s*{', '], {', clean_text)
            clean_text = re.sub(r'}\s*\[', '}, [', clean_text)
            
            # Try to parse the JSON
            json_data = json.loads(clean_text)
            return json_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Raw response text: {response_text}")
            raise Exception(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            # Log the error and return a simplified error response
            print(f"Error generating content: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}")