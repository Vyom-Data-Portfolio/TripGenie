"""
Local Configuration Overrides
Customize these for your specific setup
"""

# ===================================
# USER-SPECIFIC SETTINGS
# ===================================

# Your default origin city for flights
DEFAULT_ORIGIN_CITY = "Delhi"  # Change to your city
DEFAULT_AIRPORT_CODE = "DEL"   # Your airport code

# Your timezone (for date handling)
TIMEZONE = "Asia/Kolkata"      # Change to your timezone

# Your currency preference (display only, doesn't affect calculations)
CURRENCY_SYMBOL = "₹"          # $ or € or £ or ₹

# ===================================
# API SETTINGS
# ===================================

# Use real APIs or mocks?
USE_REAL_AMADEUS_API = False   # Set to True when you have API keys

# Enable web search for destinations (future feature)
ENABLE_WEB_SEARCH = False      # Not implemented yet

# ===================================
# PERFORMANCE SETTINGS
# ===================================

# Maximum time to wait for LLM response (seconds)
LLM_TIMEOUT = 30

# Maximum time to wait for flight API (seconds)
FLIGHT_API_TIMEOUT = 15

# Enable caching to save costs
ENABLE_CACHING = True

# ===================================
# DEVELOPMENT SETTINGS
# ===================================

# Show detailed logs in console
VERBOSE_LOGGING = True

# Save all generated trips to files
AUTO_SAVE_TRIPS = False

# Directory to save trips (if AUTO_SAVE_TRIPS = True)
TRIPS_SAVE_DIR = "generated_trips"

# ===================================
# QUALITY SETTINGS
# ===================================

# Minimum confidence score to accept intent extraction
MIN_CONFIDENCE_THRESHOLD = 0.3

# Minimum quality grade to pass evaluation
MIN_QUALITY_GRADE = "C"  # A, B, C, D, F

# ===================================
# COST CONTROLS
# ===================================

# Maximum cost per request (USD) - stops if exceeded
MAX_COST_PER_REQUEST = 0.10  # 10 cents

# Alert if cost exceeds this threshold
COST_WARNING_THRESHOLD = 0.05  # 5 cents

# ===================================
# UI SETTINGS
# ===================================

# Streamlit theme
STREAMLIT_THEME = "light"  # "light" or "dark"

# Show cost metrics in UI
SHOW_COST_METRICS = True

# Show detailed evaluation in UI
SHOW_DETAILED_EVAL = True
