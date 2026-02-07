"""
Web Scraper Orchestrator
Coordinates all scrapers and manages the scraping pipeline
"""

from typing import List, Dict, Any
from datetime import datetime
from loguru import logger
import concurrent.futures

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.news_scraper import NewsScraper, GoogleNewsScraper
from scrapers.construction_scraper import ConstructionScraper, MEEDProjectsScraper
from config import (
    ENABLE_NEWS_SCRAPING,
    ENABLE_WEB_SCRAPING,
    MAX_CONCURRENT_REQUESTS
)


class ScraperOrchestrator:
    """Orchestrates all web scrapers"""
    
    def __init__(self):
        """Initialize all scrapers"""
        self.scrapers = []
        
        # Add enabled scrapers
        if ENABLE_NEWS_SCRAPING:
            self.scrapers.append(NewsScraper())
            self.scrapers.append(GoogleNewsScraper())
        
        if ENABLE_WEB_SCRAPING:
            self.scrapers.append(ConstructionScraper())
            self.scrapers.append(MEEDProjectsScraper())
        
        logger.info(f"Initialized {len(self.scrapers)} scrapers")
    
    def scrape_all(self, parallel: bool = False) -> List[Dict[str, Any]]:
        """
        Run all scrapers and collect results
        
        Args:
            parallel: Run scrapers in parallel (faster but more resource intensive)
        
        Returns:
            List of all scraped items
        """
        all_items = []
        start_time = datetime.utcnow()
        
        logger.info(f"Starting scraping operation with {len(self.scrapers)} scrapers")
        
        if parallel:
            # Run scrapers in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
                future_to_scraper = {
                    executor.submit(scraper.scrape): scraper
                    for scraper in self.scrapers
                }
                
                for future in concurrent.futures.as_completed(future_to_scraper):
                    scraper = future_to_scraper[future]
                    try:
                        items = future.result()
                        all_items.extend(items)
                        logger.info(f"{scraper.source_name}: {len(items)} items scraped")
                    except Exception as e:
                        logger.error(f"{scraper.source_name} failed: {e}")
        else:
            # Run scrapers sequentially
            for scraper in self.scrapers:
                try:
                    logger.info(f"Running scraper: {scraper.source_name}")
                    items = scraper.scrape()
                    all_items.extend(items)
                    logger.info(f"{scraper.source_name}: {len(items)} items scraped")
                except Exception as e:
                    logger.error(f"{scraper.source_name} failed: {e}")
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Scraping completed: {len(all_items)} items in {duration:.2f} seconds")
        
        return all_items
    
    def scrape_single(self, scraper_name: str) -> List[Dict[str, Any]]:
        """Run a single scraper by name"""
        for scraper in self.scrapers:
            if scraper.source_name.lower() == scraper_name.lower():
                logger.info(f"Running single scraper: {scraper_name}")
                return scraper.scrape()
        
        logger.warning(f"Scraper not found: {scraper_name}")
        return []
    
    def get_scraper_status(self) -> List[Dict[str, Any]]:
        """Get status of all scrapers"""
        return [
            {
                'name': scraper.source_name,
                'type': scraper.source_type,
                'scraped_count': scraper.scraped_count,
                'error_count': scraper.error_count
            }
            for scraper in self.scrapers
        ]


# Global orchestrator instance
scraper_orchestrator = ScraperOrchestrator()
