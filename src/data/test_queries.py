"""
Test Queries for Evaluation
Diverse set of travel requests to test system capabilities
"""

TEST_QUERIES = [
    # Simple queries
    {
        "query": "I want a 5-day beach vacation in Thailand under $2000",
        "expected_destination": "Thailand",
        "expected_duration": 5,
        "difficulty": "easy"
    },
    
    # Medium complexity
    {
        "query": "Plan a romantic week in Paris for two people. We love art museums and good food. Budget is around $5000. Preferably in spring.",
        "expected_destination": "Paris",
        "expected_duration": 7,
        "difficulty": "medium"
    },
    
    # High complexity
    {
        "query": "Family trip to Japan for 4 people (2 adults, 2 kids aged 8 and 12). 10 days. Mix of Tokyo and Kyoto. Kids love anime and technology. We want cultural experiences too. Budget $8000. Must include Mt. Fuji.",
        "expected_destination": "Japan",
        "expected_duration": 10,
        "difficulty": "hard"
    },
    
    # Budget-conscious
    {
        "query": "Backpacking Southeast Asia for 3 weeks. I'm solo, love nature and hiking. Keep it cheap - maybe $1500 total including flights from NYC.",
        "expected_destination": "Southeast Asia",
        "expected_duration": 21,
        "difficulty": "medium"
    },
    
    # Luxury
    {
        "query": "Luxury honeymoon in Maldives. 7 nights. Best resorts. Water villas. Spa. Scuba diving. Money is not an issue.",
        "expected_destination": "Maldives",
        "expected_duration": 7,
        "difficulty": "easy"
    },
    
    # Adventure
    {
        "query": "I want an adrenaline-packed trip to New Zealand. 2 weeks. Bungee jumping, skydiving, white water rafting. Also want to see Lord of the Rings locations. Budget $4000.",
        "expected_destination": "New Zealand",
        "expected_duration": 14,
        "difficulty": "medium"
    },
    
    # Cultural/Educational
    {
        "query": "Educational trip to Egypt for me and my teenage son. 10 days. Pyramids, museums, Nile cruise. He's studying ancient history. Budget $3500 for both of us.",
        "expected_destination": "Egypt",
        "expected_duration": 10,
        "difficulty": "medium"
    },
    
    # City hopping
    {
        "query": "European city hopping - Barcelona, Rome, Amsterdam. 12 days total. Love architecture, nightlife, and local food. Solo traveler, $3000 budget.",
        "expected_destination": "Europe",
        "expected_duration": 12,
        "difficulty": "hard"
    },
    
    # Wellness retreat
    {
        "query": "I need a wellness retreat in Bali. Yoga, meditation, healthy food. 1 week. Looking for peace and relaxation. Budget around $2500.",
        "expected_destination": "Bali",
        "expected_duration": 7,
        "difficulty": "easy"
    },
    
    # Winter sports
    {
        "query": "Ski trip to Swiss Alps. Me and 3 friends. 5 days of skiing. Good nightlife too. Around $2000 per person.",
        "expected_destination": "Switzerland",
        "expected_duration": 5,
        "difficulty": "medium"
    }
]

# Quick test queries for development
QUICK_TESTS = [
    "Weekend trip to Bangkok, budget $800",
    "5 days in Bali with my girlfriend, we love beaches and temples",
    "Business trip to Singapore, 3 days, need good hotels near CBD"
]
