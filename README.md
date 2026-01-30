# 🎯 TripGenie - AI Travel Planner

AI-powered personal travel assistant built with Claude API, Streamlit, and modern ML practices.

## ✨ Features

- 🤖 **Intelligent Trip Planning** - Claude AI generates personalized itineraries
- ✈️ **Flight Search** - Mock and real Amadeus API integration
- 📊 **Quality Evaluation** - Built-in metrics and LLM-as-judge evaluation
- 💰 **Cost Tracking** - Production-grade monitoring
- 🎨 **Beautiful UI** - Modern Streamlit interface

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd tripgenie
```

2. **Set up environment**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Run with Docker Compose**
```bash
docker-compose up
```

4. **Open browser**
```
http://localhost:8501
```

### Option 2: Local Python

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up environment**
```bash
cp .env.example .env
# Add your API key to .env
```

3. **Run the app**
```bash
streamlit run app.py
```

## 🐳 Docker Commands

```bash
# Build image
docker build -t tripgenie .

# Run container
docker run -p 8501:8501 --env-file .env tripgenie

# With docker-compose
docker-compose up -d        # Start in background
docker-compose logs -f      # View logs
docker-compose down         # Stop
```

## 📁 Project Structure

```
tripgenie/
├── app.py                  # Main Streamlit app
├── src/
│   ├── agents/            # AI agents (orchestrator, planner, etc.)
│   ├── api/               # External APIs (flights, etc.)
│   ├── core/              # Core utilities (config, metrics)
│   ├── evaluation/        # Quality evaluation system
│   └── data/              # Test queries and data
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── requirements.txt       # Python dependencies
└── .env.example          # Environment template
```

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | Your Claude API key |
| `PRIMARY_MODEL` | ❌ | Claude model (default: sonnet-4) |
| `AMADEUS_API_KEY` | ❌ | For real flight data |

## 🎯 Usage Examples

**Simple query:**
```
"Weekend trip to Bangkok, budget $800"
```

**Complex query:**
```
"5-day romantic trip to Bali for 2 people. We love beaches, 
temples, and local food. Budget $2000."
```

## 📊 Tech Stack

- **Python 3.11** - Core language
- **Streamlit** - Web framework
- **Claude API** - AI intelligence
- **Docker** - Containerization
- **Pydantic** - Data validation

## 🚢 Deployment

### Streamlit Cloud (Free)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your repo
4. Add `ANTHROPIC_API_KEY` in Streamlit secrets

### AWS/GCP/Azure
Use the provided Docker image:
```bash
docker build -t tripgenie .
docker push your-registry/tripgenie
```

## 🤝 Contributing

Contributions welcome! This is a portfolio project showcasing:
- Production ML system design
- API integration patterns
- Cost tracking & monitoring
- Quality evaluation frameworks

## 📝 License

MIT License - feel free to use for learning and portfolios

## 👨‍💻 Author

Built as a portfolio project demonstrating:
- Full-stack development
- AI/ML integration
- DevOps practices (Docker)
- Production-ready code

---

**⭐ Star this repo if you find it helpful!**
