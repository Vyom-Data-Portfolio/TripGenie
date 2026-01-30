#!/bin/bash
# Quick Setup Script for TripGenie

echo "🚀 TripGenie Setup"
echo "=================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.10"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Python 3.10+ required. You have $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup .env
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - AMADEUS_API_KEY (optional)"
    echo "   - AMADEUS_API_SECRET (optional)"
    echo ""
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: streamlit run app.py"
echo ""
echo "Or try CLI:"
echo "  python main.py --query \"5-day trip to Bangkok\""
echo ""
