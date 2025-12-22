# Competitive Intelligence Platform

An AI-powered competitive intelligence platform that analyzes competitors using multi-agent architecture with LangGraph orchestration. Get comprehensive insights on pricing, features, market positioning, and strategic recommendations.

URL: https://d13qhhlvt9ye93.cloudfront.net

Swagger: https://api.tavilyapp.com/docs

Postman Collection: https://rohan-chaudhari98-1649539.postman.co/workspace/Rohan-Chaudhari's-team's-Worksp~9b947a67-a94c-48e9-85d9-7a45f4287577/collection/50831799-b6649f63-c444-442a-9ef1-7b69ba52b7bf?action=share&creator=50831799

<img width="3962" height="6400" alt="frontend10-1" src="https://github.com/user-attachments/assets/15954db3-a663-4857-9330-c9465cda903b" />


## 🌟 Features

### Multi-Agent Architecture
- **Discovery Agent** (Optional) - Automatically identifies competitors using GPT-4o-mini + Tavily AI
  - Understands company's core business and market segment
  - Searches for direct competitors using Tavily
  - Validates and filters competitors for relevance
- **Research Agent** - Gathers initial intelligence using Tavily AI search with freshness filtering
  - **Real-time Progress**: Updates shown immediately upon completion
- **Extraction Agent** - Extracts detailed structured data from competitor websites
  - **Real-time Progress**: Updates shown immediately upon completion
  - **Parallel Execution**: Runs simultaneously with Crawl Agent for improved performance
- **Crawl Agent** - Performs deep web crawling for comprehensive data collection
  - **Real-time Progress**: Updates shown immediately upon completion
  - **Parallel Execution**: Runs simultaneously with Extraction Agent for improved performance
- **Analysis Agent** - Synthesizes all data into strategic insights using GPT-4o-mini/GPT-4o
  - **Streaming Output**: Analysis streams in real-time as it's generated
  - **Typewriter Effect**: Text appears character by character (similar to ChatGPT/Claude)
  - **Incremental Updates**: Partial analysis saved to MongoDB every 10 chunks

### Comprehensive Analysis
- **Pricing Comparison** - Competitive pricing models and strategies
- **Feature Analysis** - Feature gaps and competitive advantages
- **Market Positioning** - Target segments and value propositions
- **Additional Insights** - Support quality, partnerships, brand reputation
- **Strategic Recommendations** - Actionable advice for your company
- **Interactive Charts** - Visual data representations automatically generated from analysis
  - **Pricing Bar Chart** - Compare pricing tiers across competitors
  - **Feature Radar Chart** - Multi-dimensional feature comparison (0-10 scale)
  - **Risk Assessment Matrix** - Visual risk analysis with impact and likelihood scores

### Smart Features
- **Auto-Discovery** - Automatically find competitors by just providing your company name
  - Uses GPT-4o-mini to understand your business domain
  - Discovers direct competitors using intelligent search
  - Configurable maximum number of competitors (1-10)
- **Freshness Filter** - Filter search results by time range
  - Options: Anytime, Past Month, Past 3 Months, Past 6 Months, Past Year
  - Ensures you get the most recent competitive intelligence
  - Perfect for tracking recent changes and updates

### Modern User Interface
- **Dark Gradient Hero Section** - Stunning hero with animated blob backgrounds and gradient overlays
- **Modern Design System** - Gradient buttons, enhanced cards with depth, and smooth hover animations
- **Improved Typography** - Inter font family with full weight range (400-900) for better readability
- **Enhanced Form Design** - Rounded input fields with focus states and shadow effects
- **Status Badges** - Gradient status indicators for processing, completed, and failed states
- **Feature Cards** - Interactive cards with gradient icon backgrounds and hover scale effects
- **Three-Tab Interface** - Analysis, Research Results, and Metadata with modern prose styling
- **Interactive Data Visualization** - Charts tab with pricing, features, and risk visualizations using Recharts
- **Query History** - Track and manage all your analyses with improved card layouts
- **Export Reports** - Download as PDF or Word documents with professional formatting
- **Real-time Agent Progress** - Live agent completion tracking with visual progress indicators
- **Agent Collaboration Flow** - Visual diagram showing how agents collaborate in the workflow
- **Complete Query-to-Result Flow** - Step-by-step visualization of the entire analysis pipeline
- **Streaming Analysis** - Typewriter effect for real-time analysis display (similar to ChatGPT/Claude)
- **Real-time Updates** - Live progress tracking with automatic polling every 3 seconds

### Analysis Modes
- **Standard Mode** (GPT-4o-mini) - Fast, cost-effective analysis
- **Premium Mode** (GPT-4o) - Higher quality, deeper insights

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Framework:** FastAPI (Python)
- **AI Orchestration:** LangGraph with streaming support and parallel agent execution
- **LLM:** OpenAI GPT-4o / GPT-4o-mini (with streaming)
- **Search API:** Tavily AI
- **Database:** MongoDB Atlas with real-time updates
- **Logging:** Structured logging with file rotation

**Frontend:**
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS with custom gradient utilities
- **Typography:** Inter font family (weights 400-900)
- **Design System:** Modern gradients, shadows, and animations
- **Charts:** Recharts library for data visualization
- **Routing:** React Router v6
- **Export:** jsPDF, docx
- **Markdown:** react-markdown with enhanced prose styling
- **Real-time Updates:** Polling mechanism with 3-second intervals
- **Typewriter Effect:** Custom component for streaming text display

### System Architecture

![graph8](https://github.com/user-attachments/assets/32fab254-90ce-460c-a2bd-46a25f71c243)

**Workflow Execution:**
- **Sequential Steps**: Discovery → Research → [Extraction + Crawl (parallel)] → Analysis
- **Parallel Execution**: Extraction and Crawl agents run simultaneously after Research completes
- **Performance**: Parallel execution reduces Extraction+Crawl phase time by ~50% (from ~20s to ~10s)
- **State Management**: LangGraph handles state merging for parallel nodes using reducer functions



### Data Flow

1. **User submits query** with company name, analysis focus, and optional settings:
   - **Option A (Auto-Discovery)**: Enable auto-discovery to automatically find competitors
   - **Option B (Manual)**: Provide list of competitors manually
   - **Freshness Filter**: Choose time range for search results (anytime, 1 month, 3 months, 6 months, 1 year)
   - **Premium Analysis**: Choose which model you would want to use (GPT-4o-mini vs GPT-4o)
2. **Discovery Agent** (if enabled) - Uses GPT-4o-mini to understand company domain, then Tavily to discover relevant competitors
   - **Real-time Update**: Progress shown immediately when agent completes
3. **Research Agent** - Searches for each competitor using Tavily AI with freshness filtering applied
   - **Real-time Update**: Progress shown immediately when agent completes
4. **Extraction Agent & Crawl Agent** - Run in **parallel** for improved performance
   - **Extraction Agent**: Extracts structured data from competitor websites
   - **Crawl Agent**: Performs deep crawling for additional context and hidden information
   - **Parallel Execution**: Both agents start simultaneously after Research completes, reducing total execution time by ~50% for this phase
   - **Real-time Updates**: Progress shown immediately when each agent completes
   - **Join Node**: Analysis waits for both agents to finish before proceeding
5. **Analysis Agent** - Synthesizes all data into comprehensive strategic report
   - **Streaming Output**: Analysis streams in real-time with typewriter effect
   - **Live Updates**: Partial analysis visible as it's generated (updates every 10 chunks)
   - **MongoDB Updates**: Analysis saved incrementally to database during generation
7. **Results displayed** in three tabs: Analysis, Research Results, Metadata
   - **Agent Collaboration Flow**: Visual diagram showing complete workflow
   - **Real-time Progress**: Agent completion status updates live
   - **Streaming Analysis**: Text types out character by character as it's generated
8. **Export options** available as PDF or Word documents

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **MongoDB Atlas Account** (free tier works)
- **OpenAI API Key**
- **Tavily API Key**

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/competitive-intelligence-platform.git
cd competitive-intelligence-platform
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
MONGODB_URI=your_mongodb_atlas_connection_string
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
API_PORT=8000
DEBUG=True
EOF

# Start backend server
python -m app.main
```

Backend will run on `http://localhost:8000`

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Frontend will run on `http://localhost:5173`

### API Keys Setup

#### MongoDB Atlas (Free)
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster
3. Create database user
4. Whitelist your IP
5. Get connection string

#### OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create API key
3. Add billing method (pay-as-you-go)

#### Tavily API Key
1. Go to [tavily.com](https://tavily.com)
2. Sign up and get free API key
3. Free tier: 1,000 requests/month

## 📖 Usage

### Basic Workflow

1. **Navigate to home page** (`http://localhost:5173`)

2. **Fill out the form:**
   - **Your Company Name:** e.g., "Tavily"
   - **Analysis Query:** e.g., "Compare pricing strategy and key features"
   - **Choose Input Mode:**
     - **Auto-Discovery (Recommended):** Toggle on to automatically find competitors
       - Select max competitors (1-10)
       - AI will discover the most relevant direct competitors
     - **Manual Entry:** Toggle off to provide your own list
       - Add 1-10 competitors (e.g., "Perplexity AI", "You.com")
   - **Freshness Filter:** Choose time range (Anytime, Past Month, Past 3/6/12 Months)
   - **Premium Analysis:** Optional (uses GPT-4o-mini/GPT-4o for better quality)

3. **Click "Analyze Competitors"**
   - Auto-discovery queries take 40-50 seconds (includes discovery phase)
   - Manual queries take 30-40 seconds
   - **Parallel Execution** - Extraction and Crawl agents run simultaneously for faster processing
   - **Real-time Agent Progress** - Watch agents complete one by one with live updates
   - **Agent Collaboration Flow** - See visual diagram of agent workflow including parallel execution
   - **Streaming Analysis** - Analysis appears with typewriter effect as it's generated
   - Page auto-refreshes every 3 seconds to show latest progress

4. **View Results:**
   - **Agent Collaboration Section** - Shows agent progress cards and complete workflow diagram
   - **Analysis Tab:** 
     - **Narrative Sub-tab:** Comprehensive strategic report in markdown format
       - **Streaming Display** - Text types out in real-time with typewriter effect (similar to ChatGPT)
       - **Live Updates** - Analysis appears as it's generated, not just at the end
     - **Charts Sub-tab:** Interactive visualizations (Pricing Bar Chart, Feature Radar, Risk Matrix)
   - **Research Results Tab:** AI summaries and source links from Tavily
   - **Metadata Tab:** Query details, processing info, and discovery mode

5. **Export Report:**
   - Click "PDF" or "Word" button
   - Download professional report

6. **View History:**
   - Click "History" to see all past queries
   - View or delete previous analyses

### Example Queries

**Using Auto-Discovery (Recommended):**
```
Company: Netflix
Query: Compare pricing tiers, content library features, and competitive risks
Auto-Discovery: Enabled (max 5 competitors)
Freshness: Past 6 Months
```
The system will automatically discover Hulu, HBO Max, Disney+, and other streaming competitors.

**Manual Competitor Entry:**
```
Company: Notion
Query: Analyze collaboration features, pricing tiers, and integration capabilities
Competitors: Confluence, Coda, Airtable
Freshness: Anytime
```

**Recent Changes Tracking:**
```
Company: Shopify
Query: Compare pricing, app ecosystem, and merchant support features
Auto-Discovery: Enabled (max 3 competitors)
Freshness: Past 3 Months
```
Perfect for tracking recent changes in competitive landscape.

**AI Search Engines:**
```
Company: Tavily
Query: Evaluate API capabilities, search quality, and pricing models
Competitors: Perplexity AI, You.com, Brave Search
Freshness: Past Month
```
Use freshness filter to see the latest updates.

## 🔧 Configuration

### Backend Configuration

**`backend/.env`:**
```env
# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/competitive_intel

# OpenAI
OPENAI_API_KEY=sk-...

# Tavily
TAVILY_API_KEY=tvly-...

# Server
API_PORT=8000
DEBUG=True

# CORS (for production, specify exact origins)
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

### Frontend Configuration

**`frontend/.env`:**
```env
VITE_API_URL=http://localhost:8000
```

### Analysis Settings

**Standard vs Premium Mode:**

| Feature | Standard (GPT-4o-mini) | Premium (GPT-4o) |
|---------|------------------------|------------------|
| Cost per query | ~$0.01 | ~$0.60 |
| Speed | 20-30 seconds | 30-45 seconds |
| Quality | Good | Excellent |
| Use case | Most analyses | Critical decisions |

**Adjust in `backend/app/agents/analysis_agent.py`:**
```python
# Change default analysis mode
use_premium = False  # Set to True for premium by default
```

## 📊 API Documentation

### REST API Endpoints

#### Create Query
```http
POST /api/queries
Content-Type: application/json

{
  "company_name": "Tavily",
  "query": "pricing and features",
  "competitors": ["Perplexity AI", "You.com"],
  "use_auto_discovery": false,
  "max_competitors": 5,
  "freshness": "3months",
  "use_premium_analysis": false
}
```

**With Auto-Discovery:**
```http
POST /api/queries
Content-Type: application/json

{
  "company_name": "Netflix",
  "query": "Compare pricing and content library",
  "competitors": [],
  "use_auto_discovery": true,
  "max_competitors": 5,
  "freshness": "6months",
  "use_premium_analysis": false
}
```

**Freshness Options:** `"anytime"`, `"1month"`, `"3months"`, `"6months"`, `"1year"`

Response: 201 Created
{
  "query_id": "abc123...",
  "status": "processing"
}
```

#### Get Query
```http
GET /api/queries/{query_id}

Response: 200 OK
{
  "query_id": "abc123",
  "company_name": "Tavily",
  "query": "pricing and features",
  "competitors": ["Perplexity AI", "You.com"],
  "status": "completed",
  "research_results": [...],
  "analysis": "...",
  "chart_data": {
    "pricing": [...],
    "features": [...],
    "risks": [...]
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### List Queries
```http
GET /api/queries?skip=0&limit=50

Response: 200 OK
[
  {
    "query_id": "abc123",
    "company_name": "Tavily",
    "status": "completed",
    "competitor_count": 2,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Delete Query
```http
DELETE /api/queries/{query_id}

Response: 200 OK
{
  "deleted": true
}
```

**Interactive API Docs:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

### Backend Tests

**Prerequisites:**
- Virtual environment must be activated
- All dependencies installed (`pip install -r requirements.txt`)
- `.env` file configured with API keys (MongoDB, OpenAI, Tavily)

**Run all tests:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pytest -v
```

**Run specific test file:**
```bash
pytest -v test_api.py           # API endpoint tests
pytest -v test_workflow.py      # LangGraph workflow tests
pytest -v test_mongodb.py       # MongoDB service tests
pytest -v test_pipeline.py      # Complete pipeline tests
pytest -v test_config.py        # Configuration tests
```

**Run specific test:**
```bash
pytest -v test_api.py::test_health_check
pytest -v test_workflow.py::test_langgraph_workflow
```

**Test options:**
- `-v` or `--verbose`: Show detailed output with test names
- `-s`: Show print statements and logs
- `--collect-only`: Show which tests would be run without executing them

**Test Categories:**

1. **Unit/Component Tests** (run without server):
   - `test_config.py` - Configuration loading
   - `test_mongodb.py` - MongoDB connection and operations
   - `test_workflow.py` - LangGraph workflow orchestration
   - `test_pipeline.py` - Complete agent pipeline

2. **API Integration Tests** (require FastAPI server):
   - `test_api.py` - All API endpoint tests
   - These tests will be **skipped** if the server is not running

**To run API integration tests:**

1. Start the FastAPI server in one terminal:
   ```bash
   cd backend
   source venv/bin/activate
   python -m app.main
   # Or: uvicorn app.main:app --reload
   ```

2. Run tests in another terminal:
   ```bash
   cd backend
   source venv/bin/activate
   pytest -v
   ```

**Expected output:**
- Unit/component tests will pass without server (5+ tests)
- API tests will be skipped if server is not running
- All tests will run and pass if server is running

**Note:** The test suite uses `pytest-asyncio` for async test support, configured via `pytest.ini`.

### Frontend Tests

**Prerequisites:**
- All dependencies installed (`npm install`)
- Node.js 18+ required

**Run all tests:**
```bash
cd frontend
npm test
```

**Run tests in watch mode:**
```bash
npm test  # Runs in watch mode by default
```

**Run tests once (CI mode):**
```bash
npm test -- --run
```

**Run specific test file:**
```bash
npm test -- src/components/LoadingSpinner.test.jsx
npm test -- src/components/QueryForm.test.jsx
npm test -- src/pages/HomePage.test.jsx
```

**Test options:**
- `--run`: Run tests once and exit (useful for CI)
- `--ui`: Open Vitest UI in browser
- `--coverage`: Generate coverage report

**Test Framework:**
- **Vitest** - Fast Vite-native unit test framework
- **React Testing Library** - Simple and complete React DOM testing utilities
- **jsdom** - DOM implementation for Node.js

**Test Files:**
- `src/components/LoadingSpinner.test.jsx` - Tests for loading spinner component
- `src/components/QueryForm.test.jsx` - Tests for query form including auto-discovery, freshness filter, and form validation
- `src/pages/HomePage.test.jsx` - Tests for homepage layout and components

**Test Coverage:**
- Component rendering
- User interactions (typing, clicking, selecting)
- Form validation
- State management
- API integration (mocked)

**Expected output:**
```
✓ src/components/LoadingSpinner.test.jsx (3 tests)
✓ src/pages/HomePage.test.jsx (4 tests)
✓ src/components/QueryForm.test.jsx (7 tests)

Test Files  3 passed (3)
     Tests  14 passed (14)
```

## 📁 Project Structure
```
Tavily-LangGraph
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── discovery_agent.py     # Auto-competitor discovery (GPT-4o-mini + Tavily)
│   │   │   ├── research_agent.py      # Tavily AI search (with freshness filter)
│   │   │   ├── extraction_agent.py    # Website data extraction
│   │   │   ├── crawl_agent.py         # Deep web crawling
│   │   │   └── analysis_agent.py      # GPT-4o-mini/GPT-4o synthesis + chart data extraction
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── routes.py              # API endpoints
│   │   ├── clients/
│   │   │   ├── openai_client.py
│   │   │   └── tavily_client.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── background.py
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── state.py
│   │   │   └── workflow.py            # LangGraph orchestration
│   │   ├── middleware/
│   │   │   ├──  __init__.py
│   │   │   ├── error_handler.py
│   │   │   └── request_logger.py
│   │   ├── services/                  # mongodb operations
│   │   │   ├── __init__.py          
│   │   │   ├── mongodb_dependency.py
│   │   │   └── mongodb_service.py 
│   │   ├── utils/
│   │   │   ├── __init__.py   
│   │   │   ├── env.py
│   │   │   └── logging_config.py
│   │   ├── config.py
│   │   └── main.py                    # FastAPI app
│   ├── requirements.txt
│   ├── Procfile
│   ├── .gitignore
│   ├── .ebignore
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_workflow.py
│   ├── test_pipeline.py
│   ├── test_mongodb.py
│   └── .env.example
│
├── frontend/
│   ├── public/
│   │   ├── vite.svg
│   ├── src/
│   │   ├── assets/
│   │   │   ├── react.svg
│   │   ├── pages/
│   │   │   ├── HomePage.jsx           # Main landing page
│   │   │   ├── HistoryPage.jsx        # Query history
│   │   │   └── ResultsPage.jsx        # Results display
│   │   ├── components/
│   │   │   ├── QueryForm.jsx          # Query submission form
│   │   │   ├── QueryForm.test.jsx
│   │   │   ├── ResultsDisplay.jsx     # Three-tab results with charts
│   │   │   ├── ExportButtons.jsx      # PDF/Word export
│   │   │   ├── CompetitorInput.jsx    # Competitor management
│   │   │   ├── AgentProgress.jsx      # To track real-time agent progress
│   │   │   ├── ErrorBoundary.jsx      # Error Handling
│   │   │   ├── LoadingSpinner.jsx     # Spinner
│   │   │   ├── LoadingSpinner.test.jsx
│   │   │   ├── TypewriterText.jsx
│   │   │   └── charts/
│   │   │       ├── ChartsView.jsx     # Main charts container
│   │   │       ├── PricingChart.jsx   # Bar chart for pricing comparison
│   │   │       ├── FeatureRadar.jsx   # Radar chart for features
│   │   │       └── RiskMatrix.jsx     # Risk assessment visualization
│   │   ├── pages/
│   │   │   ├── HistoryPage.jsx
│   │   │   ├── HomePage.jsx
│   │   │   ├── HomePage.test.jsx
│   │   │   └── ResultsPage.jsx
│   │   ├── services/
│   │   │   ├── api.js                 # API client
│   │   │   └── exportService.js       # Export functionality
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css                  # Tailwind styles
│   ├── package.json
│   ├── index.html
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── .gitignore
│   └── .env.production
└── README.md
```

## 🔒 Security Considerations

### API Keys
- **Never commit `.env` files** to version control
- Use environment variables for all secrets
- Rotate API keys regularly

### CORS
- In production, specify exact frontend origins
- Don't use wildcard (`*`) in production

### Rate Limiting
- Implement rate limiting for API endpoints
- Monitor API usage and costs

### Data Privacy
- Query data contains competitor information
- Ensure MongoDB security rules are configured
- Use HTTPS in production

## 💰 Cost Estimation

**Per Query (Manual, 2 competitors, Standard mode):**
- Tavily API: ~$0.002 (5 searches)
- OpenAI GPT-4o-mini: ~$0.008 (analysis) + ~$0.001 (chart data extraction)
- **Total: ~$0.01 per query**

**Per Query (Auto-Discovery, 2 competitors discovered, Standard mode):**
- OpenAI GPT-4o-mini: ~$0.002 (discovery agent - company analysis + validation)
- Tavily API: ~$0.004 (discovery searches + 5 research searches)
- OpenAI GPT-4o-mini: ~$0.008 (analysis)
**Total: ~$0.014 per query**

**Per Query (Manual, 2 competitors, Premium mode):**
- Tavily API: ~$0.002
- OpenAI GPT-4o: ~$0.60 (analysis)
- **Total: ~$0.60 per query**

**Per Query (Auto-Discovery, 2 competitors discovered, Premium mode):**
- OpenAI GPT-4o-mini: ~$0.002 (discovery)
- Tavily API: ~$0.004
- OpenAI GPT-4o: ~$0.60 (analysis)
**Total: ~$0.606 per query**

**Monthly Estimate (100 queries, 50% auto-discovery):**
- Standard mode: ~$1.20/month (50 manual @ $0.01 + 50 auto @ $0.014)
- Premium mode: ~$60.30/month (50 manual @ $0.60 + 50 auto @ $0.606)


## 🚀 Deployment

### AWS Deployment (Recommended)

**Backend (Elastic Beanstalk):**
```bash
cd backend
eb init
eb create production
eb deploy
```

**Frontend (S3 + CloudFront):**
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket-name
aws cloudfront create-invalidation \                           
  --distribution-id <distribution_id> \
  --paths "/*"
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check port 8000 is free
lsof -i:8000
kill -9 $(lsof -ti:8000)

# Verify environment variables
cat backend/.env

# Check MongoDB connection
mongo "your_mongodb_uri"
```

### Frontend won't start
```bash
# Check port 5173 is free
lsof -i:5173
kill -9 $(lsof -ti:5173)

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### CORS errors
- Verify backend CORS settings include frontend URL
- Check frontend `.env` has correct API URL
- Restart both servers

### Analysis fails
- Check API keys are valid
- Verify MongoDB connection
- Check backend logs for errors
- Ensure competitors exist and are searchable

### Auto-discovery issues
- Discovery agent requires valid OpenAI API key
- Ensure company name is recognizable (use full company name)
- Check backend logs for discovery agent errors
- If discovery fails, try manual competitor entry as fallback
- Discovery uses GPT-4o-mini which may have rate limits

## 🙏 Acknowledgments

- **Tavily AI** - AI-powered search API
- **OpenAI** - GPT-4 language models
- **LangGraph** - Multi-agent orchestration
- **MongoDB Atlas** - Cloud database
- **Tailwind CSS** - Modern styling framework
- **Recharts** - React charting library for data visualization

---

**Built using Tavily and LangGraph**
