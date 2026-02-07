"""
Configuration Management for Saudi Projects Intelligence Platform
Loads and validates environment variables and application settings
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True, parents=True)
LOGS_DIR.mkdir(exist_ok=True, parents=True)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/projects.db")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4-turbo-preview")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))

# Scraping Configuration
SCRAPING_ENABLED = os.getenv("SCRAPING_ENABLED", "true").lower() == "true"
SCRAPING_INTERVAL_HOURS = int(os.getenv("SCRAPING_INTERVAL_HOURS", "24"))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / os.getenv("LOG_FILE", "app.log")

# Application Settings
APP_TITLE = os.getenv("APP_TITLE", "Saudi Projects Intelligence Platform")
APP_MODE = os.getenv("APP_MODE", "production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Data Refresh
AUTO_REFRESH_ENABLED = os.getenv("AUTO_REFRESH_ENABLED", "true").lower() == "true"
REFRESH_INTERVAL_MINUTES = int(os.getenv("REFRESH_INTERVAL_MINUTES", "60"))

# AI Configuration
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

# Source Toggles
ENABLE_WEB_SCRAPING = os.getenv("ENABLE_WEB_SCRAPING", "true").lower() == "true"
ENABLE_NEWS_SCRAPING = os.getenv("ENABLE_NEWS_SCRAPING", "true").lower() == "true"
ENABLE_LINKEDIN_SCRAPING = os.getenv("ENABLE_LINKEDIN_SCRAPING", "false").lower() == "true"
# Strict policy: never scrape Google Maps / private platforms.
ENABLE_MAPS_SCRAPING = os.getenv("ENABLE_MAPS_SCRAPING", "false").lower() == "true"

# Saudi Arabia Regions
SAUDI_REGIONS = [
    "Riyadh",
    "Makkah",
    "Madinah",
    "Eastern Province",
    "Asir",
    "Tabuk",
    "Qassim",
    "Ha'il",
    "Northern Borders",
    "Jazan",
    "Najran",
    "Al-Bahah",
    "Al-Jawf"
]

# Project Categories
PROJECT_CATEGORIES = [
    "Residential",
    "Commercial",
    "Infrastructure",
    "Industrial",
    "Mega Project",
    "Healthcare",
    "Education",
    "Transportation",
    "Energy",
    "Tourism",
    "Sports & Entertainment",
    "Government",
    "Mixed-Use"
]

# Project Status Options
PROJECT_STATUS_OPTIONS = [
    "Active",
    "Ongoing",
    "Under Construction",
    "Planning",
    "Announced"
]

# News Sources to Scrape
NEWS_SOURCES: List[str] = [
    "https://www.arabnews.com/taxonomy/term/18266",  # Saudi Arabia Construction
    "https://www.constructionweekonline.com/projects-tenders",
    "https://www.zawya.com/en/projects/construction",
    "https://www.meedprojects.com/countries/saudi-arabia",
    "https://www.saudigazette.com.sa/",
]

# Construction & Real Estate Websites
CONSTRUCTION_SOURCES: List[str] = [
    "https://www.constructionweekonline.com/projects-tenders/saudi-arabia",
    "https://www.bigproject.me/countries/saudi-arabia",
]

# Keywords for Project Detection (English & Arabic)
PROJECT_KEYWORDS_EN = [
    "project", "construction", "development", "building", "infrastructure",
    "contractor", "awarded", "announced", "launched", "ongoing", "active",
    "under construction", "mega project", "saudi", "riyadh", "jeddah"
]

PROJECT_KEYWORDS_AR = [
    "مشروع", "إنشاء", "تطوير", "بناء", "مقاول", "البنية التحتية",
    "تم منح", "أعلن", "قيد الإنشاء", "نشط", "مشروع ضخم"
]

# Status Keywords for Classification
# Keep these broad enough to capture awarded/started projects, but still let
# completed/cancelled keywords take precedence.
ACTIVE_KEYWORDS = [
    # English
    "active",
    "ongoing",
    "under construction",
    "in progress",
    "construction started",
    "construction began",
    "work began",
    "work begins",
    "started",
    "starts",
    "groundbreaking",
    "site work",
    "mobilization",
    "awarded",
    "contract awarded",
    "contract signed",
    "commencement",
    "commence",
    "commenced",
    # Arabic
    "نشط",
    "قيد الإنشاء",
    "قيد الانشاء",
    "تحت الإنشاء",
    "تحت الانشاء",
    "قيد التنفيذ",
    "تحت التنفيذ",
    "جاري التنفيذ",
    "بدء التنفيذ",
    "بدأ التنفيذ",
    "بدء الأعمال",
    "بدأت الأعمال",
    "ترسية",
    "ترسية العقد",
    "تمت الترسية",
    "توقيع عقد",
    "وضع حجر الأساس",
]
COMPLETED_KEYWORDS = ["completed", "finished", "delivered", "inaugurated", "مكتمل", "منجز"]
CANCELLED_KEYWORDS = ["cancelled", "suspended", "halted", "stopped", "ملغي", "متوقف"]

# Confidence Score Weights
CONFIDENCE_WEIGHTS = {
    "source_count": 0.3,      # Multiple sources increase confidence
    "data_completeness": 0.3,  # Complete data fields increase confidence
    "source_reliability": 0.2, # Known reliable sources
    "recency": 0.2            # Recent updates increase confidence
}

# Source Reliability Scores
SOURCE_RELIABILITY = {
    # Official / government
    "spa.gov.sa": 1.0,
    "vision2030.gov.sa": 1.0,
    # Official mega-projects
    "neom.com": 1.0,
    "qiddiya.com": 1.0,
    "redseaglobal.com": 1.0,
    "diriyah.sa": 1.0,
    "roshn.sa": 1.0,
    # Trusted project/news sources
    "meed.com": 0.9,
    "zawya.com": 0.9,
    "constructionweekonline.com": 0.9,
    "arabianbusiness.com": 0.85,
    "saudigazette.com.sa": 0.85,
    "thenationalnews.com": 0.85,
    "arabnews.com": 0.85,
    # Arabic trusted
    "aleqt.com": 0.85,
    "sabq.org": 0.8,
    "okaz.com.sa": 0.8,
    "aawsat.com": 0.8,
    "almadinah.com": 0.8,
    "makkahnewspaper.com": 0.8,
    "default": 0.5
}

def get_source_reliability(url: str) -> float:
    """Get reliability score for a source URL"""
    for domain, score in SOURCE_RELIABILITY.items():
        if domain in url.lower():
            return score
    return SOURCE_RELIABILITY["default"]
