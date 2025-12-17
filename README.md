# Competitive Intelligence Platform

An AI-powered competitive intelligence platform that analyzes competitors using multi-agent architecture with LangGraph orchestration. Get comprehensive insights on pricing, features, market positioning, and strategic recommendations.

![Platform Screenshot](docs/screenshot.png)

## 🌟 Features

### Multi-Agent Architecture
- **Research Agent** - Gathers initial intelligence using Tavily AI search
- **Extraction Agent** - Extracts detailed structured data from competitor websites
- **Crawl Agent** - Performs deep web crawling for comprehensive data collection
- **Analysis Agent** - Synthesizes all data into strategic insights using GPT-4

### Comprehensive Analysis
- **Pricing Comparison** - Competitive pricing models and strategies
- **Feature Analysis** - Feature gaps and competitive advantages
- **Market Positioning** - Target segments and value propositions
- **Additional Insights** - Support quality, partnerships, brand reputation
- **Strategic Recommendations** - Actionable advice for your company

### Modern User Interface
- **Beautiful Design** - Modern gradients, glassmorphism, smooth animations
- **Three-Tab Interface** - Analysis, Research Results, Metadata
- **Query History** - Track and manage all your analyses
- **Export Reports** - Download as PDF or Word documents
- **Real-time Updates** - Live progress tracking during analysis

### Analysis Modes
- **Standard Mode** (GPT-4o-mini) - Fast, cost-effective analysis
- **Premium Mode** (GPT-4o) - Higher quality, deeper insights

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Framework:** FastAPI (Python)
- **AI Orchestration:** LangGraph
- **LLM:** OpenAI GPT-4o / GPT-4o-mini
- **Search API:** Tavily AI
- **Database:** MongoDB Atlas
- **Web Scraping:** BeautifulSoup4, Playwright

**Frontend:**
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS
- **Routing:** React Router v6
- **Export:** jsPDF, docx
- **Markdown:** react-markdown

### System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  (React + Tailwind CSS - Modern Gradient Design)               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  • REST API Endpoints                                           │
│  • Background Job Processing                                    │
│  • CORS Configuration                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LangGraph Workflow                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Research   │→ │  Extraction  │→ │     Crawl    │         │
│  │    Agent     │  │    Agent     │  │    Agent     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                           │                                     │
│                           ▼                                     │
│                  ┌──────────────┐                              │
│                  │   Analysis   │                              │
│                  │    Agent     │                              │
│                  └──────────────┘                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
│  • Tavily AI (Search & Summarization)                          │
│  • OpenAI GPT-4 (Analysis)                                     │
│  • MongoDB Atlas (Data Storage)                                │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User submits query** with company name, competitors, and analysis focus
2. **Research Agent** searches for each competitor using Tavily AI
3. **Extraction Agent** extracts structured data from competitor websites
4. **Crawl Agent** performs deep crawling for additional context
5. **Analysis Agent** synthesizes all data into comprehensive report
6. **Results displayed** in three tabs: Analysis, Research Results, Metadata
7. **Export options** available as PDF or Word documents

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
4. Whitelist your IP (or use 0.0.0.0/0 for development)
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
   - **Competitors:** Add 1-10 competitors (e.g., "Perplexity AI", "You.com")
   - **Premium Analysis:** Optional (uses GPT-4o for better quality)

3. **Click "Analyze Competitors"**
   - Analysis takes 20-40 seconds
   - Progress shown in real-time
   - Page auto-refreshes every 3 seconds

4. **View Results:**
   - **Analysis Tab:** Comprehensive strategic report
   - **Research Results Tab:** AI summaries and source links
   - **Metadata Tab:** Query details and processing info

5. **Export Report:**
   - Click "PDF" or "Word" button
   - Download professional report

6. **View History:**
   - Click "History" to see all past queries
   - View or delete previous analyses

### Example Queries

**SaaS Product Comparison:**
```
Company: Notion
Query: Analyze collaboration features, pricing tiers, and integration capabilities
Competitors: Confluence, Coda, Airtable
```

**E-commerce Platform:**
```
Company: Shopify
Query: Compare pricing, app ecosystem, and merchant support features
Competitors: WooCommerce, BigCommerce, Squarespace
```

**AI Search Engines:**
```
Company: Tavily
Query: Evaluate API capabilities, search quality, and pricing models
Competitors: Perplexity AI, You.com, Brave Search
```

**Video Conferencing:**
```
Company: Zoom
Query: Compare meeting capacity, recording features, and enterprise pricing
Competitors: Microsoft Teams, Google Meet, Webex
```

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
  "use_premium_analysis": false
}

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
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing Checklist

- [ ] Submit query with 2-3 competitors
- [ ] Verify real-time progress updates
- [ ] Check all three tabs display correctly
- [ ] Export to PDF - verify complete content
- [ ] Export to Word - verify complete content
- [ ] View query in history page
- [ ] Delete query from history
- [ ] Test with premium analysis mode
- [ ] Test error handling (invalid competitor name)

## 📁 Project Structure
```
competitive-intelligence-platform/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── research_agent.py      # Tavily AI search
│   │   │   ├── extraction_agent.py    # Website data extraction
│   │   │   ├── crawl_agent.py         # Deep web crawling
│   │   │   └── analysis_agent.py      # GPT-4 synthesis
│   │   ├── workflow/
│   │   │   └── competitive_intel_workflow.py  # LangGraph orchestration
│   │   ├── database/
│   │   │   └── mongodb.py             # MongoDB operations
│   │   ├── routes/
│   │   │   └── queries.py             # API endpoints
│   │   └── main.py                    # FastAPI app
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx           # Main landing page
│   │   │   ├── HistoryPage.jsx        # Query history
│   │   │   └── ResultsPage.jsx        # Results display
│   │   ├── components/
│   │   │   ├── QueryForm.jsx          # Query submission form
│   │   │   ├── ResultsDisplay.jsx     # Three-tab results
│   │   │   ├── ExportButtons.jsx      # PDF/Word export
│   │   │   └── CompetitorInput.jsx    # Competitor management
│   │   ├── services/
│   │   │   ├── api.js                 # API client
│   │   │   └── exportService.js       # Export functionality
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css                  # Tailwind styles
│   ├── package.json
│   └── .env
│
├── docs/
│   ├── architecture.md
│   ├── api-documentation.md
│   └── deployment-guide.md
│
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

**Per Query (2 competitors, Standard mode):**
- Tavily API: ~$0.002 (5 searches)
- OpenAI GPT-4o-mini: ~$0.008 (analysis)
- **Total: ~$0.01 per query**

**Per Query (2 competitors, Premium mode):**
- Tavily API: ~$0.002
- OpenAI GPT-4o: ~$0.60 (analysis)
- **Total: ~$0.60 per query**

**Monthly Estimate (100 queries):**
- Standard mode: ~$1.00/month
- Premium mode: ~$60.00/month

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
```

**See [docs/deployment-guide.md](docs/deployment-guide.md) for detailed instructions.**

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

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Contact

For questions or support:
- GitHub Issues: [github.com/yourusername/repo/issues](https://github.com/yourusername/repo/issues)
- Email: your.email@example.com

## 🙏 Acknowledgments

- **Tavily AI** - AI-powered search API
- **OpenAI** - GPT-4 language models
- **LangGraph** - Multi-agent orchestration
- **MongoDB Atlas** - Cloud database
- **Tailwind CSS** - Modern styling framework

---

**Built with ❤️ using AI agents and LangGraph**