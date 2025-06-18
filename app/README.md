# AI Personal Guide

A FastAPI application that uses a survey to detect personality types and generate personalized roadmaps for personal growth and career guidance.

## Features

1. **Survey-Based Persona Detection**
   - Collects answers to personality questions
   - Detects personality type/archetype
   - Suggests career alignment

2. **AI-Generated Roadmap**
   - Generates a daily task schedule for 3 or 6 months
   - Each day is represented as a card
   - Each card has 4-5 highly specific activities/tasks with schedules
   - Focus on skills, growth, and learning

## Technology Stack

- FastAPI
- Pydantic
- Google Gemini-2.0 flash model
- Docker

## Getting Started

### Prerequisites

- Python 3.8+
- Google AI Studio API key (for Gemini model)

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/your-username/ai-personal-guide.git
cd ai-personal-guide