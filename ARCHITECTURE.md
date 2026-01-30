# TripGenie System Architecture

## High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit Web UI]
        Session[Session State Management]
    end
    
    subgraph "Application Layer"
        Orchestrator[Orchestrator Engine]
        IntentExtractor[Intent Extractor]
        TripPlanner[Trip Planner]
        Evaluator[Quality Evaluator]
    end
    
    subgraph "External Services"
        Claude[Claude API<br/>Anthropic]
        FlightAPI[Flight API<br/>Mock/Amadeus]
    end
    
    subgraph "Data & Monitoring"
        Metrics[Metrics Tracker]
        Config[Configuration]
    end
    
    UI --> Session
    Session --> Orchestrator
    Orchestrator --> IntentExtractor
    Orchestrator --> TripPlanner
    Orchestrator --> FlightAPI
    Orchestrator --> Evaluator
    
    IntentExtractor --> Claude
    TripPlanner --> Claude
    Evaluator --> Claude
    
    Orchestrator --> Metrics
    IntentExtractor --> Metrics
    TripPlanner --> Metrics
    
    Orchestrator --> Config
    
    style Claude fill:#FF9900
    style UI fill:#60A5FA
    style Orchestrator fill:#F97316
    style Metrics fill:#10B981
```

## Detailed Component Architecture

```mermaid
graph LR
    subgraph "User Input Processing"
        A[User Query] --> B[Intent Extraction]
        B --> C[Validation]
        C --> D{Valid?}
        D -->|Yes| E[Structured Intent]
        D -->|No| F[Error Response]
    end
    
    subgraph "Trip Generation"
        E --> G[Trip Planner]
        G --> H[Claude API Call]
        H --> I[Response Parsing]
        I --> J[Pydantic Validation]
        J --> K[Trip Plan Object]
    end
    
    subgraph "Enhancement"
        K --> L{Include Flights?}
        L -->|Yes| M[Flight Search]
        L -->|No| N[Skip Flights]
        M --> O[Flight Results]
        O --> P[Merge Data]
        N --> P
    end
    
    subgraph "Quality Check"
        P --> Q{Evaluate?}
        Q -->|Yes| R[LLM-as-Judge]
        Q -->|No| S[Skip Evaluation]
        R --> T[Quality Metrics]
        T --> U[Final Result]
        S --> U
    end
    
    U --> V[Display to User]
    
    style H fill:#FF9900
    style R fill:#FF9900
    style U fill:#10B981
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Orch as Orchestrator
    participant Intent as Intent Extractor
    participant Planner as Trip Planner
    participant Claude as Claude API
    participant Metrics as Metrics Tracker
    
    User->>UI: Enter trip query
    UI->>Orch: process_query()
    
    Orch->>Metrics: start_request()
    Orch->>Intent: extract(query)
    Intent->>Claude: API call (intent extraction)
    Claude-->>Intent: Structured intent
    Intent-->>Orch: TravelIntent object
    
    Orch->>Planner: plan_trip(intent)
    Planner->>Claude: API call (itinerary generation)
    Claude-->>Planner: Trip itinerary JSON
    Planner-->>Orch: TripPlan object
    
    Orch->>Metrics: end_request()
    Orch-->>UI: TripRecommendation
    UI-->>User: Display itinerary
```

## Deployment Architecture (Current)

```mermaid
graph TB
    subgraph "Docker Container"
        App[Streamlit App<br/>Port 8501]
        Python[Python 3.11 Runtime]
        Deps[Dependencies<br/>requirements.txt]
    end
    
    subgraph "Configuration"
        Env[.env file<br/>API Keys]
        Config[config.py<br/>Settings]
    end
    
    subgraph "External"
        Browser[User Browser]
        Claude[Claude API<br/>api.anthropic.com]
    end
    
    Browser -->|HTTP| App
    App --> Python
    Python --> Deps
    App --> Env
    App --> Config
    App -->|HTTPS| Claude
    
    style App fill:#60A5FA
    style Claude fill:#FF9900
    style Browser fill:#10B981
```

## Future Architecture (Planned)

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx/ALB]
    end
    
    subgraph "Application Tier"
        App1[Streamlit Instance 1]
        App2[Streamlit Instance 2]
        App3[Streamlit Instance N]
    end
    
    subgraph "Cache Layer"
        Redis[Redis Cache]
    end
    
    subgraph "Database Layer"
        PG[(PostgreSQL<br/>Trip History)]
    end
    
    subgraph "Monitoring"
        Prom[Prometheus]
        Graf[Grafana]
        Sentry[Sentry]
    end
    
    subgraph "External APIs"
        Claude[Claude API]
        Amadeus[Amadeus API]
        Booking[Booking.com API]
    end
    
    User[Users] --> LB
    LB --> App1
    LB --> App2
    LB --> App3
    
    App1 --> Redis
    App2 --> Redis
    App3 --> Redis
    
    App1 --> PG
    App2 --> PG
    App3 --> PG
    
    App1 --> Claude
    App1 --> Amadeus
    App1 --> Booking
    
    App1 --> Prom
    App2 --> Prom
    App3 --> Prom
    
    Prom --> Graf
    App1 --> Sentry
    
    style LB fill:#60A5FA
    style Redis fill:#DC2626
    style PG fill:#2563EB
    style Claude fill:#FF9900
```

## Tech Stack Overview

```mermaid
mindmap
  root((TripGenie))
    Frontend
      Streamlit
      HTML/CSS
      JavaScript
    Backend
      Python 3.11
      Pydantic
      LangChain
    AI/ML
      Claude API
      Prompt Engineering
      LLM-as-Judge
    Infrastructure
      Docker
      Docker Compose
    APIs
      Anthropic
      Amadeus Planned
      Booking.com Planned
    Data Validation
      Pydantic Models
      Type Hints
    Monitoring
      Metrics Tracker
      Cost Tracking
```

---

## Component Descriptions

### Frontend Layer
- **Streamlit UI**: Modern web interface with professional design
- **Session State**: Manages user state during session

### Application Layer
- **Orchestrator**: Main engine coordinating all components
- **Intent Extractor**: Parses natural language queries into structured data
- **Trip Planner**: Generates day-by-day itineraries using Claude
- **Evaluator**: Quality assessment using LLM-as-judge pattern

### External Services
- **Claude API**: Core AI engine for trip planning
- **Flight API**: Mock/Amadeus integration for flight search

### Data & Monitoring
- **Metrics Tracker**: Cost and performance monitoring
- **Configuration**: Environment-based settings management

---

## Design Patterns Used

- **Orchestrator Pattern**: Central coordination of all agents
- **Repository Pattern**: Data access abstraction (planned)
- **Factory Pattern**: Model creation and validation
- **Observer Pattern**: Metrics tracking
- **Strategy Pattern**: Flexible API selection (mock vs real)

---

## Scalability Considerations

**Current (MVP)**
- Single instance deployment
- In-memory session state
- Direct API calls

**Future (Production)**
- Horizontal scaling with load balancer
- Redis for distributed caching
- PostgreSQL for persistence
- Message queue for async processing
- CDN for static assets
