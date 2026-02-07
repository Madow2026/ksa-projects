# 📂 Project Directory Tree

```
saudi-projects-intelligence/
│
├── 📄 app.py                          # Main Streamlit Dashboard Application
├── 📄 main.py                         # CLI Entry Point (web, pipeline, demo, stats)
├── 📄 config.py                       # Centralized Configuration & Settings
│
├── 📋 requirements.txt                # Python Dependencies (40+ packages)
├── 🔐 .env.example                    # Environment Variables Template
├── 🚫 .gitignore                      # Git Ignore Rules
│
├── 📚 README.md                       # Main Documentation (Comprehensive)
├── 📚 QUICKSTART.md                   # 5-Minute Quick Start Guide
├── 📚 ARCHITECTURE.md                 # Technical Architecture & AI Details
├── 📚 CONTRIBUTING.md                 # Contribution Guidelines
├── 📚 PROJECT_SUMMARY.md              # Complete Project Overview
├── 📚 LICENSE                         # MIT License
│
├── 🔧 setup.bat                       # Windows Setup Script
├── 🔧 setup.sh                        # Linux/Mac Setup Script (chmod +x)
│
├── 🗄️ database/                       # DATABASE LAYER
│   ├── __init__.py
│   ├── models.py                      # SQLAlchemy Models (5 tables)
│   │                                  # - Project (main entity)
│   │                                  # - Source (URLs)
│   │                                  # - Region (reference)
│   │                                  # - UpdateLog (history)
│   │                                  # - ScrapingLog (activity)
│   │
│   └── db_manager.py                  # Database Manager Class
│                                      # - CRUD operations
│                                      # - Query methods
│                                      # - Statistics
│                                      # - Transaction management
│
├── 🧠 ai_engine/                      # AI & NLP ENGINE
│   ├── __init__.py
│   └── nlp_engine.py                  # AI Engine Class
│                                      # - GPT-4 extraction
│                                      # - Rule-based fallback
│                                      # - Entity recognition
│                                      # - Status classification
│                                      # - Category classification
│                                      # - Semantic similarity
│                                      # - Confidence scoring
│                                      # - Deduplication
│                                      # - Arabic + English support
│
├── 🌐 scrapers/                       # WEB SCRAPING SYSTEM
│   ├── __init__.py
│   │
│   ├── base_scraper.py                # Abstract Base Scraper
│   │                                  # - HTTP client
│   │                                  # - Retry logic
│   │                                  # - Error handling
│   │                                  # - Rate limiting
│   │
│   ├── news_scraper.py                # News Websites Scraper
│   │                                  # - Multiple news sources
│   │                                  # - Article extraction
│   │                                  # - Date parsing
│   │
│   ├── construction_scraper.py        # Construction Sites Scraper
│   │                                  # - Project listings
│   │                                  # - Specialized parsers
│   │                                  # - MEED Projects
│   │
│   └── scraper_orchestrator.py       # Scraper Coordinator
│                                      # - Parallel execution
│                                      # - Error aggregation
│                                      # - Status tracking
│
├── 🔄 data_processing/                # DATA PIPELINE
│   ├── __init__.py
│   └── pipeline.py                    # Main Processing Pipeline
│                                      # - Scrape → Extract → Validate
│                                      # - Deduplicate → Store
│                                      # - Update existing projects
│                                      # - Performance tracking
│                                      # - Error recovery
│
├── 🛠️ utils/                          # UTILITIES
│   ├── __init__.py
│   ├── logger.py                      # Logging Configuration
│   │                                  # - Console logging (colored)
│   │                                  # - File logging (rotating)
│   │                                  # - Error logging (separate)
│   │
│   └── demo_data.py                   # Demo Data Generator
│                                      # - 15 sample projects
│                                      # - Realistic data
│                                      # - Quick testing
│
├── 💾 data/                           # DATA DIRECTORY (auto-created)
│   ├── projects.db                    # SQLite Database (created at runtime)
│   └── *.xlsx                         # Exported Excel files
│
└── 📋 logs/                           # LOGS DIRECTORY (auto-created)
    ├── app.log                        # Application logs (10MB rotation)
    └── errors.log                     # Error logs only (10MB rotation)


📊 CODE METRICS:
├── Total Python Files: 16
├── Total Lines of Code: ~3,500+
├── Database Tables: 5
├── API Endpoints: N/A (Desktop app)
├── Scrapers: 4 (News, Google News, Construction, MEED)
├── AI Models: 2 (GPT-4, Sentence Transformers)
└── Documentation Files: 7


🎯 KEY ENTRY POINTS:
├── app.py              → Launch Streamlit Dashboard
├── main.py web         → Launch Dashboard via CLI
├── main.py pipeline    → Run Data Collection Pipeline
├── main.py demo        → Generate Demo Data
└── main.py stats       → Show Database Statistics


🔧 CONFIGURATION FILES:
├── config.py           → Application Settings
├── .env                → Environment Variables (API keys)
├── requirements.txt    → Python Dependencies
└── .gitignore         → Git Ignore Rules


📚 DOCUMENTATION:
├── README.md          → Main documentation (Installation, Usage, API)
├── QUICKSTART.md      → 5-minute quick start guide
├── ARCHITECTURE.md    → Technical architecture & AI implementation
├── CONTRIBUTING.md    → How to contribute
├── PROJECT_SUMMARY.md → Complete project overview
└── LICENSE            → MIT License


🚀 DEPLOYMENT FILES:
├── setup.bat          → Windows automated setup
└── setup.sh           → Linux/Mac automated setup


📦 PACKAGE STRUCTURE:
├── database/          → Data layer (ORM, queries)
├── ai_engine/         → Intelligence layer (AI, NLP)
├── scrapers/          → Data collection layer
├── data_processing/   → Pipeline orchestration
└── utils/             → Helper functions & tools
```

---

## 🎨 Visual Architecture

```
┌─────────────────────────────────────────────────┐
│            STREAMLIT WEB UI (app.py)            │
│  Dashboard │ Charts │ Filters │ Search │ Export │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         DATA PIPELINE (data_processing/)        │
│  Scrape → AI Extract → Validate → Dedupe → DB  │
└─┬──────────┬────────────┬────────────┬─────────┘
  │          │            │            │
  ▼          ▼            ▼            ▼
┌───────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
│Scrapers│ │AI Engine│ │Pipeline │ │ Database │
│ 4 types│ │GPT-4+NLP│ │Orchestr.│ │SQLAlchemy│
└────────┘ └─────────┘ └─────────┘ └──────────┘
```

---

## 📊 Database Schema

```
┌─────────────────┐
│    projects     │ ← Main table
│─────────────────│
│ id (PK)         │
│ project_name    │
│ status          │
│ region          │
│ city            │
│ category        │
│ owner           │
│ contractor      │
│ confidence      │
│ ...             │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│    sources      │ ← Project URLs
│─────────────────│
│ id (PK)         │
│ project_id (FK) │
│ source_url      │
│ source_type     │
│ reliability     │
└─────────────────┘
```

---

## 🔄 Data Flow

```
Internet Sources
      ↓
  Scrapers (4 types)
      ↓
  Raw HTML/Text
      ↓
  AI Engine (Extract + Classify)
      ↓
  Structured Data
      ↓
  Validation + Scoring
      ↓
  Deduplication Check
      ↓
  Database Storage
      ↓
  Streamlit Dashboard
```

---

## 💡 Quick Stats

- **Total Files**: 23 Python + 7 Docs
- **Code Lines**: ~3,500+
- **Dependencies**: 40+ packages
- **Database Tables**: 5
- **Scrapers**: 4
- **AI Models**: 2
- **Supported Regions**: 13
- **Project Categories**: 13+
- **Languages**: Arabic + English

---

**Legend**:
- 📄 Python script
- 📋 Text/Config file
- 📚 Documentation
- 🗄️ Database module
- 🧠 AI module
- 🌐 Scraping module
- 🔄 Pipeline module
- 🛠️ Utility module
- 💾 Data directory
- 📋 Logs directory
