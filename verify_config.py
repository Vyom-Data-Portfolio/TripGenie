"""
Configuration Verification Script
Checks if all required settings are properly configured
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("\n" + "="*80)
print("🔍 TripGenie Configuration Verification")
print("="*80)

# Load environment variables
load_dotenv()

# Check .env file exists
env_file = Path(".env")
if env_file.exists():
    print("\n✅ .env file found")
else:
    print("\n❌ .env file NOT found")
    print("   → Copy .env.example to .env and add your API key")
    exit(1)

# Check required variables
print("\n📋 Checking Required Variables:")

# 1. Anthropic API Key
api_key = os.getenv("ANTHROPIC_API_KEY", "")
if api_key and api_key != "your_claude_api_key_here":
    print(f"   ✅ ANTHROPIC_API_KEY: Set ({api_key[:10]}...)")
else:
    print("   ❌ ANTHROPIC_API_KEY: NOT SET or still placeholder")
    print("      → Get key from https://console.anthropic.com/")

# 2. Optional variables
print("\n📋 Checking Optional Variables:")

amadeus_key = os.getenv("AMADEUS_API_KEY", "")
if amadeus_key and amadeus_key != "your_amadeus_key_here":
    print(f"   ✅ AMADEUS_API_KEY: Set")
else:
    print("   ⚠️  AMADEUS_API_KEY: Not set (will use mock flight data)")

amadeus_secret = os.getenv("AMADEUS_API_SECRET", "")
if amadeus_secret and amadeus_secret != "your_amadeus_secret_here":
    print(f"   ✅ AMADEUS_API_SECRET: Set")
else:
    print("   ⚠️  AMADEUS_API_SECRET: Not set (will use mock flight data)")

# 3. Model settings
print("\n📋 Model Configuration:")
print(f"   PRIMARY_MODEL: {os.getenv('PRIMARY_MODEL', 'claude-sonnet-4-20250514')}")
print(f"   TEMPERATURE: {os.getenv('TEMPERATURE', '0.0')}")
print(f"   MAX_TOKENS: {os.getenv('MAX_TOKENS', '4000')}")

# 4. Check Python packages
print("\n📦 Checking Python Packages:")

try:
    import anthropic
    print("   ✅ anthropic package installed")
except ImportError:
    print("   ❌ anthropic package NOT installed")
    print("      → Run: pip install -r requirements.txt")

try:
    import streamlit
    print("   ✅ streamlit package installed")
except ImportError:
    print("   ❌ streamlit package NOT installed")
    print("      → Run: pip install -r requirements.txt")

try:
    from pydantic import BaseModel
    print("   ✅ pydantic package installed")
except ImportError:
    print("   ❌ pydantic package NOT installed")
    print("      → Run: pip install -r requirements.txt")

# 5. Check project structure
print("\n📁 Checking Project Structure:")

required_dirs = ["src", "src/agents", "src/api", "src/core", "src/evaluation", "src/data"]
for dir_name in required_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"   ✅ {dir_name}/ exists")
    else:
        print(f"   ❌ {dir_name}/ NOT found")

required_files = ["app.py", "main.py", "requirements.txt", "README.md"]
for file_name in required_files:
    file_path = Path(file_name)
    if file_path.exists():
        print(f"   ✅ {file_name} exists")
    else:
        print(f"   ❌ {file_name} NOT found")

# 6. Test API connection (if key is set)
if api_key and api_key != "your_claude_api_key_here":
    print("\n🔌 Testing API Connection:")
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        # Try a simple API call
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print("   ✅ API connection successful!")
        print(f"   Response: {response.content[0].text}")
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if api_key and api_key != "your_claude_api_key_here":
    print("\n✅ Configuration looks good! You're ready to run TripGenie.")
    print("\nNext steps:")
    print("  1. Run: python demo_test.py")
    print("  2. Run: python main.py --query \"5-day trip to Bangkok\"")
    print("  3. Run: streamlit run app.py")
else:
    print("\n⚠️  Configuration incomplete!")
    print("\nRequired action:")
    print("  1. Edit .env file")
    print("  2. Add your ANTHROPIC_API_KEY")
    print("  3. Run this script again")

print("="*80 + "\n")
