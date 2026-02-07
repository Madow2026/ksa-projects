"""
Google News RSS Scraper - TRUSTED SOURCE ONLY
Uses Google News RSS to discover Saudi construction project news from verified sources
"""

import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
import time
import requests
from bs4 import BeautifulSoup

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


class GoogleNewsRSSScraper:
    """
    Google News RSS-based scraper for Saudi project discovery
    ONLY uses news aggregation, not raw web crawling
    """
    
    def __init__(self):
        self.name = "Google News RSS"
        self.source_type = "News Aggregator"
        self.scraped_count = 0
        
        # Search queries (English + Arabic)
        self.search_queries_en = [
            "Saudi Arabia construction project awarded",
            "Saudi Arabia infrastructure project under construction",
            "Saudi Arabia mega project commencement",
            "NEOM project construction Saudi Arabia",
            "Qiddiya project Saudi Arabia",
            "Red Sea project Saudi Arabia",
            "Saudi Vision 2030 project construction"
        ]
        
        self.search_queries_ar = [
            "مشروع تحت التنفيذ السعودية",
            "بدء تنفيذ مشروع السعودية",
            "ترسية مشروع السعودية",
            "مشروع إنشائي السعودية",
            "مشروع نيوم",
            "مشروع القدية",
            "مشروع البحر الأحمر"
        ]
        
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape Google News RSS feeds for Saudi project news"""
        logger.info("Starting Google News RSS scraping...")
        all_articles = []
        
        # Search English queries
        for query in self.search_queries_en:
            logger.info(f"Searching: {query}")
            articles = self._search_google_news(query, lang='en')
            all_articles.extend(articles)
            time.sleep(2)  # Rate limiting
        
        # Search Arabic queries
        for query in self.search_queries_ar:
            logger.info(f"Searching: {query}")
            articles = self._search_google_news(query, lang='ar')
            all_articles.extend(articles)
            time.sleep(2)  # Rate limiting
        
        logger.info(f"Total articles found from Google News RSS: {len(all_articles)}")
        return all_articles
    
    def _search_google_news(self, query: str, lang: str = 'en') -> List[Dict[str, Any]]:
        """
        Search Google News RSS feed for a specific query
        
        Args:
            query: Search query
            lang: Language (en or ar)
        """
        articles = []
        
        try:
            # Google News RSS URL
            base_url = "https://news.google.com/rss/search"
            
            params = {
                'q': query,
                'hl': lang,
                'gl': 'SA',  # Saudi Arabia
                'ceid': 'SA:ar' if lang == 'ar' else 'US:en'
            }
            
            # Build URL
            url = f"{base_url}?q={query}&hl={lang}&gl=SA&ceid={'SA:ar' if lang == 'ar' else 'US:en'}"
            
            logger.debug(f"Fetching RSS feed: {url}")
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            if not feed.entries:
                logger.warning(f"No entries found for query: {query}")
                return []
            
            logger.info(f"Found {len(feed.entries)} articles for: {query}")
            
            # Process each article
            for entry in feed.entries[:15]:  # Limit to 15 per query
                article = self._parse_rss_entry(entry, query, lang)
                if article:
                    articles.append(article)
                    self.scraped_count += 1
            
        except Exception as e:
            logger.error(f"Error searching Google News for '{query}': {e}")
        
        return articles
    
    def _parse_rss_entry(self, entry, query: str, lang: str) -> Optional[Dict[str, Any]]:
        """Parse a single RSS feed entry"""
        try:
            # Extract basic info
            title = entry.get('title', '')
            link = entry.get('link', '')
            published = entry.get('published', '')
            summary = entry.get('summary', '')
            source = entry.get('source', {}).get('title', 'Unknown Source')
            
            if not title or not link:
                return None
            
            # Try to fetch full article content
            full_text = self._fetch_article_content(link)
            
            # Combine text for AI extraction
            text = f"{title}\n\n{summary}\n\n{full_text}"
            
            return {
                'title': title,
                'url': link,
                'text': text,
                'source_type': 'News',
                'source_name': source,
                'published_date': self._parse_date(published),
                'language': lang,
                'search_query': query,
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None
    
    def _fetch_article_content(self, url: str) -> str:
        """
        Fetch full article content from URL
        Uses simple extraction to avoid blocking
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Try common article selectors
            article_selectors = [
                'article',
                'div.article-content',
                'div.article-body',
                'div.post-content',
                'div.entry-content',
                'div[itemprop="articleBody"]',
                'main'
            ]
            
            text = ""
            for selector in article_selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(separator='\n', strip=True)
                    break
            
            # Fallback: get all paragraphs
            if not text:
                paragraphs = soup.find_all('p')
                text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
            
            return text[:5000]  # Limit to 5000 chars
            
        except Exception as e:
            logger.warning(f"Could not fetch full content from {url}: {e}")
            return ""
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return None


# Global instance
google_news_scraper = GoogleNewsRSSScraper()
