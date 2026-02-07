"""
MEED Projects Scraper - TRUSTED CONSTRUCTION NEWS SOURCE
Scrapes project news from MEED (Middle East Economic Digest)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
import time
import requests
from bs4 import BeautifulSoup
import feedparser

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


class MEEDScraper:
    """
    MEED (Middle East Economic Digest) project news scraper
    TRUSTED SOURCE for construction & infrastructure projects
    """
    
    def __init__(self):
        self.name = "MEED Projects"
        self.source_type = "Construction News"
        self.scraped_count = 0
        
        # MEED RSS and URLs
        self.urls = [
            "https://www.meed.com/saudi-arabia",
            "https://www.meed.com/construction",
            "https://www.meed.com/projects"
        ]
        
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape MEED for Saudi project news"""
        logger.info("Starting MEED scraping...")
        all_articles = []
        
        for url in self.urls:
            logger.info(f"Scraping MEED: {url}")
            articles = self._scrape_url(url)
            all_articles.extend(articles)
            time.sleep(3)  # Rate limiting
        
        logger.info(f"Total articles from MEED: {len(all_articles)}")
        return all_articles
    
    def _scrape_url(self, url: str) -> List[Dict[str, Any]]:
        """Scrape MEED URL for articles"""
        articles = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # MEED article selectors
            article_elements = soup.select('article, div.article-card, div[class*="article"]')
            
            logger.info(f"Found {len(article_elements)} articles on {url}")
            
            for element in article_elements[:15]:
                article = self._parse_article(element, url)
                if article and self._is_saudi_related(article['text']):
                    articles.append(article)
                    self.scraped_count += 1
            
        except Exception as e:
            logger.error(f"Error scraping MEED {url}: {e}")
        
        return articles
    
    def _parse_article(self, element, base_url: str) -> Optional[Dict[str, Any]]:
        """Parse MEED article element"""
        try:
            # Extract title
            title_elem = element.select_one('h1, h2, h3, .title, .headline')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract link
            link_elem = element.select_one('a')
            link = ""
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if href.startswith('http'):
                    link = href
                elif href.startswith('/'):
                    link = f"https://www.meed.com{href}"
            
            # Extract summary
            summary_elem = element.select_one('p, .summary, .description')
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            if not title or len(title) < 10:
                return None
            
            # Fetch full article if we have a link
            full_text = ""
            if link:
                full_text = self._fetch_full_article(link)
            
            text = f"{title}\n\n{summary}\n\n{full_text}"
            
            return {
                'title': title,
                'url': link or base_url,
                'text': text,
                'source_type': 'Construction News',
                'source_name': 'MEED',
                'language': 'en',
                'reliability_score': 0.9,
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing MEED article: {e}")
            return None
    
    def _fetch_full_article(self, url: str) -> str:
        """Fetch full article content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for elem in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                elem.decompose()
            
            # Try article selectors
            article_elem = soup.select_one('article, div.article-content, div[class*="article-body"]')
            
            if article_elem:
                return article_elem.get_text(separator='\n', strip=True)[:5000]
            
            # Fallback
            paragraphs = soup.find_all('p')
            return '\n'.join([p.get_text(strip=True) for p in paragraphs])[:5000]
            
        except Exception as e:
            logger.warning(f"Could not fetch full article from {url}: {e}")
            return ""
    
    def _is_saudi_related(self, text: str) -> bool:
        """Check if article is related to Saudi Arabia"""
        text_lower = text.lower()
        keywords = [
            'saudi', 'arabia', 'riyadh', 'jeddah', 'makkah', 'mecca',
            'dammam', 'ksa', 'neom', 'qiddiya', 'red sea', 'vision 2030'
        ]
        return any(keyword in text_lower for keyword in keywords)


# Global instance
meed_scraper = MEEDScraper()
