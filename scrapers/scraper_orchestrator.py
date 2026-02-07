"""
Web Scraper Orchestrator - REBUILT WITH TRUSTED SOURCES ONLY
Coordinates all scrapers using VERIFIED and RELIABLE sources
"""

from typing import List, Dict, Any
from datetime import datetime
from loguru import logger
import concurrent.futures

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.google_news_scraper import google_news_scraper
from scrapers.spa_scraper import spa_scraper


class ScraperOrchestrator:
    """
    Orchestrates all web scrapers using TRUSTED SOURCES ONLY
    
    Priority Order:
    1. Google News RSS (aggregated news from verified sources)
    2. Saudi Press Agency (official government - highest reliability)
    3. MEED (construction industry standard)
    4. Arabic News (trusted Saudi media: الاقتصادية، سبق، عكاظ)
    """
    
    def __init__(self):
        """Initialize all trusted scrapers"""
        self.scrapers = [
            google_news_scraper,
            spa_scraper
        ]
        
        logger.info(f"✅ Initialized {len(self.scrapers)} TRUSTED scrapers")
        logger.info("📋 Sources: Google News RSS (discovery-only), SPA (official)")
    
    def scrape_all(self, parallel: bool = False) -> List[Dict[str, Any]]:
        """
        Run all scrapers and collect results
        
        Args:
            parallel: Run scrapers in parallel (NOT recommended for rate limiting)
        
        Returns:
            List of all scraped items from trusted sources
        """
        logger.info("========== Starting Trusted Source Scraping ==========")
        start_time = datetime.utcnow()
        
        all_items = []
        
        if parallel:
            # Parallel execution (faster but may hit rate limits)
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = {executor.submit(scraper.scrape): scraper for scraper in self.scrapers}
                
                for future in concurrent.futures.as_completed(futures):
                    scraper = futures[future]
                    try:
                        items = future.result()
                        all_items.extend(items)
                        logger.info(f"✅ {scraper.name}: {len(items)} items")
                    except Exception as e:
                        logger.error(f"❌ {scraper.name} failed: {e}")
        else:
            # Sequential execution (safer for rate limiting)
            for scraper in self.scrapers:
                try:
                    logger.info(f"🔍 Running: {scraper.name}")
                    items = scraper.scrape()
                    all_items.extend(items)
                    logger.info(f"✅ {scraper.name}: {len(items)} items")
                except Exception as e:
                    logger.error(f"❌ {scraper.name} failed: {e}")
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info("========== Scraping Complete ==========")
        logger.info(f"📊 Total items collected: {len(all_items)}")
        logger.info(f"⏱️  Duration: {duration:.2f} seconds")
        
        # Log source breakdown
        self._log_source_breakdown(all_items)
        
        return all_items
    
    def _log_source_breakdown(self, items: List[Dict[str, Any]]):
        """Log breakdown by source"""
        sources = {}
        for item in items:
            source = item.get('source_name', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        logger.info("📈 Source Breakdown:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {source}: {count} items")


# Global orchestrator instance
scraper_orchestrator = ScraperOrchestrator()

