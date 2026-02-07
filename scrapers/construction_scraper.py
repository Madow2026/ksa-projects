"""
Construction & Project Websites Scraper
Scrapes dedicated construction and project listing websites
"""

from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import BaseScraper
from config import CONSTRUCTION_SOURCES


class ConstructionScraper(BaseScraper):
    """Scraper for construction and project websites"""
    
    def __init__(self):
        super().__init__("Construction Websites", "Website")
        self.sources = CONSTRUCTION_SOURCES
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape all construction websites"""
        all_projects = []
        
        for source_url in self.sources:
            logger.info(f"Scraping construction source: {source_url}")
            projects = self._scrape_source(source_url)
            all_projects.extend(projects)
        
        logger.info(f"Total projects scraped from construction sites: {len(all_projects)}")
        return all_projects
    
    def _scrape_source(self, url: str) -> List[Dict[str, Any]]:
        """Scrape a single construction website"""
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        projects = []
        
        # Selectors for project listings
        project_selectors = [
            'div.project',
            'div.project-item',
            'div.project-card',
            'div[class*="project"]',
            'article.project',
            'li.project'
        ]
        
        for selector in project_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements[:30]:  # Limit per page
                    project = self._parse_project(element, url)
                    if project and self._is_saudi_project_element(project):
                        projects.append(project)
                        self.scraped_count += 1
                break
        
        return projects
    
    def _parse_project(self, element, base_url: str) -> Optional[Dict[str, Any]]:
        """Parse project element"""
        try:
            # Project title/name
            title_element = element.select_one('h2, h3, h4, .title, .project-title, .name')
            title = self.extract_text(title_element)
            
            if not title or len(title) < 5:
                return None
            
            # Project link
            link_element = element.select_one('a')
            link = self.extract_link(link_element, base_url)
            
            # Project details
            details = {}
            
            # Try to find specific fields
            details_elements = element.select('.detail, .info, .meta, p, span')
            for detail_elem in details_elements:
                text = self.extract_text(detail_elem)
                if text:
                    # Parse common patterns
                    if 'location' in text.lower() or 'region' in text.lower():
                        details['location'] = text
                    elif 'value' in text.lower() or 'cost' in text.lower():
                        details['value'] = text
                    elif 'client' in text.lower() or 'owner' in text.lower():
                        details['owner'] = text
                    elif 'contractor' in text.lower():
                        details['contractor'] = text
            
            # Get all text for AI processing
            full_text = self.extract_text(element)
            
            return {
                'title': self.clean_text(title),
                'description': full_text[:500],
                'url': link or base_url,
                'source_type': 'Website',
                'raw_text': full_text,
                'extracted_details': details,
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing project: {e}")
            return None
    
    def _is_saudi_project_element(self, project: Dict[str, Any]) -> bool:
        """Check if project is Saudi-related"""
        text = project.get('raw_text', '').lower()
        return self.is_saudi_project(text)


class MEEDProjectsScraper(BaseScraper):
    """Specialized scraper for MEED Projects"""
    
    def __init__(self):
        super().__init__("MEED Projects", "Portal")
        self.base_url = "https://www.meedprojects.com"
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape MEED Projects for Saudi Arabia"""
        url = f"{self.base_url}/countries/saudi-arabia"
        
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        projects = []
        
        # MEED has structured project listings
        project_cards = soup.select('.project-card, .project-item, article')
        
        for card in project_cards[:50]:
            try:
                title_elem = card.select_one('h3, h4, .project-name')
                title = self.extract_text(title_elem)
                
                if not title:
                    continue
                
                # Extract other fields
                status_elem = card.select_one('.status, .project-status')
                status = self.extract_text(status_elem)
                
                value_elem = card.select_one('.value, .project-value')
                value = self.extract_text(value_elem)
                
                sector_elem = card.select_one('.sector, .category')
                sector = self.extract_text(sector_elem)
                
                link_elem = card.select_one('a')
                link = self.extract_link(link_elem, self.base_url)
                
                projects.append({
                    'title': self.clean_text(title),
                    'status': status,
                    'value': value,
                    'category': sector,
                    'url': link or url,
                    'source_type': 'Portal',
                    'raw_text': self.extract_text(card),
                    'scraped_at': datetime.utcnow().isoformat()
                })
                
                self.scraped_count += 1
                
            except Exception as e:
                logger.error(f"Error parsing MEED project: {e}")
                continue
        
        logger.info(f"Scraped {len(projects)} projects from MEED")
        return projects
