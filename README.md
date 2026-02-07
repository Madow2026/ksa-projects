# 🏗️ Saudi Projects Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://openai.com/)

An AI-powered intelligence platform that automatically discovers, extracts, classifies, and tracks **ACTIVE & ONGOING construction and development projects** across Saudi Arabia.

## 🎯 Overview

This platform combines **web scraping**, **AI/NLP**, and **data intelligence** to create a comprehensive, continuously-updated database of Saudi Arabian projects from multiple sources including news sites, construction portals, LinkedIn, and Google Maps.

### ✨ Key Features

- 🤖 **AI-Powered Extraction**: Uses GPT-4 and NLP to extract structured data from unstructured text
- 🌐 **Multi-Source Scraping**: Aggregates data from news, construction sites, and portals
- 🔍 **Smart Deduplication**: Semantic similarity detection prevents duplicate entries
- 📊 **Real-Time Dashboard**: Modern Streamlit UI with interactive visualizations
- 🎯 **Confidence Scoring**: AI evaluates data quality and completeness
- 🔄 **Auto-Updates**: Continuous monitoring and project status updates
- 🌍 **Bilingual Support**: Handles both Arabic and English content
- 📦 **Export Capability**: Export project data to Excel

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB UI                         │
│         (Dashboard, Filters, Visualizations)                │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                DATA PROCESSING PIPELINE                     │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Scrapers   │──│  AI Engine   │──│  Deduplication  │  │
│  │  Orchestrator│  │  (NLP/GPT)   │  │   & Scoring     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   DATABASE LAYER                            │
│              SQLite (MVP) / PostgreSQL                      │
│   Projects | Sources | Regions | Logs | Updates            │
└─────────────────────────────────────────────────────────────┘
```

### 📁 Project Structure

```
saudi-projects-intelligence/
│
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration & settings
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
│
├── database/                       # Database layer
│   ├── __init__.py
│   ├── models.py                   # SQLAlchemy models
│   └── db_manager.py               # Database operations
│
├── ai_engine/                      # AI & NLP engine
│   ├── __init__.py
│   └── nlp_engine.py               # AI extraction & classification
│
├── scrapers/                       # Web scrapers
│   ├── __init__.py
│   ├── base_scraper.py             # Base scraper class
│   ├── news_scraper.py             # News websites scraper
│   ├── construction_scraper.py     # Construction sites scraper
│   └── scraper_orchestrator.py     # Scraper coordinator
│
├── data_processing/                # Data pipeline
│   ├── __init__.py
│   └── pipeline.py                 # Main processing pipeline
│
├── utils/                          # Utilities
│   ├── __init__.py
│   ├── logger.py                   # Logging configuration
│   └── demo_data.py                # Demo data generator
│
├── data/                           # Data directory (auto-created)
│   └── projects.db                 # SQLite database
│
├── logs/                           # Logs directory (auto-created)
│   ├── app.log
│   └── errors.log
│
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Internet connection for scraping
- OpenAI API key (optional but recommended for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/saudi-projects-intelligence.git
   cd saudi-projects-intelligence
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key (optional)
   # OPENAI_API_KEY=your_api_key_here
   ```

5. **Generate demo data (optional)**
   ```bash
   python utils/demo_data.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **Access the dashboard**
   - Open browser to `http://localhost:8501`
   - Click "Run Pipeline" to start discovering projects

## 🧠 How AI Works

### 1. **Data Extraction**

The AI engine extracts structured information from unstructured text:

```python
Input: Raw article/webpage text
       ↓
AI Processing (GPT-4)
       ↓
Output: {
    "project_name": "King Salman Park",
    "status": "Under Construction",
    "region": "Riyadh",
    "category": "Mega Project",
    "owner": "Royal Commission for Riyadh City",
    "contractor": "Saudi Binladin Group",
    ...
}
```

### 2. **Classification & Validation**

- **Status Classification**: Identifies if project is Active/Ongoing/Completed
- **Category Detection**: Classifies into 13+ categories
- **Region Mapping**: Maps locations to Saudi regions
- **Quality Filtering**: Rejects completed/cancelled projects

### 3. **Confidence Scoring**

Each project gets a confidence score (0-1) based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Source Count | 30% | Multiple sources increase confidence |
| Data Completeness | 30% | More filled fields = higher confidence |
| Source Reliability | 20% | Known reliable sources score higher |
| Recency | 20% | Recent updates are more confident |

### 4. **Deduplication**

Uses semantic similarity to detect duplicates:
- Compares project names using transformer embeddings
- Checks location matching
- Merges duplicate entries and updates with new information

## 📊 Data Sources

The platform scrapes from multiple sources:

### Configured Sources

1. **News Websites**
   - Arab News (Construction section)
   - Construction Week Online
   - Zawya Projects
   - MEED Projects
   - Saudi Gazette

2. **Construction Portals**
   - Construction Week Online (Saudi Arabia)
   - Big Project ME

3. **Google News** (Arabic & English queries)
   - Saudi construction projects
   - Mega projects
   - Regional developments

### Adding New Sources

Edit `config.py` to add new sources:

```python
NEWS_SOURCES = [
    "https://your-new-source.com",
    # Add more sources here
]
```

## 🎨 Dashboard Features

### Main Dashboard

- **KPI Cards**: Total projects, top region, average confidence, new projects
- **Regional Chart**: Bar chart of projects by region
- **Category Chart**: Pie chart of project categories
- **Interactive Table**: Sortable, filterable project list
- **Smart Search**: Full-text search across all fields

### Filters

- Region filter (13 Saudi regions)
- City search
- Category filter (13+ categories)
- Contractor search
- Project status

### Data Pipeline Control

- One-click pipeline execution
- Real-time progress tracking
- Recent activity log
- Error monitoring

## 🔧 Configuration

Key settings in `config.py`:

```python
# AI Settings
AI_MODEL = "gpt-4-turbo-preview"
CONFIDENCE_THRESHOLD = 0.7

# Scraping Settings
SCRAPING_INTERVAL_HOURS = 24
MAX_CONCURRENT_REQUESTS = 5

# Source Toggles
ENABLE_WEB_SCRAPING = True
ENABLE_NEWS_SCRAPING = True
ENABLE_LINKEDIN_SCRAPING = False
```

## 📈 Database Schema

### Projects Table

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| project_name | String | Project name |
| status | String | Active/Ongoing/Under Construction |
| region | String | Saudi region |
| city | String | City name |
| category | String | Project category |
| project_owner | String | Client/Owner |
| main_contractor | String | Main contractor |
| consultant | String | Consultant company |
| confidence_score | Float | AI confidence (0-1) |
| first_discovered | DateTime | First discovery date |
| last_updated | DateTime | Last update date |

### Additional Tables

- **sources**: Project source URLs
- **regions**: Saudi regions reference
- **update_logs**: Change history
- **scraping_logs**: Scraping operations log

## 🔄 Automation

### Scheduled Updates

For production deployment, use a scheduler:

**Linux/Mac (cron):**
```bash
# Run pipeline daily at 2 AM
0 2 * * * cd /path/to/project && python -c "from data_processing.pipeline import data_pipeline; data_pipeline.run_full_pipeline()"
```

**Windows (Task Scheduler):**
- Create a task to run `python -c "from data_processing.pipeline import data_pipeline; data_pipeline.run_full_pipeline()"`

## 🚀 Deployment

### Local Deployment

```bash
streamlit run app.py --server.port 8501
```

### Production Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Add secrets (OpenAI API key)
5. Deploy

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 🧪 Testing

### Generate Demo Data

```bash
python utils/demo_data.py
```

### Run Pipeline Manually

```bash
python -c "from data_processing.pipeline import data_pipeline; data_pipeline.run_full_pipeline()"
```

### Check Database

```bash
python -c "from database.db_manager import db_manager; print(db_manager.get_dashboard_stats())"
```

## 📝 API Reference

### Database Manager

```python
from database.db_manager import db_manager

# Get all projects
projects = db_manager.get_all_projects(region="Riyadh", limit=100)

# Search projects
results = db_manager.search_projects("construction")

# Get statistics
stats = db_manager.get_dashboard_stats()
```

### AI Engine

```python
from ai_engine.nlp_engine import ai_engine

# Extract project info
text = "New project in Riyadh..."
project = ai_engine.extract_project_info(text, source_url)

# Calculate confidence
confidence = ai_engine.calculate_confidence_score(project_data)

# Check similarity
is_dup = ai_engine.is_duplicate(project1, project2)
```

### Scraper Orchestrator

```python
from scrapers.scraper_orchestrator import scraper_orchestrator

# Run all scrapers
items = scraper_orchestrator.scrape_all(parallel=False)

# Run specific scraper
items = scraper_orchestrator.scrape_single("News Sources")
```

## 🛠️ Troubleshooting

### Common Issues

**1. OpenAI API Error**
```
Solution: Check your API key in .env file
```

**2. Scraping Blocked**
```
Solution: Some sites may block scrapers. Use delays and proper user agents.
Check config.py for USER_AGENT setting.
```

**3. Database Locked**
```
Solution: SQLite doesn't handle concurrent writes well.
For production, migrate to PostgreSQL.
```

**4. Memory Issues**
```
Solution: Reduce MAX_CONCURRENT_REQUESTS in config.py
Process data in smaller batches
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **Streamlit** for the web framework
- **BeautifulSoup & Scrapy** for web scraping
- **Sentence Transformers** for semantic similarity
- **SQLAlchemy** for database ORM

## 📞 Contact

For questions, issues, or suggestions:

- Create an issue on GitHub
- Email: your-email@example.com
- LinkedIn: [Your Profile]

---

**Built with ❤️ for Saudi Arabia's Construction Industry**

*Last Updated: February 2026*
