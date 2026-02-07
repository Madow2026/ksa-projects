"""
Base Scraper Class for Saudi Projects Intelligence Platform
All specific scrapers inherit from this base class
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import random
from loguru import logger
from abc import ABC, abstractmethod

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import USER_AGENT, REQUEST_TIMEOUT, MAX_CONCURRENT_REQUESTS


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, source_name: str, source_type: str):
        """Initialize scraper"""
        self.source_name = source_name
        self.source_type = source_type
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.scraped_count = 0
        self.error_count = 0
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method - must be implemented by subclasses"""
        pass
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch a web page and return BeautifulSoup object
        Includes retry logic and error handling
        """
        for attempt in range(retries):
            try:
                logger.info(f"Fetching: {url} (Attempt {attempt + 1}/{retries})")
                
                response = self.session.get(
                    url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                # Random delay to be polite
                time.sleep(random.uniform(1, 3))
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    self.error_count += 1
                    return None
        
        return None
    
    def extract_text(self, element, default: str = "") -> str:
        """Safely extract text from BeautifulSoup element"""
        if element:
            return element.get_text(strip=True)
        return default
    
    def extract_link(self, element, base_url: str = "") -> Optional[str]:
        """Extract and normalize link from element"""
        if not element:
            return None
        
        href = element.get('href', '')
        if not href:
            return None
        
        # Make absolute URL
        if href.startswith('http'):
            return href
        elif href.startswith('/'):
            return base_url.rstrip('/') + href
        else:
            return base_url.rstrip('/') + '/' + href
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep Arabic
        # Keep alphanumeric, Arabic, spaces, and common punctuation
        
        return text.strip()
    
    def is_saudi_project(self, text: str) -> bool:
        """Check if text mentions Saudi Arabia"""
        saudi_keywords = [
            'saudi', 'saudi arabia', 'ksa', 'riyadh', 'jeddah', 'mecca',
            'السعودية', 'المملكة', 'الرياض', 'جدة', 'مكة'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in saudi_keywords)
    
    def get_scraping_summary(self) -> Dict[str, Any]:
        """Get summary of scraping operation"""
        return {
            'source_name': self.source_name,
            'source_type': self.source_type,
            'scraped_count': self.scraped_count,
            'error_count': self.error_count,
            'timestamp': datetime.utcnow().isoformat()
        }
