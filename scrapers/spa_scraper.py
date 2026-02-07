"""
Saudi Press Agency (SPA) Scraper - OFFICIAL GOVERNMENT SOURCE
Scrapes official news from Saudi Arabia's state news agency (واس)
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


class SPAScraper:
    """
    Saudi Press Agency (SPA/واس) official news scraper
    HIGHEST RELIABILITY SOURCE - Government official announcements
    """
    
    def __init__(self):
        self.name = "Saudi Press Agency (SPA)"
        self.source_type = "Official Government"
        self.scraped_count = 0
        
        # SPA RSS feeds and URLs
        self.rss_feeds = [
            "https://www.spa.gov.sa/rss.php",  # Main RSS
        ]
        
        # SPA search URLs for projects
        self.search_urls = [
            "https://www.spa.gov.sa/search.php?q=مشروع",
            "https://www.spa.gov.sa/search.php?q=إنشاء",
            "https://www.spa.gov.sa/search.php?q=تنفيذ",
        ]
        
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape SPA for official project announcements"""
        logger.info("Starting Saudi Press Agency (SPA) scraping...")
        all_articles = []
        
        # Try RSS feeds first
        for rss_url in self.rss_feeds:
            logger.info(f"Fetching SPA RSS: {rss_url}")
            articles = self._scrape_rss(rss_url)
            all_articles.extend(articles)
            time.sleep(2)
        
        logger.info(f"Total articles found from SPA: {len(all_articles)}")
        return all_articles
    
    def _scrape_rss(self, rss_url: str) -> List[Dict[str, Any]]:
        """Scrape SPA RSS feed"""
        articles = []
        
        try:
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                logger.warning(f"No entries in SPA RSS feed")
                return []
            
            logger.info(f"Found {len(feed.entries)} SPA articles")
            
            for entry in feed.entries[:30]:  # Get more from official source
                # Filter for project-related news
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()
                
                # Arabic project keywords
                project_keywords = [
                    'مشروع', 'إنشاء', 'تنفيذ', 'بناء', 'تطوير',
                    'ترسية', 'افتتاح', 'تدشين', 'نيوم', 'القدية',
                    'البحر الأحمر', 'رؤية 2030', 'طريق', 'جسر',
                    'مطار', 'مشفى', 'مستشفى', 'مدرسة', 'جامعة'
                ]
                
                # Check if article is about projects
                if any(keyword in title or keyword in summary for keyword in project_keywords):
                    article = self._parse_rss_entry(entry)
                    if article:
                        articles.append(article)
                        self.scraped_count += 1
            
        except Exception as e:
            logger.error(f"Error scraping SPA RSS: {e}")
        
        return articles
    
    def _parse_rss_entry(self, entry) -> Optional[Dict[str, Any]]:
        """Parse SPA RSS entry"""
        try:
            title = entry.get('title', '')
            link = entry.get('link', '')
            published = entry.get('published', '')
            summary = entry.get('summary', '')
            
            if not title or not link:
                return None
            
            # Fetch full article
            full_text = self._fetch_spa_article(link)
            
            # Combine text
            text = f"{title}\n\n{summary}\n\n{full_text}"
            
            return {
                'title': title,
                'url': link,
                'text': text,
                'source_type': 'Official Government',
                'source_name': 'Saudi Press Agency (SPA)',
                'published_date': self._parse_date(published),
                'language': 'ar',
                'reliability_score': 1.0,  # Highest reliability
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing SPA entry: {e}")
            return None
    
    def _fetch_spa_article(self, url: str) -> str:
        """Fetch full SPA article content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # SPA-specific selectors
            article_selectors = [
                'div.article-content',
                'div.news-content',
                'div.content',
                'article',
                'div[class*="article"]'
            ]
            
            text = ""
            for selector in article_selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(separator='\n', strip=True)
                    break
            
            if not text:
                paragraphs = soup.find_all('p')
                text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
            
            return text[:5000]
            
        except Exception as e:
            logger.warning(f"Could not fetch SPA article from {url}: {e}")
            return ""
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string"""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return None


# Global instance
spa_scraper = SPAScraper()
