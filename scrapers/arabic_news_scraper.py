"""
Trusted Arabic News Scrapers
Scrapes from reliable Saudi/Arab news sources: الاقتصادية، سبق، عكاظ
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


class ArabicNewsScraper:
    """
    Scraper for trusted Arabic news sources
    Sources: الاقتصادية, سبق, عكاظ, الشرق الأوسط
    """
    
    def __init__(self):
        self.name = "Arabic Trusted News"
        self.source_type = "Arabic News"
        self.scraped_count = 0
        
        # Trusted Arabic news sources
        self.sources = {
            'aleqt': {
                'name': 'الاقتصادية',
                'url': 'https://www.aleqt.com',
                'rss': 'https://www.aleqt.com/feeds/rss',
                'search_url': 'https://www.aleqt.com/search?q=مشروع'
            },
            'sabq': {
                'name': 'سبق',
                'url': 'https://sabq.org',
                'sections': [
                    'https://sabq.org/saudia/economy',
                    'https://sabq.org/saudia/projects'
                ]
            },
            'okaz': {
                'name': 'عكاظ',
                'url': 'https://www.okaz.com.sa',
                'sections': [
                    'https://www.okaz.com.sa/economy',
                    'https://www.okaz.com.sa/local'
                ]
            }
        }
        
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape all Arabic news sources"""
        logger.info("Starting Arabic news scraping...")
        all_articles = []
        
        # Scrape each source
        for source_key, source_info in self.sources.items():
            logger.info(f"Scraping {source_info['name']}...")
            articles = self._scrape_source(source_key, source_info)
            all_articles.extend(articles)
            time.sleep(3)  # Rate limiting
        
        logger.info(f"Total articles from Arabic news: {len(all_articles)}")
        return all_articles
    
    def _scrape_source(self, source_key: str, source_info: Dict) -> List[Dict[str, Any]]:
        """Scrape a specific Arabic news source"""
        articles = []
        
        try:
            # Try RSS if available
            if 'rss' in source_info:
                articles.extend(self._scrape_rss(source_info['rss'], source_info['name']))
            
            # Scrape sections
            if 'sections' in source_info:
                for section_url in source_info['sections']:
                    section_articles = self._scrape_section(section_url, source_info['name'])
                    articles.extend(section_articles)
                    time.sleep(2)
            
            # Try search URL
            if 'search_url' in source_info:
                search_articles = self._scrape_section(source_info['search_url'], source_info['name'])
                articles.extend(search_articles)
        
        except Exception as e:
            logger.error(f"Error scraping {source_info['name']}: {e}")
        
        return articles
    
    def _scrape_rss(self, rss_url: str, source_name: str) -> List[Dict[str, Any]]:
        """Scrape RSS feed"""
        articles = []
        
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:20]:
                title = entry.get('title', '').lower()
                
                # Filter for project keywords
                project_keywords = [
                    'مشروع', 'إنشاء', 'تنفيذ', 'بناء', 'تطوير',
                    'ترسية', 'نيوم', 'القدية', 'البحر الأحمر'
                ]
                
                if any(keyword in title for keyword in project_keywords):
                    article = self._parse_rss_entry(entry, source_name)
                    if article:
                        articles.append(article)
                        self.scraped_count += 1
        
        except Exception as e:
            logger.error(f"Error scraping RSS {rss_url}: {e}")
        
        return articles
    
    def _scrape_section(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """Scrape a news section page"""
        articles = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic article selectors
            article_elements = soup.select('article, div.article, div[class*="article"], div.news-item')
            
            for element in article_elements[:10]:
                article = self._parse_article(element, url, source_name)
                if article and self._is_project_related(article['title']):
                    articles.append(article)
                    self.scraped_count += 1
        
        except Exception as e:
            logger.error(f"Error scraping section {url}: {e}")
        
        return articles
    
    def _parse_rss_entry(self, entry, source_name: str) -> Optional[Dict[str, Any]]:
        """Parse RSS entry"""
        try:
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary = entry.get('summary', '')
            
            if not title or not link:
                return None
            
            # Fetch full article
            full_text = self._fetch_article(link)
            text = f"{title}\n\n{summary}\n\n{full_text}"
            
            return {
                'title': title,
                'url': link,
                'text': text,
                'source_type': 'Arabic News',
                'source_name': source_name,
                'language': 'ar',
                'reliability_score': 0.8,
                'scraped_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None
    
    def _parse_article(self, element, base_url: str, source_name: str) -> Optional[Dict[str, Any]]:
        """Parse article element"""
        try:
            # Extract title
            title_elem = element.select_one('h1, h2, h3, h4, .title')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract link
            link_elem = element.select_one('a')
            link = ""
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if href.startswith('http'):
                    link = href
                elif href.startswith('/'):
                    from urllib.parse import urljoin
                    link = urljoin(base_url, href)
            
            if not title or len(title) < 10:
                return None
            
            # Fetch full article
            full_text = self._fetch_article(link) if link else ""
            text = f"{title}\n\n{full_text}"
            
            return {
                'title': title,
                'url': link or base_url,
                'text': text,
                'source_type': 'Arabic News',
                'source_name': source_name,
                'language': 'ar',
                'reliability_score': 0.8,
                'scraped_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return None
    
    def _fetch_article(self, url: str) -> str:
        """Fetch full article content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for elem in soup(['script', 'style', 'nav', 'footer', 'header']):
                elem.decompose()
            
            article_elem = soup.select_one('article, div[class*="article"], div[class*="content"]')
            
            if article_elem:
                return article_elem.get_text(separator='\n', strip=True)[:5000]
            
            paragraphs = soup.find_all('p')
            return '\n'.join([p.get_text(strip=True) for p in paragraphs])[:5000]
        
        except Exception as e:
            logger.warning(f"Could not fetch article from {url}: {e}")
            return ""
    
    def _is_project_related(self, title: str) -> bool:
        """Check if title is project-related"""
        keywords = [
            'مشروع', 'إنشاء', 'تنفيذ', 'بناء', 'تطوير',
            'ترسية', 'افتتاح', 'تدشين', 'نيوم', 'القدية',
            'البحر الأحمر', 'رؤية', 'طريق', 'جسر'
        ]
        return any(keyword in title for keyword in keywords)


# Global instance
arabic_news_scraper = ArabicNewsScraper()
