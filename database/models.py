"""
Database Models for Saudi Projects Intelligence Platform
Using SQLAlchemy ORM for database abstraction
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime,
    Text, ForeignKey, Boolean, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()


class ProjectStatus(str, enum.Enum):
    """Project Status Enumeration"""
    ACTIVE = "Active"
    ONGOING = "Ongoing"
    UNDER_CONSTRUCTION = "Under Construction"
    PLANNING = "Planning"
    ANNOUNCED = "Announced"


class ProjectCategory(str, enum.Enum):
    """Project Category Enumeration"""
    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    INFRASTRUCTURE = "Infrastructure"
    INDUSTRIAL = "Industrial"
    MEGA_PROJECT = "Mega Project"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    TRANSPORTATION = "Transportation"
    ENERGY = "Energy"
    TOURISM = "Tourism"
    SPORTS_ENTERTAINMENT = "Sports & Entertainment"
    GOVERNMENT = "Government"
    MIXED_USE = "Mixed-Use"


class SourceType(str, enum.Enum):
    """Source Type Enumeration"""
    NEWS = "News"
    LINKEDIN = "LinkedIn"
    MAPS = "Maps"
    WEBSITE = "Website"
    PRESS_RELEASE = "Press Release"
    PORTAL = "Portal"


class Project(Base):
    """Main Project Entity"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    project_name = Column(String(500), nullable=False, index=True)
    project_name_ar = Column(String(500))  # Arabic name if available
    status = Column(String(50), nullable=False, index=True)
    
    # Stakeholders
    project_owner = Column(String(300))  # Client
    main_contractor = Column(String(300), index=True)
    consultant = Column(String(300))
    
    # Location
    region = Column(String(100), nullable=False, index=True)
    city = Column(String(100), index=True)
    location_details = Column(Text)  # Additional location info
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Dates
    start_date = Column(DateTime)
    announcement_date = Column(DateTime)
    expected_completion_date = Column(DateTime)
    
    # Classification
    category = Column(String(100), nullable=False, index=True)
    sub_category = Column(String(100))
    
    # Project Details
    description = Column(Text)
    project_value = Column(String(100))  # e.g., "500 million SAR"
    project_size = Column(String(100))   # e.g., "50,000 sqm"
    
    # AI & Quality Metrics
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    is_verified = Column(Boolean, default=False)
    data_completeness = Column(Float, default=0.0)  # Percentage of filled fields
    
    # Metadata
    first_discovered = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    update_count = Column(Integer, default=0)
    
    # Relationships
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")
    update_logs = relationship("UpdateLog", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert project to dictionary"""
        return {
            'id': self.id,
            'project_name': self.project_name,
            'project_name_ar': self.project_name_ar,
            'status': self.status,
            'project_owner': self.project_owner,
            'main_contractor': self.main_contractor,
            'consultant': self.consultant,
            'region': self.region,
            'city': self.city,
            'location_details': self.location_details,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'announcement_date': self.announcement_date.isoformat() if self.announcement_date else None,
            'expected_completion_date': self.expected_completion_date.isoformat() if self.expected_completion_date else None,
            'category': self.category,
            'sub_category': self.sub_category,
            'description': self.description,
            'project_value': self.project_value,
            'project_size': self.project_size,
            'confidence_score': self.confidence_score,
            'is_verified': self.is_verified,
            'data_completeness': self.data_completeness,
            'first_discovered': self.first_discovered.isoformat() if self.first_discovered else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'update_count': self.update_count
        }


class Source(Base):
    """Source URLs for each project"""
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    source_url = Column(String(1000), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_title = Column(String(500))
    reliability_score = Column(Float, default=0.5)
    
    discovered_date = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship
    project = relationship("Project", back_populates="sources")


class Region(Base):
    """Saudi Arabia Regions Reference Table"""
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    region_name_en = Column(String(100), nullable=False, unique=True)
    region_name_ar = Column(String(100))
    region_code = Column(String(10))
    
    # Statistics (updated periodically)
    total_projects = Column(Integer, default=0)
    active_projects = Column(Integer, default=0)
    last_stats_update = Column(DateTime, default=datetime.utcnow)


class UpdateLog(Base):
    """Historical log of project updates"""
    __tablename__ = 'update_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    update_timestamp = Column(DateTime, default=datetime.utcnow)
    update_type = Column(String(50))  # 'created', 'updated', 'verified', 'merged'
    field_changed = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    source_url = Column(String(1000))
    
    # Relationship
    project = relationship("Project", back_populates="update_logs")


class ScrapingLog(Base):
    """Log of scraping operations"""
    __tablename__ = 'scraping_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    scrape_timestamp = Column(DateTime, default=datetime.utcnow)
    source_type = Column(String(50))
    source_url = Column(String(1000))
    
    status = Column(String(20))  # 'success', 'failed', 'partial'
    projects_found = Column(Integer, default=0)
    projects_added = Column(Integer, default=0)
    projects_updated = Column(Integer, default=0)
    
    error_message = Column(Text)
    execution_time = Column(Float)  # seconds
