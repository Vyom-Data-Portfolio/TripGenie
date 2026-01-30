"""
TripGenie Streamlit UI - Professional Redesign
Modern, clean interface following industry best practices
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.agents.orchestrator import orchestrator
from src.evaluation.evaluator import evaluator
from src.core.metrics import tracker
from src.data.test_queries import QUICK_TESTS
import json

# Page config
st.set_page_config(
    page_title="TripGenie - AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS - Following modern best practices
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* 8px Grid System - Professional Spacing */
    .main {
        background: #F9FAFB;
        padding: 0;
    }
    
    .block-container {
        max-width: 1200px;
        padding: 48px 24px;
        margin: 0 auto;
    }
    
    /* Professional Color Palette */
    :root {
        --primary-blue: #2563EB;
        --accent-orange: #F97316;
        --text-dark: #1F2937;
        --text-light: #6B7280;
        --bg-white: #FFFFFF;
        --bg-light: #F9FAFB;
        --border-light: #E5E7EB;
        --sidebar-bg: #F1F5F9;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        color: var(--primary-blue);
        margin-bottom: 16px;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.25rem;
        color: var(--text-light);
        margin-bottom: 48px;
        font-weight: 500;
    }
    
    /* Sidebar - Professional Design */
    [data-testid="stSidebar"] {
        background: #E2E8F0;
        padding: 24px 16px;
    }
    
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-dark);
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 16px;
    }
    
    [data-testid="stSidebar"] label {
        color: var(--text-dark);
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    /* Input Fields - Clean Design */
    .stTextInput input,
    .stTextArea textarea {
        border: 2px solid var(--border-light);
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 1rem;
        color: var(--text-dark);
        background: white;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--primary-blue);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    .stTextArea textarea {
        min-height: 120px;
        line-height: 1.6;
    }
    
    /* Buttons - Modern CTA Design */
    .stButton > button {
        background: #FB923C;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #F97316;
        box-shadow: 0 4px 6px rgba(249, 115, 22, 0.3);
        transform: translateY(-1px);
    }
    
    /* Primary Button Variant */
    .stButton > button[kind="primary"] {
        background: #60A5FA;
        font-size: 1.125rem;
        padding: 14px 32px;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #3B82F6;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
    }
    
    /* Cards - Professional Design */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-blue);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-light);
        font-weight: 500;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Section Headers */
    h1, h2, h3 {
        color: var(--text-dark);
        font-weight: 700;
    }
    
    h2 {
        font-size: 1.875rem;
        margin-top: 48px;
        margin-bottom: 24px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--border-light);
    }
    
    h3 {
        font-size: 1.25rem;
        margin-bottom: 16px;
    }
    
    /* Text Styling */
    p, span, div, label {
        color: var(--text-dark);
        line-height: 1.6;
    }
    
    /* Theme Cards - Multi-select */
    .theme-card {
        display: inline-block;
        padding: 12px 20px;
        margin: 8px 8px 8px 0;
        border: 2px solid var(--border-light);
        border-radius: 8px;
        background: white;
        color: var(--text-dark);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
    }
    
    .theme-card:hover {
        border-color: var(--primary-blue);
        background: #EFF6FF;
    }
    
    .theme-card.selected {
        border-color: var(--primary-blue);
        background: var(--primary-blue);
        color: white;
    }
    
    /* Date inputs */
    .stDateInput input,
    .stSelectbox select {
        border: 2px solid var(--border-light) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        color: #000000 !important;
        background: #FAFAFA !important;
    }
    
    /* Selectbox - Force light background */
    .stSelectbox > div > div {
        background-color: #FAFAFA !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: #FAFAFA !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #FAFAFA !important;
        color: #000000 !important;
    }
    
    /* Dropdown menu */
    [data-baseweb="popover"] {
        background: white !important;
    }
    
    /* Date picker calendar popup */
    [data-baseweb="calendar"] {
        background: white !important;
    }
    
    [data-baseweb="calendar"] * {
        background: white !important;
        color: #000000 !important;
    }
    
    [data-baseweb="calendar"] header {
        background: white !important;
    }
    
    /* Calendar days */
    [aria-label*="day"] {
        background: white !important;
        color: #000000 !important;
    }
    
    /* Selected date */
    [aria-selected="true"] {
        background: var(--primary-blue) !important;
        color: white !important;
    }
    
    [role="listbox"] {
        background: white !important;
    }
    
    [role="option"] {
        background: white !important;
        color: #000000 !important;
    }
    
    [role="option"]:hover {
        background: #F3F4F6 !important;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        padding: 8px 0;
    }
    
    .stCheckbox label {
        font-weight: 500;
        font-size: 1rem;
    }
    
    /* Money saver badge */
    .money-saver-badge {
        display: inline-block;
        background: #ECFDF5;
        color: #065F46;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 8px;
    }
    
    /* Fix cursor visibility in textarea */
    .stTextArea textarea {
        caret-color: var(--text-dark) !important;
    }
    
    /* Expanders - Clean Card Style */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 16px;
        font-weight: 600;
        color: var(--text-dark);
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--primary-blue);
        background: #F0F9FF;
    }
    
    .streamlit-expanderContent {
        border: 1px solid var(--border-light);
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 24px;
        background: white;
    }
    
    /* Dividers */
    hr {
        margin: 48px 0;
        border: none;
        border-top: 1px solid var(--border-light);
    }
    
    /* Success Messages */
    .stSuccess {
        background: #ECFDF5;
        border: 1px solid #10B981;
        border-radius: 8px;
        padding: 16px;
        color: #065F46;
    }
    
    /* Warning Messages */
    .stWarning {
        background: #FEF3C7;
        border: 1px solid #F59E0B;
        border-radius: 8px;
        padding: 16px;
        color: #92400E;
    }
    
    /* Info Boxes */
    .stInfo {
        background: #EFF6FF;
        border: 1px solid var(--primary-blue);
        border-radius: 8px;
        padding: 16px;
        color: #1E40AF;
    }
    
    /* Remove default Streamlit padding */
    .main .block-container {
        padding-top: 48px;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .block-container {
            padding: 24px 16px;
        }
        
        h2 {
            font-size: 1.5rem;
            margin-top: 32px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">✈️ TripGenie</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Your AI-Powered Personal Travel Assistant</p>',
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 📍 Your Location")
    user_city = st.text_input("City", "Delhi", key="user_city")
    user_country = st.text_input("Country", "India", key="user_country")
    
    st.markdown("---")
    
    st.markdown("### 🎯 Destination")
    dest_preference = st.radio(
        "Choose destination",
        ["Let me specify", "Surprise me! 🎲"],
        key="dest_pref"
    )
    
    if dest_preference == "Let me specify":
        preferred_dest = st.text_input("Where to?", "", key="pref_dest", 
                                      placeholder="e.g., Bali, Paris, Tokyo...")
    else:
        preferred_dest = None
    
    st.markdown("---")
    
    st.markdown("### 🛫 Options")
    include_flights = st.checkbox("Include Flights", value=True)
    use_real_apis = st.checkbox("Real APIs", value=False, 
                                help="Use Amadeus API (requires keys)")
    
    st.markdown("---")
    
    st.markdown("### 💡 Quick Examples")
    examples = [
        "🏖️ Beach weekend ($800)",
        "🗼 5 days in Paris",
        "🏔️ Adventure trip"
    ]
    
    for i, example in enumerate(examples):
        if st.button(example, key=f"ex_{i}"):
            st.session_state['user_query'] = example

# Initialize session state
if 'recommendation' not in st.session_state:
    st.session_state['recommendation'] = None
if 'evaluation' not in st.session_state:
    st.session_state['evaluation'] = None
if 'user_query' not in st.session_state:
    st.session_state['user_query'] = ""
if 'selected_themes' not in st.session_state:
    st.session_state['selected_themes'] = []
if 'flexible_dates' not in st.session_state:
    st.session_state['flexible_dates'] = False
if 'smart_money_saver' not in st.session_state:
    st.session_state['smart_money_saver'] = False

# Main interface
st.markdown("## 🗣️ Describe Your Dream Trip")

user_query = st.text_area(
    "",
    value=st.session_state['user_query'],
    height=120,
    placeholder="✨ Example: I want a 5-day romantic getaway to Santorini with my partner. We love sunsets, good wine, and exploring local villages. Budget is around $3000.",
    key="query_input",
    label_visibility="collapsed"
)

# Dates Section
st.markdown("### 📅 Travel Dates")
col_date1, col_date2, col_flexible = st.columns([1, 1, 1])

from datetime import datetime, timedelta
current_date = datetime.now()
default_start = current_date + timedelta(days=7)  # Default to 1 week from now
default_end = default_start + timedelta(days=7)  # Default 1 week trip

with col_date1:
    if st.session_state['flexible_dates']:
        current_month_index = current_date.month - 1  # 0-indexed
        start_month = st.selectbox("Start Month", 
            ["January", "February", "March", "April", "May", "June", 
             "July", "August", "September", "October", "November", "December"],
            index=current_month_index,
            key="start_month")
        start_year = st.selectbox("Start Year", 
            [2026, 2027, 2028],
            index=0,
            key="start_year")
        start_date = None
    else:
        start_date = st.date_input("Start Date", value=default_start, key="start_date")

with col_date2:
    if st.session_state['flexible_dates']:
        end_month = st.selectbox("End Month", 
            ["January", "February", "March", "April", "May", "June", 
             "July", "August", "September", "October", "November", "December"],
            index=current_month_index,
            key="end_month")
        end_year = st.selectbox("End Year", 
            [2026, 2027, 2028],
            index=0,
            key="end_year")
        end_date = None
    else:
        end_date = st.date_input("End Date", value=default_end, key="end_date")

with col_flexible:
    flexible = st.checkbox("Flexible with dates", 
                          value=st.session_state['flexible_dates'],
                          key="flexible_checkbox")
    if flexible != st.session_state['flexible_dates']:
        st.session_state['flexible_dates'] = flexible
        st.rerun()

# Themes Section
st.markdown("### 🎨 Trip Themes")
st.markdown("Select all that apply:")

themes = ["Adventure", "Relaxation", "Romantic", "Workation", "Health Retreat"]

# Create theme buttons using columns
theme_cols = st.columns(5)
for idx, theme in enumerate(themes):
    with theme_cols[idx]:
        if st.button(
            theme,
            key=f"theme_{theme}",
            type="primary" if theme in st.session_state['selected_themes'] else "secondary",
            use_container_width=True
        ):
            if theme in st.session_state['selected_themes']:
                st.session_state['selected_themes'].remove(theme)
            else:
                st.session_state['selected_themes'].append(theme)
            st.rerun()

# Display selected themes
if st.session_state['selected_themes']:
    st.markdown(f"**Selected:** {', '.join(st.session_state['selected_themes'])}")

# Smart Money Saver Section
st.markdown("### 💰 Budget Options")
smart_saver = st.checkbox(
    "Smart Money Saver - Prioritize finding best deals",
    value=st.session_state['smart_money_saver'],
    key="smart_saver_checkbox"
)

if smart_saver != st.session_state['smart_money_saver']:
    st.session_state['smart_money_saver'] = smart_saver

if st.session_state['smart_money_saver']:
    st.markdown(
        '<div class="money-saver-badge">💡 Finding best deals on flights, hotels, and activities...</div>',
        unsafe_allow_html=True
    )

# Action buttons
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    plan_button = st.button("🎯 Plan My Trip", type="primary", use_container_width=True)

with col2:
    if st.session_state['recommendation']:
        evaluate_button = st.button("📊 Evaluate", use_container_width=True)
    else:
        evaluate_button = False

with col3:
    if st.session_state['recommendation']:
        if st.button("💾 Export", use_container_width=True):
            rec = st.session_state['recommendation']
            json_str = json.dumps(rec.model_dump(), indent=2, default=str)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_str,
                file_name="trip_plan.json",
                mime="application/json"
            )

with col4:
    if st.session_state['recommendation']:
        if st.button("🔄 New Trip", use_container_width=True):
            st.session_state['recommendation'] = None
            st.session_state['evaluation'] = None
            st.rerun()

# Process query
if plan_button and user_query:
    with st.spinner("🧠 Creating your perfect itinerary..."):
        try:
            orchestrator.use_real_apis = use_real_apis
            
            # Build enhanced context
            context = {
                'origin': user_city,
                'origin_country': user_country,
                'user_location': f"{user_city}, {user_country}",
                'preferred_destination': preferred_dest if dest_preference == "Let me specify" else None,
                'themes': st.session_state['selected_themes'],
                'smart_money_saver': st.session_state['smart_money_saver'],
                'flexible_dates': st.session_state['flexible_dates']
            }
            
            # Add date information
            if st.session_state['flexible_dates']:
                context['start_month'] = st.session_state.get('start_month', 'January')
                context['start_year'] = st.session_state.get('start_year', 2026)
                context['end_month'] = st.session_state.get('end_month', 'January')
                context['end_year'] = st.session_state.get('end_year', 2026)
            else:
                if 'start_date' in st.session_state:
                    context['start_date'] = str(st.session_state['start_date'])
                if 'end_date' in st.session_state:
                    context['end_date'] = str(st.session_state['end_date'])
            
            # Enhance query with themes and money saver
            enhanced_query = user_query
            if st.session_state['selected_themes']:
                enhanced_query += f"\n\nTrip themes: {', '.join(st.session_state['selected_themes'])}"
            if st.session_state['smart_money_saver']:
                enhanced_query += "\n\nIMPORTANT: Prioritize budget-friendly options and best deals for flights, accommodation, and activities."
            
            recommendation = orchestrator.process_query(
                user_query=enhanced_query,
                include_flights=include_flights,
                context=context
            )
            st.session_state['recommendation'] = recommendation
            st.session_state['evaluation'] = None
            
            st.success("✅ Your personalized trip plan is ready!")
            
        except Exception as e:
            st.error(f"❌ Something went wrong: {str(e)}")

# Evaluate if requested
if evaluate_button and st.session_state['recommendation']:
    with st.spinner("📊 Evaluating trip quality..."):
        try:
            evaluation = evaluator.evaluate(st.session_state['recommendation'])
            st.session_state['evaluation'] = evaluation
            
        except Exception as e:
            st.error(f"❌ Evaluation error: {str(e)}")

# Display results
if st.session_state['recommendation']:
    rec = st.session_state['recommendation']
    
    st.markdown("---")
    
    # Overview metrics
    st.markdown("## 📋 Trip Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌍 Destination",
            value=rec.trip_plan.destination
        )
    with col2:
        st.metric(
            label="📅 Duration",
            value=f"{rec.trip_plan.duration_days} days"
        )
    with col3:
        st.metric(
            label="💰 Total Cost",
            value=f"${rec.total_cost_estimate:.0f}"
        )
    with col4:
        st.metric(
            label="⚡ Generated",
            value=f"{rec.generation_time_ms:.0f}ms"
        )
    
    # Evaluation scores
    if st.session_state['evaluation']:
        st.markdown("---")
        st.markdown("## ⭐ Quality Score")
        
        eval_data = st.session_state['evaluation']
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Overall Grade", eval_data.grade)
        with col2:
            st.metric("Intent Match", f"{eval_data.intent_match_score:.1f}/10")
        with col3:
            st.metric("Budget", f"{eval_data.budget_adherence_score:.1f}/10")
        with col4:
            st.metric("Feasibility", f"{eval_data.feasibility_score:.1f}/10")
        with col5:
            st.metric("Complete", f"{eval_data.completeness_score:.1f}/10")
        
        if eval_data.error_messages:
            st.warning("⚠️ **Issues Found:**")
            for msg in eval_data.error_messages:
                st.write(f"• {msg}")
    
    # Daily itinerary
    st.markdown("---")
    st.markdown("## 📅 Day-by-Day Itinerary")
    
    for day in rec.trip_plan.daily_plans:
        with st.expander(f"**Day {day.day}** • {day.date} • ${day.estimated_cost_usd}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🌅 Morning")
                st.write(day.morning)
            
            with col2:
                st.markdown("### ☀️ Afternoon")
                st.write(day.afternoon)
            
            with col3:
                st.markdown("### 🌙 Evening")
                st.write(day.evening)
            
            if day.notes:
                st.info(f"💡 {day.notes}")
    
    # Highlights and Tips
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## ✨ Trip Highlights")
        for highlight in rec.trip_plan.highlights:
            st.markdown(f"• {highlight}")
    
    with col2:
        st.markdown("## 💡 Practical Tips")
        for tip in rec.trip_plan.practical_tips:
            st.markdown(f"• {tip}")
    
    # Flights
    if rec.outbound_flights and rec.outbound_flights.offers:
        st.markdown("---")
        st.markdown("## ✈️ Flight Options")
        
        for i, offer in enumerate(rec.outbound_flights.offers[:3], 1):
            with st.expander(f"**Option {i}** • ${offer.price_usd} • {offer.airline}", expanded=i==1):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Departure", offer.departure_time)
                with col2:
                    st.metric("Duration", f"{offer.duration_hours:.1f}h")
                with col3:
                    st.metric("Stops", offer.stops)
                with col4:
                    st.metric("Price", f"${offer.price_usd}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 32px 0;">
    <p style="font-size: 0.875rem; margin-bottom: 8px;">Built with Claude AI • Streamlit • Docker</p>
    <p style="font-size: 0.75rem;">🚀 Production-Ready ML System • 📊 Quality Evaluation • 💰 Cost Tracking</p>
</div>
""", unsafe_allow_html=True)