"""
Data Processing Pipeline for Saudi Projects Intelligence Platform
Orchestrates scraping, AI extraction, deduplication, and database storage
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from loguru import logger
import time

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.scraper_orchestrator import scraper_orchestrator
from ai_engine.nlp_engine import ai_engine
from database.db_manager import db_manager
from config import CONFIDENCE_THRESHOLD, get_source_reliability


class DataPipeline:
    """Main data processing pipeline"""
    
    def __init__(self):
        """Initialize pipeline"""
        self.scraped_count = 0
        self.processed_count = 0
        self.added_count = 0
        self.updated_count = 0
        self.rejected_count = 0
        self.error_count = 0
    
    def run_full_pipeline(self, parallel_scraping: bool = False) -> Dict[str, Any]:
        """
        Run the complete pipeline:
        1. Scrape data from sources
        2. Extract & classify with AI
        3. Deduplicate
        4. Store in database
        
        Returns:
            Summary statistics of the pipeline run
        """
        start_time = datetime.utcnow()
        logger.info("========== Starting Full Data Pipeline ==========")
        
        # Step 1: Scrape data
        logger.info("Step 1: Scraping data from sources...")
        scraped_items = scraper_orchestrator.scrape_all(parallel=parallel_scraping)
        self.scraped_count = len(scraped_items)
        logger.info(f"Scraped {self.scraped_count} items")
        
        # Log scraping operation
        db_manager.add_scraping_log({
            'source_type': 'All',
            'source_url': 'Multiple',
            'status': 'success',
            'projects_found': self.scraped_count,
            'projects_added': 0,  # Will update later
            'projects_updated': 0,
            'execution_time': 0
        })
        
        # Step 2: Process each item
        logger.info("Step 2: Processing items with AI...")
        for item in scraped_items:
            self._process_item(item)
        
        # Step 3: Update statistics
        logger.info("Step 3: Updating statistics...")
        self._update_statistics()
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        summary = {
            'scraped': self.scraped_count,
            'processed': self.processed_count,
            'added': self.added_count,
            'updated': self.updated_count,
            'rejected': self.rejected_count,
            'errors': self.error_count,
            'duration_seconds': round(duration, 2),
            'timestamp': end_time.isoformat()
        }
        
        logger.info("========== Pipeline Complete ==========")
        logger.info(f"Summary: {summary}")
        
        return summary
    
    def run_streaming_pipeline(self, parallel_scraping: bool = False):
        """
        Run pipeline with streaming results - yields each project as discovered
        
        Yields:
            Dict with project info and current stats
        """
        start_time = datetime.utcnow()
        logger.info("========== Starting Streaming Pipeline ==========")
        
        # Reset counters
        self.scraped_count = 0
        self.processed_count = 0
        self.added_count = 0
        self.updated_count = 0
        self.rejected_count = 0
        self.error_count = 0
        
        # Yield initial status
        yield {
            'searching': True,
            'scraped': 0,
            'processed': 0,
            'added': 0,
            'updated': 0,
            'rejected': 0,
            'project': None,
            'rejected_reason': None
        }
        
        try:
            # Step 1: Scrape data
            logger.info("Scraping data from sources...")
            scraped_items = scraper_orchestrator.scrape_all(parallel=parallel_scraping)
            self.scraped_count = len(scraped_items)
            logger.info(f"Found {self.scraped_count} items to process")
            
            # Step 2: Process each item and yield results
            for idx, item in enumerate(scraped_items, 1):
                try:
                    # Process the item
                    project_data, rejected_reason = self._process_item_with_return(item)
                    
                    if project_data:
                        # Yield the discovered project
                        yield {
                            'searching': idx < len(scraped_items),
                            'scraped': self.scraped_count,
                            'processed': idx,
                            'added': self.added_count,
                            'updated': self.updated_count,
                            'rejected': self.rejected_count,
                            'project': project_data,
                            'rejected_reason': None
                        }
                    else:
                        # Project was rejected
                        yield {
                            'searching': idx < len(scraped_items),
                            'scraped': self.scraped_count,
                            'processed': idx,
                            'added': self.added_count,
                            'updated': self.updated_count,
                            'rejected': self.rejected_count,
                            'project': None,
                            'rejected_reason': rejected_reason
                        }
                
                except Exception as e:
                    logger.error(f"Error processing item {idx}: {e}")
                    self.error_count += 1
            
            # Final update
            self._update_statistics()
            
            # Yield completion status
            duration = (datetime.utcnow() - start_time).total_seconds()
            yield {
                'searching': False,
                'completed': True,
                'scraped': self.scraped_count,
                'processed': self.processed_count,
                'added': self.added_count,
                'updated': self.updated_count,
                'rejected': self.rejected_count,
                'duration': round(duration, 2),
                'project': None,
                'rejected_reason': None
            }
            
            logger.info("========== Streaming Pipeline Complete ==========")
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            yield {
                'error': True,
                'message': str(e),
                'searching': False
            }
    
    def _process_item_with_return(self, item: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Process item and return project data if successful
        Similar to _process_item but returns the project data
        """
        try:
            source_url = item.get('url', '')
            source_type = item.get('source_type', 'Website')
            text = item.get('text', '')
            source_name = item.get('source_name')
            reliability_score = float(item.get('reliability_score') or get_source_reliability(source_url))
            official_source = bool(item.get('official_source', False))
            
            if not text:
                self.rejected_count += 1
                return None, "missing_text"
            
            # AI extraction
            project_data = ai_engine.extract_project_info(text, source_url)
            
            if not project_data:
                self.rejected_count += 1
                return None, "ai_or_rules_rejected"
            
            # Calculate confidence
            confidence = ai_engine.calculate_confidence_score(project_data)
            # Base confidence combines extractor confidence + source reliability
            base_confidence = max(0.0, min(1.0, (confidence * 0.7) + (reliability_score * 0.3)))
            project_data['confidence_score'] = base_confidence
            
            # If missing critical fields, keep but will be low confidence.
            # We only hard-reject when status is not active/ongoing/under construction.
            status = (project_data.get('status') or "").strip()
            if status not in ["Active", "Ongoing", "Under Construction"]:
                self.rejected_count += 1
                return None, f"inactive_status:{status or 'missing'}"

            # Ensure DB-required fields exist
            if not project_data.get('region'):
                project_data['region'] = "Unknown"
            if not project_data.get('category'):
                project_data['category'] = "Infrastructure"
            
            # Check for duplicates (semantic-ish by name)
            similar = db_manager.find_similar_projects(project_data.get('project_name', ''))
            
            if similar:
                # Update existing
                project_id = similar[0]['id']
                self._update_existing_project(project_id, project_data, source_url)
                self.updated_count += 1
                project_data['id'] = project_id
                project_data['status_type'] = 'updated'
                # Add/refresh source with reliability and title
                try:
                    db_manager.add_source(project_id, {
                        'source_url': source_url,
                        'source_type': source_type,
                        'source_title': item.get('title') or source_name,
                        'reliability_score': reliability_score
                    })
                except Exception:
                    pass

                # Update confidence based on source count + official
                self._recompute_confidence(project_id, official_source)
                return project_data, None
            else:
                # Add new
                project_id = self._add_new_project(project_data, source_url, source_type)
                if project_id:
                    self.added_count += 1
                    project_data['id'] = project_id
                    project_data['status_type'] = 'new'
                    # Add source metadata
                    try:
                        db_manager.add_source(project_id, {
                            'source_url': source_url,
                            'source_type': source_type,
                            'source_title': item.get('title') or source_name,
                            'reliability_score': reliability_score
                        })
                    except Exception:
                        pass

                    self._recompute_confidence(project_id, official_source)
                    return project_data, None
            
            self.processed_count += 1
            return None, "not_saved"
            
        except Exception as e:
            logger.error(f"Error processing item: {e}")
            self.error_count += 1
            return None, f"exception:{e}"

    def _recompute_confidence(self, project_id: int, official_source: bool):
        """Recompute confidence based on requested policy.

        - Official source => High
        - 2+ sources => Medium
        - 1 non-official source => Low
        """
        try:
            sources = db_manager.get_project_sources(project_id)
            source_count = len(sources)

            # Determine if any official/high-reliability source exists
            max_rel = max([s.get('reliability_score', 0.5) for s in sources], default=0.5)
            any_official = official_source or (max_rel >= 0.99)

            # Confidence bands
            if any_official:
                confidence = 0.92
                verified = True
            elif source_count >= 2:
                confidence = 0.78
                verified = True
            else:
                confidence = 0.62
                verified = False

            db_manager.update_project(project_id, {
                'confidence_score': confidence,
                'is_verified': verified
            })
        except Exception as e:
            logger.warning(f"Could not recompute confidence: {e}")
    
    def _process_item(self, item: Dict[str, Any]) -> Optional[int]:
        """
        Process a single scraped item:
        - Extract structured data with AI
        - Check for duplicates
        - Add or update in database
        
        Returns:
            Project ID if added/updated, None if rejected
        """
        try:
            # Get raw text
            raw_text = item.get('raw_text', item.get('description', ''))
            source_url = item.get('url', '')
            
            if not raw_text:
                logger.warning("No text to process, skipping")
                return None
            
            # Step 1: AI Extraction
            logger.debug(f"Extracting from: {item.get('title', 'Unknown')}")
            project_data = ai_engine.extract_project_info(raw_text, source_url)
            
            if not project_data:
                logger.info("Project rejected by AI extraction")
                self.rejected_count += 1
                return None
            
            self.processed_count += 1
            
            # Step 2: Check for duplicates
            existing_projects = db_manager.find_similar_projects(
                project_data.get('project_name', '')
            )
            
            if existing_projects:
                # Check if it's a duplicate using AI similarity
                for existing in existing_projects:
                    if ai_engine.is_duplicate(project_data, existing):
                        logger.info(f"Duplicate found: {project_data.get('project_name')}")
                        # Update existing project
                        project_id = existing['id']
                        self._update_existing_project(project_id, project_data, source_url)
                        self.updated_count += 1
                        return project_id
            
            # Step 3: Calculate confidence score
            confidence = ai_engine.calculate_confidence_score(project_data, source_count=1)
            project_data['confidence_score'] = confidence
            
            # Calculate data completeness
            project_data['data_completeness'] = self._calculate_completeness(project_data)
            
            # Step 4: Add to database if confidence is sufficient
            if confidence >= CONFIDENCE_THRESHOLD:
                project_id = self._add_new_project(project_data, source_url, item.get('source_type', 'Website'))
                if project_id:
                    self.added_count += 1
                    logger.info(f"Added project: {project_data.get('project_name')} (ID: {project_id})")
                    return project_id
            else:
                logger.info(f"Low confidence ({confidence}), skipping: {project_data.get('project_name')}")
                self.rejected_count += 1
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing item: {e}")
            self.error_count += 1
            return None
    
    def _add_new_project(self, project_data: Dict[str, Any], source_url: str, source_type: str) -> Optional[int]:
        """Add a new project to database"""
        try:
            # Prepare project data for database
            db_project_data = {
                'project_name': project_data.get('project_name', 'Unknown'),
                'project_name_ar': project_data.get('project_name_ar'),
                'status': project_data.get('status', 'Active'),
                'project_owner': project_data.get('project_owner'),
                'main_contractor': project_data.get('main_contractor'),
                'consultant': project_data.get('consultant'),
                'region': project_data.get('region', 'Unknown'),
                'city': project_data.get('city'),
                'category': project_data.get('category', 'Commercial'),
                'description': project_data.get('description'),
                'project_value': project_data.get('project_value'),
                'confidence_score': project_data.get('confidence_score', 0.0),
                'data_completeness': project_data.get('data_completeness', 0.0),
            }
            
            # Add project
            project_id = db_manager.add_project(db_project_data)
            
            if project_id:
                # Add source
                db_manager.add_source(project_id, {
                    'source_url': source_url,
                    'source_type': source_type,
                    'reliability_score': get_source_reliability(source_url)
                })
                
                # Add update log
                db_manager.add_update_log({
                    'project_id': project_id,
                    'update_type': 'created',
                    'field_changed': 'all',
                    'new_value': 'Project created',
                    'source_url': source_url
                })
            
            return project_id
            
        except Exception as e:
            logger.error(f"Error adding project to database: {e}")
            return None
    
    def _update_existing_project(self, project_id: int, new_data: Dict[str, Any], source_url: str):
        """Update an existing project with new information"""
        try:
            # Get existing project
            existing = db_manager.get_project_by_id(project_id)
            if not existing:
                return
            
            # Prepare updates (only update if new data is more complete)
            updates = {}
            
            # Update fields if they're empty in existing but present in new data
            fields_to_check = [
                'project_owner', 'main_contractor', 'consultant',
                'city', 'description', 'project_value', 'start_date'
            ]
            
            for field in fields_to_check:
                if not existing.get(field) and new_data.get(field):
                    updates[field] = new_data[field]
            
            # Always update last_updated
            if updates:
                db_manager.update_project(project_id, updates)
                
                # Add source if new
                db_manager.add_source(project_id, {
                    'source_url': source_url,
                    'source_type': new_data.get('source_type', 'Website'),
                    'reliability_score': 0.5
                })
                
                logger.info(f"Updated project {project_id} with {len(updates)} fields")
        
        except Exception as e:
            logger.error(f"Error updating project: {e}")
    
    def _calculate_completeness(self, project_data: Dict[str, Any]) -> float:
        """Calculate data completeness percentage"""
        fields = [
            'project_name', 'status', 'region', 'category',
            'project_owner', 'main_contractor', 'city',
            'description', 'start_date', 'project_value'
        ]
        
        filled = sum(1 for field in fields if project_data.get(field))
        return round(filled / len(fields), 2)
    
    def _update_statistics(self):
        """Update database statistics"""
        try:
            # This could update region statistics, etc.
            pass
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    def process_single_url(self, url: str, source_type: str = "Website") -> Optional[Dict[str, Any]]:
        """
        Process a single URL manually
        
        Args:
            url: URL to process
            source_type: Type of source (News, Website, etc.)
        
        Returns:
            Project data if successfully processed
        """
        try:
            from scrapers.base_scraper import BaseScraper
            
            # Create a temporary scraper
            scraper = BaseScraper("Manual", source_type)
            soup = scraper.fetch_page(url)
            
            if not soup:
                return None
            
            # Extract text
            text = soup.get_text()
            
            # Process with AI
            project_data = ai_engine.extract_project_info(text, url)
            
            if project_data:
                # Calculate confidence
                confidence = ai_engine.calculate_confidence_score(project_data)
                project_data['confidence_score'] = confidence
                
                # Add to database if sufficient confidence
                if confidence >= CONFIDENCE_THRESHOLD:
                    project_id = self._add_new_project(project_data, url, source_type)
                    project_data['id'] = project_id
                    return project_data
            
            return project_data
            
        except Exception as e:
            logger.error(f"Error processing URL: {e}")
            return None


# Global pipeline instance
data_pipeline = DataPipeline()
