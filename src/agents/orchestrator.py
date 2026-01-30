"""
Main Orchestration Engine
Ties everything together: Intent → Planning → Flights → Output
"""
from typing import Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime
import json

from .intent_extractor import intent_extractor, TravelIntent
from .trip_planner import trip_planner, TripPlan
from ..api.flights import flight_api, FlightSearchResult
from ..core.metrics import tracker

class TripRecommendation(BaseModel):
    """Complete trip recommendation with everything"""
    intent: TravelIntent
    trip_plan: TripPlan
    outbound_flights: Optional[FlightSearchResult] = None
    return_flights: Optional[FlightSearchResult] = None
    total_cost_estimate: float = 0.0
    generation_time_ms: float = 0.0
    confidence_score: float = 0.0

class TripGenieOrchestrator:
    """
    Main orchestrator for TripGenie
    Handles the full pipeline from user query to complete trip recommendation
    """
    
    def __init__(self, use_real_apis: bool = False):
        """
        Args:
            use_real_apis: If True, use real Amadeus API. If False, use mocks.
        """
        self.use_real_apis = use_real_apis
        self.conversation_history: List[Dict] = []
    
    def process_query(
        self, 
        user_query: str,
        include_flights: bool = True,
        context: Optional[Dict] = None
    ) -> TripRecommendation:
        """
        Process user query end-to-end
        
        Args:
            user_query: Natural language travel request
            include_flights: Whether to search for flights
            context: Optional context (RAG results, preferences, etc.)
            
        Returns:
            Complete trip recommendation
        """
        
        start_time = datetime.now()
        
        # Step 1: Extract Intent
        print("🧠 Extracting travel intent...")
        intent = intent_extractor.extract(user_query, context=context)
        print(f"   Destination: {intent.destination}")
        print(f"   Dates: {intent.start_date} to {intent.end_date}")
        print(f"   Budget: ${intent.budget_usd}")
        print(f"   Confidence: {intent.confidence_score:.2f}")
        
        # Validate intent
        is_valid, missing = intent_extractor.validate_intent(intent)
        if not is_valid:
            print(f"⚠️  Missing required fields: {', '.join(missing)}")
            # For MVP, we'll continue with partial intent
        
        # Step 2: Generate Trip Plan
        print("\n📋 Generating trip itinerary...")
        trip_plan = trip_planner.plan_trip(intent, context)
        print(f"   {trip_plan.duration_days} day trip to {trip_plan.destination}")
        print(f"   Estimated cost: ${trip_plan.total_estimated_cost}")
        
        # Step 3: Search Flights (if requested)
        outbound_flights = None
        return_flights = None
        
        if include_flights and intent.destination and intent.start_date:
            print("\n✈️  Searching flights...")
            
            # Get airport codes (simplified - in production, use geocoding API)
            origin_code = self._get_airport_code(context.get('origin', 'NYC') if context else 'NYC')
            dest_code = self._get_airport_code(intent.destination)
            
            if self.use_real_apis:
                outbound_flights = flight_api.search_flights(
                    origin=origin_code,
                    destination=dest_code,
                    departure_date=intent.start_date,
                    return_date=intent.end_date,
                    adults=intent.num_travelers,
                    cabin_class=intent.flight_class.upper()
                )
            else:
                # Use mock data
                outbound_flights = flight_api.get_mock_flights(
                    origin=origin_code,
                    destination=dest_code,
                    departure_date=intent.start_date or "2026-03-15"
                )
            
            if outbound_flights.search_success and outbound_flights.offers:
                cheapest = min(outbound_flights.offers, key=lambda x: x.price_usd)
                print(f"   Found {len(outbound_flights.offers)} flights")
                print(f"   Cheapest: ${cheapest.price_usd} ({cheapest.airline})")
        
        # Step 4: Calculate Total Cost
        total_cost = trip_plan.total_estimated_cost
        
        if outbound_flights and outbound_flights.offers:
            flight_cost = min(o.price_usd for o in outbound_flights.offers) * intent.num_travelers
            if intent.end_date:  # Round trip
                flight_cost *= 2
            total_cost += flight_cost
        
        # Step 5: Calculate confidence
        confidence = self._calculate_confidence(intent, trip_plan, outbound_flights)
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Build recommendation
        recommendation = TripRecommendation(
            intent=intent,
            trip_plan=trip_plan,
            outbound_flights=outbound_flights,
            return_flights=return_flights,
            total_cost_estimate=total_cost,
            generation_time_ms=generation_time,
            confidence_score=confidence
        )
        
        print(f"\n✅ Trip recommendation generated in {generation_time:.0f}ms")
        print(f"   Total estimated cost: ${total_cost:.2f}")
        print(f"   Overall confidence: {confidence:.2f}")
        
        return recommendation
    
    def _get_airport_code(self, location: str) -> str:
        """
        Map location to IATA airport code
        In production, use a proper geocoding/airport API
        """
        # Simple mapping for demo
        airport_map = {
            'bangkok': 'BKK',
            'thailand': 'BKK',
            'new york': 'JFK',
            'nyc': 'JFK',
            'london': 'LHR',
            'paris': 'CDG',
            'tokyo': 'NRT',
            'singapore': 'SIN',
            'dubai': 'DXB',
            'hong kong': 'HKG',
            'bali': 'DPS',
            'phuket': 'HKT',
            'mumbai': 'BOM',
            'delhi': 'DEL',
            'sydney': 'SYD',
        }
        
        location_lower = location.lower()
        for key, code in airport_map.items():
            if key in location_lower:
                return code
        
        # Default fallback
        return 'JFK'
    
    def _calculate_confidence(
        self,
        intent: TravelIntent,
        trip_plan: TripPlan,
        flights: Optional[FlightSearchResult]
    ) -> float:
        """
        Calculate overall confidence score
        Based on: intent quality, plan completeness, flight availability
        """
        
        scores = []
        
        # Intent confidence (0-1)
        scores.append(intent.confidence_score)
        
        # Plan completeness (0-1)
        plan_score = 1.0
        if not trip_plan.daily_plans:
            plan_score = 0.0
        elif len(trip_plan.daily_plans) < (intent.duration_days or 1):
            plan_score = 0.7
        scores.append(plan_score)
        
        # Flight availability (0-1)
        if flights:
            flight_score = 1.0 if flights.search_success and flights.offers else 0.5
            scores.append(flight_score)
        
        # Average of all scores
        return sum(scores) / len(scores) if scores else 0.5
    
    def export_recommendation(
        self,
        recommendation: TripRecommendation,
        filepath: str,
        format: str = "json"
    ) -> None:
        """
        Export recommendation to file
        
        Args:
            recommendation: Trip recommendation to export
            filepath: Output file path
            format: 'json' or 'markdown'
        """
        
        if format == "json":
            with open(filepath, 'w') as f:
                json.dump(recommendation.model_dump(), f, indent=2, default=str)
        
        elif format == "markdown":
            md = self._format_as_markdown(recommendation)
            with open(filepath, 'w') as f:
                f.write(md)
    
    def _format_as_markdown(self, rec: TripRecommendation) -> str:
        """Format recommendation as readable markdown"""
        
        md = f"""# Trip to {rec.trip_plan.destination}

## Overview
- **Duration:** {rec.trip_plan.duration_days} days
- **Dates:** {rec.intent.start_date or 'Flexible'} to {rec.intent.end_date or 'Flexible'}
- **Travelers:** {rec.intent.num_travelers}
- **Budget:** ${rec.intent.budget_usd or 'Flexible'}
- **Total Estimated Cost:** ${rec.total_cost_estimate:.2f}

## Daily Itinerary

"""
        
        for day in rec.trip_plan.daily_plans:
            md += f"""### Day {day.day} - {day.date}

**Morning:** {day.morning}

**Afternoon:** {day.afternoon}

**Evening:** {day.evening}

**Estimated Cost:** ${day.estimated_cost_usd}

{f"**Notes:** {day.notes}" if day.notes else ""}

---

"""
        
        md += f"""## Highlights
{chr(10).join(f"- {h}" for h in rec.trip_plan.highlights)}

## Practical Tips
{chr(10).join(f"- {t}" for t in rec.trip_plan.practical_tips)}
"""
        
        if rec.outbound_flights and rec.outbound_flights.offers:
            md += "\n## Flight Options\n\n"
            for i, offer in enumerate(rec.outbound_flights.offers[:3], 1):
                md += f"""### Option {i} - ${offer.price_usd}
- **Airline:** {offer.airline}
- **Departure:** {offer.departure_time}
- **Duration:** {offer.duration_hours:.1f} hours
- **Stops:** {offer.stops}

"""
        
        return md

# Global instance
orchestrator = TripGenieOrchestrator(use_real_apis=False)
