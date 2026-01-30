"""
Evaluation Framework
Measures trip plan quality, cost accuracy, and system performance
CRITICAL for production ML systems
"""
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import json
from anthropic import Anthropic

from ..agents.orchestrator import TripRecommendation
from ..agents.intent_extractor import TravelIntent
from ..agents.trip_planner import TripPlan
from ..core.config import config
from ..core.metrics import tracker

class EvaluationMetrics(BaseModel):
    """Metrics for a single trip recommendation"""
    
    # Quality Scores (0-10)
    intent_match_score: float = 0.0  # How well plan matches intent
    budget_adherence_score: float = 0.0  # Budget compliance
    feasibility_score: float = 0.0  # Realistic timing/logistics
    completeness_score: float = 0.0  # All required info present
    coherence_score: float = 0.0  # Day-to-day flow makes sense
    
    # Overall
    overall_score: float = 0.0  # Weighted average
    grade: str = "F"  # A, B, C, D, F
    
    # Performance
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    
    # Pass/Fail Checks
    has_critical_errors: bool = False
    error_messages: List[str] = []
    
    # Metadata
    evaluated_at: str = ""

class TripEvaluator:
    """
    Evaluates trip recommendations for quality
    Uses both heuristic rules and LLM-as-judge
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.SECONDARY_MODEL  # Use cheaper model for evaluation
    
    def evaluate(self, recommendation: TripRecommendation) -> EvaluationMetrics:
        """
        Comprehensive evaluation of trip recommendation
        
        Args:
            recommendation: Trip recommendation to evaluate
            
        Returns:
            Detailed evaluation metrics
        """
        
        print("\n📊 Evaluating trip quality...")
        
        metrics = EvaluationMetrics(
            evaluated_at=datetime.now().isoformat(),
            latency_ms=recommendation.generation_time_ms,
            cost_usd=self._calculate_generation_cost()
        )
        
        # 1. Heuristic Checks (fast, deterministic)
        self._run_heuristic_checks(recommendation, metrics)
        
        # 2. LLM-as-Judge (slower, more nuanced)
        if not metrics.has_critical_errors:
            self._run_llm_evaluation(recommendation, metrics)
        
        # 3. Calculate Overall Score
        metrics.overall_score = self._calculate_overall_score(metrics)
        metrics.grade = self._score_to_grade(metrics.overall_score)
        
        print(f"   Overall Score: {metrics.overall_score:.1f}/10 (Grade: {metrics.grade})")
        print(f"   Intent Match: {metrics.intent_match_score:.1f}/10")
        print(f"   Budget Adherence: {metrics.budget_adherence_score:.1f}/10")
        print(f"   Feasibility: {metrics.feasibility_score:.1f}/10")
        
        return metrics
    
    def _run_heuristic_checks(
        self,
        rec: TripRecommendation,
        metrics: EvaluationMetrics
    ) -> None:
        """Run fast heuristic validation checks"""
        
        intent = rec.intent
        plan = rec.trip_plan
        
        # Check 1: Completeness
        completeness = 10.0
        if not plan.daily_plans:
            metrics.error_messages.append("No daily plans generated")
            metrics.has_critical_errors = True
            completeness = 0.0
        elif len(plan.daily_plans) != plan.duration_days:
            metrics.error_messages.append(f"Plan has {len(plan.daily_plans)} days but should have {plan.duration_days}")
            completeness = 5.0
        
        metrics.completeness_score = completeness
        
        # Check 2: Budget Adherence
        if intent.budget_usd and intent.budget_usd > 0:
            budget_ratio = rec.total_cost_estimate / intent.budget_usd
            
            if budget_ratio <= 1.0:
                metrics.budget_adherence_score = 10.0
            elif budget_ratio <= 1.2:  # 20% over
                metrics.budget_adherence_score = 7.0
            elif budget_ratio <= 1.5:  # 50% over
                metrics.budget_adherence_score = 4.0
            else:
                metrics.budget_adherence_score = 2.0
                metrics.error_messages.append(
                    f"Budget exceeded: ${rec.total_cost_estimate:.0f} vs ${intent.budget_usd:.0f}"
                )
        else:
            metrics.budget_adherence_score = 8.0  # No budget = assume OK
        
        # Check 3: Coherence (basic)
        coherence = 10.0
        for i, day in enumerate(plan.daily_plans):
            # Check day numbers are sequential
            if day.day != i + 1:
                coherence -= 2.0
                metrics.error_messages.append(f"Day numbering issue at day {i+1}")
            
            # Check activities exist
            if not day.morning or not day.afternoon or not day.evening:
                coherence -= 1.0
        
        metrics.coherence_score = max(0.0, coherence)
    
    def _run_llm_evaluation(
        self,
        rec: TripRecommendation,
        metrics: EvaluationMetrics
    ) -> None:
        """
        Use LLM to evaluate subjective quality
        Intent match, feasibility, etc.
        """
        
        tracker.start_request()
        
        system_prompt = """You are an expert travel planner evaluating trip itineraries.

Evaluate on these criteria (score 0-10 each):

1. INTENT_MATCH: How well does the plan match the user's stated preferences?
2. FEASIBILITY: Are activities realistic? Proper timing? Achievable in a day?

Return a JSON object with your scores and brief reasoning."""

        user_prompt = f"""Evaluate this trip plan:

USER INTENT:
- Destination preference: {rec.intent.destination}
- Interests: {', '.join(rec.intent.interests) if rec.intent.interests else 'General'}
- Budget: ${rec.intent.budget_usd or 'Flexible'}
- Pace: {rec.intent.pace}
- Must include: {', '.join(rec.intent.must_include) if rec.intent.must_include else 'None'}

GENERATED PLAN:
Destination: {rec.trip_plan.destination}
Duration: {rec.trip_plan.duration_days} days
Total Cost: ${rec.total_cost_estimate:.2f}

Sample Day (Day 1):
{rec.trip_plan.daily_plans[0].model_dump_json(indent=2) if rec.trip_plan.daily_plans else "No plans"}

Return JSON:
{{
  "intent_match_score": 8.5,
  "intent_match_reasoning": "Plan aligns well with beach vacation request",
  "feasibility_score": 7.0,
  "feasibility_reasoning": "Day 1 has too many activities, might be rushed"
}}
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            response_text = response.content[0].text
            
            # Clean JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            eval_data = json.loads(response_text)
            
            metrics.intent_match_score = float(eval_data.get('intent_match_score', 7.0))
            metrics.feasibility_score = float(eval_data.get('feasibility_score', 7.0))
            
            tracker.end_request(
                operation="llm_evaluation",
                model=self.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                success=True
            )
            
        except Exception as e:
            # Fallback to conservative scores
            metrics.intent_match_score = 6.0
            metrics.feasibility_score = 6.0
            
            tracker.end_request(
                operation="llm_evaluation",
                model=self.model,
                input_tokens=0,
                output_tokens=0,
                success=False,
                error=str(e)
            )
    
    def _calculate_overall_score(self, metrics: EvaluationMetrics) -> float:
        """Calculate weighted overall score"""
        
        if metrics.has_critical_errors:
            return 0.0
        
        # Weighted average
        weights = {
            'intent_match': 0.30,
            'budget': 0.25,
            'feasibility': 0.20,
            'completeness': 0.15,
            'coherence': 0.10
        }
        
        score = (
            metrics.intent_match_score * weights['intent_match'] +
            metrics.budget_adherence_score * weights['budget'] +
            metrics.feasibility_score * weights['feasibility'] +
            metrics.completeness_score * weights['completeness'] +
            metrics.coherence_score * weights['coherence']
        )
        
        return round(score, 1)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 9.0:
            return "A"
        elif score >= 7.5:
            return "B"
        elif score >= 6.0:
            return "C"
        elif score >= 4.0:
            return "D"
        else:
            return "F"
    
    def _calculate_generation_cost(self) -> float:
        """Get total cost from metrics tracker"""
        summary = tracker.get_summary()
        return summary['total_cost_usd']
    
    def batch_evaluate(
        self,
        recommendations: List[TripRecommendation]
    ) -> Dict:
        """
        Evaluate multiple recommendations and return aggregate stats
        Useful for A/B testing, regression testing, etc.
        """
        
        results = []
        for rec in recommendations:
            metrics = self.evaluate(rec)
            results.append(metrics)
        
        # Aggregate statistics
        avg_score = sum(m.overall_score for m in results) / len(results)
        avg_latency = sum(m.latency_ms for m in results) / len(results)
        total_cost = sum(m.cost_usd for m in results)
        
        grade_distribution = {}
        for m in results:
            grade_distribution[m.grade] = grade_distribution.get(m.grade, 0) + 1
        
        return {
            "total_evaluated": len(results),
            "average_score": round(avg_score, 2),
            "average_latency_ms": round(avg_latency, 2),
            "total_cost_usd": round(total_cost, 4),
            "grade_distribution": grade_distribution,
            "all_metrics": [m.model_dump() for m in results]
        }

# Global instance
evaluator = TripEvaluator()
