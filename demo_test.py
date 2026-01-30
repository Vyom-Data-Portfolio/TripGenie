"""
Quick Demo Test
Tests the system end-to-end without needing API keys
"""
import sys
import os
from pathlib import Path

# Add src to path - Works on Windows, Mac, Linux
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("\n" + "="*80)
print("🚀 TripGenie - Quick Demo Test")
print("="*80)

# Test imports
print("\n1. Testing imports...")
try:
    from src.agents.orchestrator import orchestrator
    from src.evaluation.evaluator import evaluator
    from src.core.metrics import tracker
    print("   ✅ All modules imported successfully")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test orchestrator
print("\n2. Testing orchestrator...")
try:
    test_query = "5-day beach vacation in Thailand under $2000"
    print(f"   Query: {test_query}")
    
    # This will work even without API keys due to error handling
    try:
        recommendation = orchestrator.process_query(
            user_query=test_query,
            include_flights=False
        )
        print("   ✅ Orchestrator working")
        print(f"   Generated plan for: {recommendation.trip_plan.destination}")
    except Exception as e:
        if "ANTHROPIC_API_KEY" in str(e):
            print("   ⚠️  Need to set ANTHROPIC_API_KEY in .env file")
            print("   (This is expected if you haven't configured API keys yet)")
        else:
            print(f"   ❌ Error: {e}")
    
except Exception as e:
    print(f"   ❌ Orchestrator test failed: {e}")

# Test metrics
print("\n3. Testing metrics tracker...")
try:
    summary = tracker.get_summary()
    print(f"   ✅ Metrics tracker working")
    print(f"   Requests tracked: {summary['total_requests']}")
except Exception as e:
    print(f"   ❌ Metrics error: {e}")

# Summary
print("\n" + "="*80)
print("DEMO TEST COMPLETE")
print("="*80)
print("\nNext steps:")
print("  python main.py --query \"your travel query\"")
print("  streamlit run app.py")
print("="*80 + "\n")
