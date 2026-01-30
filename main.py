"""
TripGenie CLI
Command-line interface for testing and batch processing
"""
import argparse
import json
import os
import sys
from pathlib import Path

# Add src to path - Works on Windows, Mac, Linux
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.agents.orchestrator import orchestrator
from src.evaluation.evaluator import evaluator
from src.core.metrics import tracker
from src.data.test_queries import TEST_QUERIES, QUICK_TESTS

def run_single_query(query: str, include_flights: bool = True):
    """Run a single travel query"""
    print("\n" + "="*80)
    print(f"QUERY: {query}")
    print("="*80)
    
    # Process
    recommendation = orchestrator.process_query(
        user_query=query,
        include_flights=include_flights
    )
    
    # Evaluate
    evaluation = evaluator.evaluate(recommendation)
    
    # Display summary
    print("\n" + "-"*80)
    print("SUMMARY")
    print("-"*80)
    print(f"Destination: {recommendation.trip_plan.destination}")
    print(f"Duration: {recommendation.trip_plan.duration_days} days")
    print(f"Total Cost: ${recommendation.total_cost_estimate:.2f}")
    print(f"Quality Grade: {evaluation.grade} ({evaluation.overall_score:.1f}/10)")
    print(f"Generation Time: {recommendation.generation_time_ms:.0f}ms")
    print(f"Generation Cost: ${evaluation.cost_usd:.4f}")
    
    return recommendation, evaluation

def run_batch_evaluation():
    """Run evaluation on all test queries"""
    print("\n" + "="*80)
    print("BATCH EVALUATION - Running all test queries")
    print("="*80)
    
    recommendations = []
    
    for i, test in enumerate(QUICK_TESTS, 1):
        print(f"\n[{i}/{len(QUICK_TESTS)}] Processing: {test}")
        
        try:
            rec = orchestrator.process_query(
                user_query=test,
                include_flights=False  # Skip flights for speed
            )
            recommendations.append(rec)
        except Exception as e:
            print(f"   ERROR: {e}")
    
    # Batch evaluate
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)
    
    results = evaluator.batch_evaluate(recommendations)
    
    print(f"\nTotal Evaluated: {results['total_evaluated']}")
    print(f"Average Score: {results['average_score']}/10")
    print(f"Average Latency: {results['average_latency_ms']:.0f}ms")
    print(f"Total Cost: ${results['total_cost_usd']:.4f}")
    print(f"\nGrade Distribution:")
    for grade, count in sorted(results['grade_distribution'].items()):
        print(f"  {grade}: {count}")
    
    # Export results
    output_file = Path("evaluation_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Results exported to {output_file}")
    
    return results

def export_metrics():
    """Export system metrics"""
    output_file = Path("system_metrics.json")
    tracker.export_json(str(output_file))
    print(f"✅ Metrics exported to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="TripGenie - AI Travel Planner CLI")
    parser.add_argument(
        "--query",
        type=str,
        help="Single travel query to process"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run batch evaluation on test queries"
    )
    parser.add_argument(
        "--no-flights",
        action="store_true",
        help="Skip flight search"
    )
    parser.add_argument(
        "--export-metrics",
        action="store_true",
        help="Export system metrics to JSON"
    )
    
    args = parser.parse_args()
    
    # Run appropriate mode
    if args.query:
        run_single_query(args.query, include_flights=not args.no_flights)
    elif args.batch:
        run_batch_evaluation()
    elif args.export_metrics:
        export_metrics()
    else:
        # Interactive mode
        print("\n✈️  TripGenie - AI Travel Planner")
        print("="*80)
        print("\nExamples:")
        print("  python main.py --query \"5-day beach trip to Thailand under $2000\"")
        print("  python main.py --batch")
        print("  python main.py --export-metrics")
        print("\nOr run: streamlit run app.py")
        print("="*80)

if __name__ == "__main__":
    main()
