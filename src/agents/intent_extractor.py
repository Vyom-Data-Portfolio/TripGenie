"""
Intent Understanding Module
Extracts structured travel intent from natural language using Claude
"""
from anthropic import Anthropic
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from typing import Optional, List, Dict
import json

from ..core.config import config
from ..core.metrics import tracker

class TravelIntent(BaseModel):
    """Structured representation of user's travel intent"""
    
    # Core requirements
    destination: Optional[str] = Field(None, description="Desired destination(s)")
    start_date: Optional[str] = Field(None, description="Trip start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Trip end date (YYYY-MM-DD)")
    duration_days: Optional[int] = Field(None, description="Trip duration in days")
    
    # Traveler info
    num_travelers: int = Field(1, description="Number of travelers")
    traveler_type: Optional[str] = Field(None, description="solo/couple/family/group")
    
    # Budget
    budget_usd: Optional[float] = Field(None, description="Total budget in USD")
    budget_flexibility: str = Field("moderate", description="strict/moderate/flexible")
    
    # Preferences
    interests: List[str] = Field(default_factory=list, description="Activities/interests")
    accommodation_type: Optional[str] = Field(None, description="hotel/hostel/resort/airbnb")
    pace: Optional[str] = Field("moderate", description="relaxed/moderate/packed")
    
    # Flight preferences
    flight_class: str = Field("economy", description="economy/business/first")
    direct_flights_only: bool = Field(False, description="Prefer direct flights")
    
    # Constraints
    must_include: List[str] = Field(default_factory=list, description="Must-visit places")
    must_avoid: List[str] = Field(default_factory=list, description="Places/activities to avoid")
    
    # Metadata
    original_query: str = Field("", description="Original user query")
    confidence_score: float = Field(0.0, description="Extraction confidence 0-1")

class IntentExtractor:
    """
    Extracts structured travel intent using Claude
    Uses function calling for reliable structured output
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.PRIMARY_MODEL
        
    def extract(self, user_query: str, context: Optional[Dict] = None) -> TravelIntent:
        """
        Extract travel intent from natural language
        
        Args:
            user_query: User's travel request in natural language
            
        Returns:
            TravelIntent object with structured data
        """
        
        tracker.start_request()
        
        system_prompt = """You are a travel intent extraction expert. 
Extract structured travel information from user queries.

Be smart about:
- Inferring missing information from context
- Converting relative dates (e.g., "next week") to actual dates
- Estimating budgets from travel style descriptions
- Identifying interests from activity mentions
- Setting reasonable defaults

If information is truly ambiguous or missing, leave it as null.
Provide a confidence score (0-1) for the overall extraction quality."""

        user_prompt = f"""Extract travel intent from this query:

"{user_query}"

Today's date is: {datetime.now().strftime('%Y-%m-%d')}

User's location: {context.get('user_location', 'Not specified') if context else 'Not specified'}

IMPORTANT: If the destination is vague (e.g., "beach vacation", "mountains"), 
consider the user's location. Prefer domestic destinations unless explicitly 
mentioned otherwise.

Return a JSON object with the travel intent details."""

        try:
            # Use Claude with JSON mode for structured output
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.0,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract response
            response_text = response.content[0].text
            
            # Parse JSON from response
            # Claude might wrap it in markdown, so clean it
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            intent_data = json.loads(response_text)
            intent_data['original_query'] = user_query
            
            # Track metrics
            tracker.end_request(
                operation="intent_extraction",
                model=self.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                success=True
            )
            
            return TravelIntent(**intent_data)
            
        except Exception as e:
            # Fallback: basic intent with original query
            tracker.end_request(
                operation="intent_extraction",
                model=self.model,
                input_tokens=0,
                output_tokens=0,
                success=False,
                error=str(e)
            )
            
            return TravelIntent(
                original_query=user_query,
                confidence_score=0.1
            )
    
    def validate_intent(self, intent: TravelIntent) -> tuple[bool, List[str]]:
        """
        Validate extracted intent for completeness
        
        Returns:
            (is_valid, list_of_missing_fields)
        """
        missing = []
        
        if not intent.destination:
            missing.append("destination")
        
        if not intent.start_date and not intent.duration_days:
            missing.append("dates or duration")
            
        if intent.confidence_score < 0.3:
            missing.append("high confidence extraction")
        
        return len(missing) == 0, missing

# Global instance
intent_extractor = IntentExtractor()
