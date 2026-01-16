# 🎯 Board Panel - AI-Powered Startup Advisory System

An intelligent multi-agent system powered by CrewAI that provides comprehensive startup analysis through 5 specialized AI advisors working in parallel.

## 🌟 Features

- **5 Specialized AI Agents** working independently:
  - 📊 **Marketing Advisor**: Growth strategies, user acquisition, and marketing optimization
  - 💻 **Tech Lead**: Technical architecture, scalability, and engineering best practices
  - 👥 **Org/HR Strategist**: Team building, hiring strategies, and organizational design
  - 🎯 **Competitive Analyst**: Market positioning, competitive intelligence, and differentiation
  - 💰 **Finance Advisor**: Burn rate analysis, financial planning, and runway optimization

- **Parallel Processing**: All agents analyze independently and simultaneously
- **Comprehensive Analysis**: Each agent provides:
  - ✅ Strengths identification
  - ⚠️ Weakness detection
  - 💡 Actionable suggestions
  - 📅 Detailed 30-day roadmap

- **FastAPI Integration**: RESTful API with async/sync endpoints
- **Custom Tools**: Specialized tools for market research, financial benchmarking, tech stack analysis, and more

## 📋 Prerequisites

- Python 3.10 - 3.13
- pip or uv (package manager)

## 🚀 Installation

### Option 1: Using pip

```bash
# Clone or navigate to the project
cd board_panel

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Option 2: Using uv (recommended)

```bash
# Install uv if you haven't
pip install uv

# Install dependencies
uv pip install -r requirements.txt

# Or use uv sync
uv sync
```

## 🔑 Configuration

Create a `.env` file in the project root:

```env
# OpenAI API Key (required for CrewAI)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Model configuration
OPENAI_MODEL_NAME=gpt-4-turbo-preview

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## 💻 Usage

### Running the FastAPI Server

```bash
# Start the API server
uvicorn board_panel.api:app --reload --host 0.0.0.0 --port 8000

# Or use the shortcut
python -m board_panel.api
```

The API will be available at: `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

### Running the Crew Directly (CLI)

```bash
# Run with example data
python -m board_panel.main

# Or use the installed command
board_panel
```

## 📡 API Endpoints

### 1. Submit Analysis (Async)

**POST** `/api/v1/analyze`

Submit startup data for asynchronous analysis. Returns an `analysis_id` to track progress.

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

Response:
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Analysis submitted successfully",
  "submitted_at": "2024-01-15T10:30:00"
}
```

### 2. Check Analysis Status

**GET** `/api/v1/status/{analysis_id}`

```bash
curl "http://localhost:8000/api/v1/status/550e8400-e29b-41d4-a716-446655440000"
```

Response:
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "marketing_analysis": { ... },
    "tech_analysis": { ... },
    "org_hr_analysis": { ... },
    "competitive_analysis": { ... },
    "finance_analysis": { ... }
  },
  "submitted_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:35:00"
}
```

### 3. Submit Analysis (Sync)

**POST** `/api/v1/analyze/sync`

⚠️ **Warning**: This endpoint blocks until analysis is complete (2-5 minutes).

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/sync" \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

### 4. List All Analyses

**GET** `/api/v1/analyses?status=completed&limit=10`

```bash
curl "http://localhost:8000/api/v1/analyses?status=completed&limit=10"
```

### 5. Health Check

**GET** `/health`

```bash
curl "http://localhost:8000/health"
```

## 📝 Request Format

Here's the complete input structure:

```json
{
  "startup_data": {
    "product_technology": {
      "product_type": "SaaS",
      "current_features": [
        "User Authentication",
        "Dashboard Analytics",
        "API Integration"
      ],
      "tech_stack": ["React", "Node.js", "PostgreSQL", "AWS"],
      "data_strategy": "User Data",
      "ai_usage": "Planned",
      "tech_challenges": "Scaling database queries, implementing real-time features"
    },
    "marketing_growth": {
      "current_marketing_channels": [
        "Content Marketing",
        "LinkedIn",
        "Product Hunt"
      ],
      "monthly_users": 5000,
      "customer_acquisition_cost": "$85",
      "retention_strategy": "Email onboarding sequence, in-app tutorials",
      "growth_problems": "High churn rate in first 30 days, low organic traffic"
    },
    "team_organization": {
      "team_size": 8,
      "founder_roles": ["CEO", "CTO", "CPO"],
      "hiring_plan_next_3_months": "1 Senior Engineer, 1 Marketing Manager, 1 Sales Rep",
      "org_challenges": "Remote team coordination, lack of clear processes"
    },
    "competition_market": {
      "known_competitors": [
        "Competitor A",
        "Competitor B",
        "Open Source Solution"
      ],
      "unique_advantage": "AI-powered insights and automation",
      "pricing_model": "Freemium with $49/month Pro plan",
      "market_risks": "Large incumbents entering the space, economic downturn"
    },
    "finance_runway": {
      "monthly_burn": "$75,000",
      "current_revenue": "$12,000 MRR",
      "funding_status": "Seed",
      "runway_months": "14",
      "financial_concerns": "Need to improve unit economics before Series A"
    }
  }
}
```

## 🔧 Project Structure

```
board_panel/
├── src/
│   └── board_panel/
│       ├── __init__.py
│       ├── main.py              # CLI entry point
│       ├── api.py               # FastAPI application
│       ├── crew.py              # CrewAI agent definitions
│       ├── models.py            # Pydantic data models
│       ├── config/
│       │   ├── agents.yaml      # Agent configurations
│       │   └── tasks.yaml       # Task definitions
│       └── tools/
│           ├── __init__.py
│           └── custom_tool.py   # Custom CrewAI tools
├── tests/
├── knowledge/                   # Knowledge base for agents
├── .env                        # Environment variables
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
└── README.md
```

## 🛠️ Custom Tools

The system includes 5 specialized tools:

1. **Market Research Tool**: Industry analysis and market trends
2. **Financial Benchmark Tool**: Startup financial metrics and benchmarks
3. **Tech Stack Analysis Tool**: Technology evaluation and recommendations
4. **Hiring Strategy Tool**: Recruitment planning and compensation guidance
5. **Competitor Analysis Tool**: Competitive intelligence and positioning

## 🧪 Testing

```bash
# Run with example data
python -m board_panel.main

# Test API endpoints
curl http://localhost:8000/health
```

## 📊 Response Structure

Each agent returns:

```json
{
  "agent_name": "Marketing Advisor",
  "strengths": [
    "Strong product-market fit indicators",
    "Diversified marketing channel strategy"
  ],
  "weaknesses": [
    "High customer acquisition cost",
    "Low retention in first 30 days"
  ],
  "suggestions": [
    "Implement cohort analysis to identify churn patterns",
    "Test referral program for viral growth",
    "Optimize onboarding flow with product analytics"
  ],
  "next_month_roadmap": [
    "Week 1: Set up analytics tracking and cohort analysis",
    "Week 2: Launch A/B test for onboarding flow",
    "Week 3: Implement referral program MVP",
    "Week 4: Analyze results and iterate"
  ],
  "detailed_analysis": "Comprehensive 2-3 paragraph analysis..."
}
```

## 🚀 Deployment

### Docker (Coming Soon)

```bash
docker build -t board-panel .
docker run -p 8000:8000 board-panel
```

### Cloud Deployment

Deploy to:
- **AWS**: Lambda + API Gateway
- **Google Cloud**: Cloud Run
- **Heroku**: `heroku create && git push heroku main`
- **Railway**: One-click deploy

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 🔗 Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📧 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@example.com

---

Built with ❤️ using CrewAI and FastAPI
