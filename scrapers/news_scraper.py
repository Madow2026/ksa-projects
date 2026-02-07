"""
News Scraper for Saudi Projects
Scrapes construction and project news from various news sources
"""

from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import BaseScraper
from config import NEWS_SOURCES


class NewsScraper(BaseScraper):
    """Scraper for news websites"""
    
    def __init__(self):
        super().__init__("News Sources", "News")
        self.sources = NEWS_SOURCES
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape all configured news sources"""
        all_articles = []
        
        for source_url in self.sources:
            logger.info(f"Scraping news source: {source_url}")
            articles = self._scrape_source(source_url)
            all_articles.extend(articles)
        
        logger.info(f"Total articles scraped from news: {len(all_articles)}")
        return all_articles
    
    def _scrape_source(self, url: str) -> List[Dict[str, Any]]:
        """Scrape a single news source"""
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        articles = []
        
        # Generic selectors for articles (adapt based on site structure)
        article_selectors = [
            'article',
            'div.article',
            'div.post',
            'div.news-item',
            'div.story',
            'div[class*="article"]',
            'div[class*="post"]'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements[:20]:  # Limit to 20 per page
                    article = self._parse_article(element, url)
                    if article and self._is_relevant(article):
                        articles.append(article)
                        self.scraped_count += 1
                break
        
        return articles
    
    def _parse_article(self, element, base_url: str) -> Optional[Dict[str, Any]]:
        """Parse article element and extract data"""
        try:
            # Extract title
            title_element = element.select_one('h1, h2, h3, h4, .title, .headline')
            title = self.extract_text(title_element)
            
            if not title or len(title) < 10:
                return None
            
            # Extract link
            link_element = element.select_one('a')
            link = self.extract_link(link_element, base_url)
            
            # Extract description/snippet
            desc_element = element.select_one('p, .description, .excerpt, .summary')
            description = self.extract_text(desc_element)
            
            # Extract date if available
            date_element = element.select_one('time, .date, .published, .timestamp')
            date_str = self.extract_text(date_element)
            
            # Combine text for analysis
            full_text = f"{title} {description}"
            
            return {
                'title': self.clean_text(title),
                'description': self.clean_text(description),
                'url': link or base_url,
                'source_type': 'News',
                'published_date': date_str,
                'raw_text': full_text,
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return None
    
    def _is_relevant(self, article: Dict[str, Any]) -> bool:
        """Check if article is relevant to Saudi projects"""
        text = article.get('raw_text', '').lower()
        
        # Must mention Saudi Arabia
        if not self.is_saudi_project(text):
            return False
        
        # Must mention project-related keywords
        project_keywords = ['project', 'construction', 'development', 'building', 'contractor']
        if not any(keyword in text for keyword in project_keywords):
            return False
        
        return True


class GoogleNewsScraper(BaseScraper):
    """Scraper for Google News (simplified version)"""
    
    def __init__(self):
        super().__init__("Google News", "News")
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape Google News for Saudi project news
        Note: This is a simplified version. For production, consider using Google News API
        """
        articles = []
        
        # Search queries for Saudi projects
        queries = [
            "Saudi Arabia construction projects",
            "Saudi mega projects",
            "Riyadh development projects",
            "مشاريع السعودية",
            "مشاريع الرياض"
        ]
        
        for query in queries:
            logger.info(f"Searching Google News for: {query}")
            
            # Google News URL
            search_url = f"https://news.google.com/search?q={query.replace(' ', '+')}&hl=en-SA&gl=SA&ceid=SA:en"
            
            soup = self.fetch_page(search_url)
            if not soup:
                continue
            
            # Parse Google News results (structure may change)
            article_elements = soup.select('article')
            
            for element in article_elements[:10]:
                try:
                    title_elem = element.select_one('a')
                    if not title_elem:
                        continue
                    
                    title = self.extract_text(title_elem)
                    link = self.extract_link(title_elem, "https://news.google.com")
                    
                    if title and self.is_saudi_project(title):
                        articles.append({
                            'title': self.clean_text(title),
                            'description': '',
                            'url': link or search_url,
                            'source_type': 'News',
                            'raw_text': title,
                            'scraped_at': datetime.utcnow().isoformat()
                        })
                        self.scraped_count += 1
                        
                except Exception as e:
                    logger.error(f"Error parsing Google News article: {e}")
                    continue
        
        logger.info(f"Total articles from Google News: {len(articles)}")
        return articles
