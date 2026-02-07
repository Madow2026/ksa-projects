"""
Database Manager for Saudi Projects Intelligence Platform
Handles database connections, sessions, and operations
"""

from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database.models import Base, Project, Source, Region, UpdateLog, ScrapingLog
from config import DATABASE_URL, SAUDI_REGIONS


class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, database_url: str = DATABASE_URL):
        """Initialize database connection"""
        # Use StaticPool for SQLite to avoid threading issues
        if database_url.startswith('sqlite'):
            self.engine = create_engine(
                database_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool
            )
        else:
            self.engine = create_engine(database_url)
        
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create tables and initialize reference data"""
        Base.metadata.create_all(bind=self.engine)
        self._initialize_regions()
    
    def _initialize_regions(self):
        """Initialize Saudi regions if not exists"""
        with self.get_session() as session:
            existing_count = session.query(Region).count()
            if existing_count == 0:
                regions = [
                    Region(region_name_en=region, region_name_ar="")
                    for region in SAUDI_REGIONS
                ]
                session.add_all(regions)
                session.commit()
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # ==================== Project Operations ====================
    
    def add_project(self, project_data: Dict[str, Any]) -> Optional[int]:
        """Add a new project to database"""
        with self.get_session() as session:
            project = Project(**project_data)
            session.add(project)
            session.flush()
            return project.id
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict]:
        """Get project by ID"""
        with self.get_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            return project.to_dict() if project else None
    
    def get_all_projects(self, 
                         region: Optional[str] = None,
                         city: Optional[str] = None,
                         category: Optional[str] = None,
                         contractor: Optional[str] = None,
                         status: Optional[str] = None,
                         limit: int = 1000) -> List[Dict]:
        """Get all projects with optional filters"""
        with self.get_session() as session:
            query = session.query(Project)
            
            # Apply filters
            if region:
                query = query.filter(Project.region == region)
            if city:
                query = query.filter(Project.city == city)
            if category:
                query = query.filter(Project.category == category)
            if contractor:
                query = query.filter(Project.main_contractor.ilike(f"%{contractor}%"))
            if status:
                query = query.filter(Project.status == status)
            
            # Order by last updated (most recent first)
            query = query.order_by(Project.last_updated.desc())
            
            # Limit results
            projects = query.limit(limit).all()
            return [p.to_dict() for p in projects]
    
    def search_projects(self, search_term: str) -> List[Dict]:
        """Smart search across multiple fields"""
        with self.get_session() as session:
            search_pattern = f"%{search_term}%"
            projects = session.query(Project).filter(
                or_(
                    Project.project_name.ilike(search_pattern),
                    Project.project_owner.ilike(search_pattern),
                    Project.main_contractor.ilike(search_pattern),
                    Project.city.ilike(search_pattern),
                    Project.description.ilike(search_pattern)
                )
            ).order_by(Project.confidence_score.desc()).limit(100).all()
            
            return [p.to_dict() for p in projects]
    
    def update_project(self, project_id: int, updates: Dict[str, Any]) -> bool:
        """Update project fields"""
        with self.get_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            
            for key, value in updates.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            project.last_updated = datetime.utcnow()
            project.update_count += 1
            session.commit()
            return True
    
    def find_similar_projects(self, project_name: str, threshold: float = 0.8) -> List[Dict]:
        """Find projects with similar names (simple matching)"""
        with self.get_session() as session:
            # Simple similarity: check if 80% of words match
            projects = session.query(Project).filter(
                Project.project_name.ilike(f"%{project_name[:20]}%")
            ).all()
            return [p.to_dict() for p in projects]
    
    # ==================== Source Operations ====================
    
    def add_source(self, project_id: int, source_data: Dict[str, Any]) -> int:
        """Add a source URL to a project"""
        with self.get_session() as session:
            source = Source(project_id=project_id, **source_data)
            session.add(source)
            session.flush()
            return source.id
    
    def get_project_sources(self, project_id: int) -> List[Dict]:
        """Get all sources for a project"""
        with self.get_session() as session:
            sources = session.query(Source).filter(Source.project_id == project_id).all()
            return [{
                'id': s.id,
                'source_url': s.source_url,
                'source_type': s.source_type,
                'source_title': s.source_title,
                'reliability_score': s.reliability_score,
                'discovered_date': s.discovered_date.isoformat() if s.discovered_date else None
            } for s in sources]
    
    # ==================== Statistics ====================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get statistics for dashboard"""
        with self.get_session() as session:
            total_projects = session.query(func.count(Project.id)).scalar()
            
            # Projects by region
            projects_by_region = session.query(
                Project.region,
                func.count(Project.id).label('count')
            ).group_by(Project.region).all()
            
            # Projects by category
            projects_by_category = session.query(
                Project.category,
                func.count(Project.id).label('count')
            ).group_by(Project.category).all()
            
            # New projects this month
            first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
            new_this_month = session.query(func.count(Project.id)).filter(
                Project.first_discovered >= first_day_of_month
            ).scalar()
            
            # Average confidence score
            avg_confidence = session.query(func.avg(Project.confidence_score)).scalar() or 0.0
            
            # Top contractors
            top_contractors = session.query(
                Project.main_contractor,
                func.count(Project.id).label('count')
            ).filter(
                Project.main_contractor.isnot(None)
            ).group_by(Project.main_contractor).order_by(func.count(Project.id).desc()).limit(10).all()
            
            return {
                'total_projects': total_projects or 0,
                'projects_by_region': [{'region': r, 'count': c} for r, c in projects_by_region],
                'projects_by_category': [{'category': c, 'count': cnt} for c, cnt in projects_by_category],
                'new_this_month': new_this_month or 0,
                'avg_confidence_score': round(float(avg_confidence), 2),
                'top_contractors': [{'contractor': c, 'count': cnt} for c, cnt in top_contractors if c]
            }
    
    def get_region_stats(self) -> List[Dict]:
        """Get statistics per region"""
        with self.get_session() as session:
            stats = session.query(
                Project.region,
                func.count(Project.id).label('total'),
                func.avg(Project.confidence_score).label('avg_confidence')
            ).group_by(Project.region).all()
            
            return [{
                'region': region,
                'total_projects': total,
                'avg_confidence': round(float(avg_conf or 0), 2)
            } for region, total, avg_conf in stats]
    
    # ==================== Logging ====================
    
    def add_update_log(self, log_data: Dict[str, Any]) -> int:
        """Add an update log entry"""
        with self.get_session() as session:
            log = UpdateLog(**log_data)
            session.add(log)
            session.flush()
            return log.id
    
    def add_scraping_log(self, log_data: Dict[str, Any]) -> int:
        """Add a scraping log entry"""
        with self.get_session() as session:
            log = ScrapingLog(**log_data)
            session.add(log)
            session.flush()
            return log.id
    
    def get_recent_scraping_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent scraping logs"""
        with self.get_session() as session:
            logs = session.query(ScrapingLog).order_by(
                ScrapingLog.scrape_timestamp.desc()
            ).limit(limit).all()
            
            return [{
                'id': log.id,
                'timestamp': log.scrape_timestamp.isoformat() if log.scrape_timestamp else None,
                'source_type': log.source_type,
                'status': log.status,
                'projects_found': log.projects_found,
                'projects_added': log.projects_added,
                'projects_updated': log.projects_updated,
                'error_message': log.error_message
            } for log in logs]


# Global database manager instance
db_manager = DatabaseManager()
