"""
Trip Planning Agent
Generates day-by-day itineraries using Claude
"""
from anthropic import Anthropic
from typing import Dict, List, Optional
from pydantic import BaseModel
import json

from ..core.config import config
from ..core.metrics import tracker
from .intent_extractor import TravelIntent

class DayPlan(BaseModel):
    """Single day in the itinerary"""
    day: int
    date: str
    morning: str
    afternoon: str
    evening: str
    estimated_cost_usd: float
    notes: str = ""

class TripPlan(BaseModel):
    """Complete trip plan"""
    destination: str
    duration_days: int
    daily_plans: List[DayPlan]
    total_estimated_cost: float
    highlights: List[str]
    practical_tips: List[str]
    
class TripPlannerAgent:
    """
    Main trip planning agent
    Creates detailed day-by-day itineraries
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.PRIMARY_MODEL
    
    def plan_trip(self, intent: TravelIntent, context: Optional[Dict] = None) -> TripPlan:
        """
        Generate complete trip plan from intent
        
        Args:
            intent: Structured travel intent
            context: Optional additional context (RAG results, etc.)
            
        Returns:
            Complete trip plan with day-by-day itinerary
        """
        
        tracker.start_request()
        
        system_prompt = """You are an expert travel planner creating personalized itineraries.

Your itineraries should:
- Balance activities with rest time
- Consider local culture and customs
- Include practical details (opening hours, booking tips)
- Be realistic about timing and distances
- Respect the traveler's budget and preferences
- Include cost estimates

Return a detailed JSON object with the trip plan."""

        # Build user prompt
        user_prompt = self._build_planning_prompt(intent, context)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,  # Slightly creative for variety
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_text = response.content[0].text
            
            # Clean JSON from markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            plan_data = json.loads(response_text)
            
            # Track metrics
            tracker.end_request(
                operation="trip_planning",
                model=self.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                success=True
            )
            
            return TripPlan(**plan_data)
            
        except Exception as e:
            tracker.end_request(
                operation="trip_planning",
                model=self.model,
                input_tokens=0,
                output_tokens=0,
                success=False,
                error=str(e)
            )
            raise
    
    def _build_planning_prompt(self, intent: TravelIntent, context: Optional[Dict]) -> str:
        """Build detailed planning prompt"""
        
        prompt = f"""Create a detailed trip itinerary with these requirements:

DESTINATION: {intent.destination or 'Not specified'}
DURATION: {intent.duration_days or 'Flexible'} days
DATES: {intent.start_date or 'Flexible'} to {intent.end_date or 'Flexible'}
TRAVELERS: {intent.num_travelers} ({intent.traveler_type or 'general'})
BUDGET: ${intent.budget_usd or 'Flexible'} USD ({intent.budget_flexibility} flexibility)

INTERESTS: {', '.join(intent.interests) if intent.interests else 'General sightseeing'}
PACE: {intent.pace}
ACCOMMODATION: {intent.accommodation_type or 'Hotels'}

MUST INCLUDE: {', '.join(intent.must_include) if intent.must_include else 'None'}
AVOID: {', '.join(intent.must_avoid) if intent.must_avoid else 'None'}
"""

        if context and 'destination_info' in context:
            prompt += f"\nDESTINATION CONTEXT:\n{context['destination_info']}\n"
        
        prompt += f"""
Return a JSON object with this structure:
{{
  "destination": "City/Country",
  "duration_days": {intent.duration_days or 'EXACTLY the number of days requested'},
  "daily_plans": [
    {{
      "day": 1,
      "date": "2026-02-15",
      "morning": "Activity description with timing",
      "afternoon": "Activity description", 
      "evening": "Activity description",
      "estimated_cost_usd": 150.0,
      "notes": "Practical tips for the day"
    }}
  ],
  "total_estimated_cost": 750.0,
  "highlights": ["Top experience 1", "Top experience 2"],
  "practical_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

CRITICAL: Create EXACTLY {intent.duration_days or 'the requested number of'} daily_plans entries. No more, no less.
Make it detailed, realistic, and actionable."""
        
        return prompt

# Global instance
trip_planner = TripPlannerAgent()