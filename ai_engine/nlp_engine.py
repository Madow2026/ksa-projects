"""
AI Engine for Saudi Projects Intelligence Platform
Handles NLP, entity extraction, classification, and AI-powered analysis
"""

import re
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
from loguru import logger

# OpenAI for advanced NLP
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")

# Sentence transformers for semantic similarity
try:
    from sentence_transformers import SentenceTransformer, util
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Sentence transformers not available. Install with: pip install sentence-transformers")

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    OPENAI_API_KEY, AI_MODEL, AI_TEMPERATURE,
    PROJECT_KEYWORDS_EN, PROJECT_KEYWORDS_AR,
    ACTIVE_KEYWORDS, COMPLETED_KEYWORDS, CANCELLED_KEYWORDS,
    SAUDI_REGIONS, PROJECT_CATEGORIES, CONFIDENCE_WEIGHTS,
    get_source_reliability
)


class AIEngine:
    """AI Engine for intelligent project extraction and analysis"""
    
    def __init__(self):
        """Initialize AI Engine with models"""
        self.openai_client = None
        self.embedding_model = None
        
        # Initialize OpenAI if available
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
        
        # Initialize embedding model for similarity
        if TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
                logger.info("Embedding model initialized")
            except Exception as e:
                logger.error(f"Failed to initialize embedding model: {e}")
    
    def extract_project_info(self, text: str, source_url: str = "") -> Optional[Dict[str, Any]]:
        """
        Extract structured project information from unstructured text
        Uses AI (GPT) if available, falls back to rule-based extraction
        """
        if self.openai_client:
            return self._extract_with_ai(text, source_url)
        else:
            return self._extract_with_rules(text, source_url)
    
    def _extract_with_ai(self, text: str, source_url: str) -> Optional[Dict[str, Any]]:
        """Extract project information using OpenAI GPT"""
        try:
            prompt = f"""
You are an expert at extracting structured project information from text about construction and development projects in Saudi Arabia.

Extract the following information from the text below. If information is not found, use null.

Required fields:
- project_name: The official project name
- project_name_ar: Arabic name if mentioned
- status: One of [Active, Ongoing, Under Construction, Planning, Announced]
- project_owner: The client or owner
- main_contractor: The main contractor
- consultant: The consultant company
- region: Saudi region (Riyadh, Makkah, Eastern Province, etc.)
- city: Specific city
- category: One of [Residential, Commercial, Infrastructure, Industrial, Mega Project, Healthcare, Education, Transportation, Energy, Tourism, Sports & Entertainment, Government, Mixed-Use]
- description: Brief project description (max 200 words)
- start_date: Project start date if mentioned (ISO format YYYY-MM-DD)
- announcement_date: Announcement date if mentioned (ISO format)
- project_value: Project value/budget if mentioned
- project_size: Project size/area if mentioned

IMPORTANT RULES:
1. Only extract ACTIVE/ONGOING/UNDER CONSTRUCTION projects
2. REJECT if the project is COMPLETED, FINISHED, DELIVERED, or INAUGURATED
3. REJECT if the project is CANCELLED, SUSPENDED, or HALTED
4. The project MUST be in Saudi Arabia
5. Return JSON format only

Text:
{text[:3000]}

Return ONLY valid JSON with the extracted data, or {{"rejected": true, "reason": "explanation"}} if the project should be rejected.
"""
            
            response = self.openai_client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a construction project data extraction expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=AI_TEMPERATURE,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(result_text)
            
            # Check if rejected
            if result.get("rejected"):
                logger.info(f"Project rejected by AI: {result.get('reason')}")
                return None
            
            # Add source information
            result['source_url'] = source_url
            result['extracted_by'] = 'ai'
            
            return result
            
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            # Fallback to rule-based
            return self._extract_with_rules(text, source_url)
    
    def _extract_with_rules(self, text: str, source_url: str) -> Optional[Dict[str, Any]]:
        """Extract project information using rule-based NLP"""
        # Check if it's a completed/cancelled project (reject immediately)
        text_lower = text.lower()
        
        # Reject completed projects
        for keyword in COMPLETED_KEYWORDS:
            if keyword in text_lower:
                logger.info(f"Project rejected: Contains completed keyword '{keyword}'")
                return None
        
        # Reject cancelled projects
        for keyword in CANCELLED_KEYWORDS:
            if keyword in text_lower:
                logger.info(f"Project rejected: Contains cancelled keyword '{keyword}'")
                return None
        
        # Extract basic information
        project_info = {
            'project_name': self._extract_project_name(text),
            'status': self._classify_status(text),
            'region': self._extract_region(text),
            'city': self._extract_city(text),
            'category': self._classify_category(text),
            'project_owner': self._extract_entity(text, ['owner', 'client', 'developer']),
            'main_contractor': self._extract_entity(text, ['contractor', 'builder']),
            'consultant': self._extract_entity(text, ['consultant', 'designer', 'architect']),
            'description': text[:300],
            'source_url': source_url,
            'extracted_by': 'rules'
        }
        
        # Must have at least project name and region
        if not project_info['project_name'] or not project_info['region']:
            return None
        
        return project_info
    
    def _extract_project_name(self, text: str) -> str:
        """Extract project name from text"""
        # Look for patterns like "Project Name:", "the ... project", etc.
        patterns = [
            r"project[:\s]+([A-Z][^\n\r\.]+(?:project|Project))",
            r"([A-Z][^\n\r\.]+(?:Development|Complex|Tower|Center|City|Park))",
            r"the\s+([A-Z][^\n\r\.]+(?:project|Project))",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if len(name) > 10 and len(name) < 200:
                    return name
        
        # Fallback: use first sentence
        sentences = text.split('.')
        if sentences:
            return sentences[0][:100].strip()
        
        return "Unknown Project"
    
    def _classify_status(self, text: str) -> str:
        """Classify project status from text"""
        text_lower = text.lower()
        
        # Check for active keywords
        for keyword in ACTIVE_KEYWORDS:
            if keyword in text_lower:
                if "under construction" in text_lower:
                    return "Under Construction"
                elif "ongoing" in text_lower:
                    return "Ongoing"
                else:
                    return "Active"
        
        # Default for new projects
        return "Announced"
    
    def _extract_region(self, text: str) -> Optional[str]:
        """Extract Saudi region from text"""
        text_lower = text.lower()
        
        for region in SAUDI_REGIONS:
            if region.lower() in text_lower:
                return region
        
        return None
    
    def _extract_city(self, text: str) -> Optional[str]:
        """Extract city name from text"""
        # Common Saudi cities
        cities = [
            "Riyadh", "Jeddah", "Mecca", "Medina", "Dammam", "Khobar", "Dhahran",
            "Jubail", "Yanbu", "Tabuk", "Abha", "Khamis Mushait", "Najran",
            "Jazan", "Hail", "Buraydah", "Al Khobar", "Qatif", "Al Ahsa"
        ]
        
        text_lower = text.lower()
        for city in cities:
            if city.lower() in text_lower:
                return city
        
        return None
    
    def _classify_category(self, text: str) -> str:
        """Classify project category from text"""
        text_lower = text.lower()
        
        # Category keywords
        category_keywords = {
            "Residential": ["residential", "housing", "apartment", "villa", "homes"],
            "Commercial": ["commercial", "retail", "mall", "shopping", "office"],
            "Infrastructure": ["infrastructure", "road", "bridge", "highway", "railway", "metro"],
            "Industrial": ["industrial", "factory", "plant", "manufacturing"],
            "Mega Project": ["mega", "giga", "neom", "red sea", "qiddiya"],
            "Healthcare": ["hospital", "medical", "healthcare", "clinic"],
            "Education": ["school", "university", "education", "campus"],
            "Transportation": ["airport", "port", "station", "transport"],
            "Energy": ["energy", "power", "solar", "wind", "oil", "gas"],
            "Tourism": ["hotel", "resort", "tourism", "entertainment"],
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return "Commercial"  # Default
    
    def _extract_entity(self, text: str, entity_types: List[str]) -> Optional[str]:
        """Extract entity (company/organization) by type"""
        # Look for patterns like "contractor: Company Name" or "by Company Name"
        for entity_type in entity_types:
            patterns = [
                f"{entity_type}[:\s]+([A-Z][^\\n\\r\\.]+(?:Company|Corp|Ltd|Group|Contracting))",
                f"by\\s+([A-Z][^\\n\\r\\.]+(?:Company|Corp|Ltd|Group|Contracting))",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entity = match.group(1).strip()
                    if len(entity) > 5 and len(entity) < 150:
                        return entity
        
        return None
    
    def calculate_confidence_score(self, project_data: Dict[str, Any], 
                                   source_count: int = 1) -> float:
        """
        Calculate confidence score for a project based on multiple factors
        Returns a score between 0.0 and 1.0
        """
        scores = {}
        
        # 1. Source count score (more sources = higher confidence)
        scores['source_count'] = min(source_count / 5.0, 1.0)  # Max at 5 sources
        
        # 2. Data completeness score
        required_fields = ['project_name', 'status', 'region', 'category']
        optional_fields = ['project_owner', 'main_contractor', 'city', 'description', 
                          'start_date', 'project_value']
        
        filled_required = sum(1 for f in required_fields if project_data.get(f))
        filled_optional = sum(1 for f in optional_fields if project_data.get(f))
        
        completeness = (filled_required / len(required_fields)) * 0.7 + \
                       (filled_optional / len(optional_fields)) * 0.3
        scores['data_completeness'] = completeness
        
        # 3. Source reliability score
        source_url = project_data.get('source_url', '')
        scores['source_reliability'] = get_source_reliability(source_url)
        
        # 4. Recency score (newer = higher confidence)
        # If we have a timestamp, calculate recency
        scores['recency'] = 0.8  # Default good score
        
        # Calculate weighted average
        total_score = sum(
            scores[key] * CONFIDENCE_WEIGHTS[key]
            for key in scores.keys()
        )
        
        return round(total_score, 2)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts
        Returns a score between 0.0 and 1.0
        """
        if not self.embedding_model:
            # Fallback to simple similarity
            return self._simple_similarity(text1, text2)
        
        try:
            embeddings = self.embedding_model.encode([text1, text2])
            similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
            return round(similarity, 2)
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return self._simple_similarity(text1, text2)
    
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Simple word-based similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def is_duplicate(self, project1: Dict, project2: Dict, threshold: float = 0.85) -> bool:
        """
        Check if two projects are duplicates using semantic similarity
        """
        # Compare project names
        name_similarity = self.calculate_similarity(
            project1.get('project_name', ''),
            project2.get('project_name', '')
        )
        
        # If names are very similar, likely a duplicate
        if name_similarity > threshold:
            # Additional check: same region
            if project1.get('region') == project2.get('region'):
                return True
        
        return False
    
    def generate_project_summary(self, project_data: Dict[str, Any]) -> str:
        """Generate AI summary of project (if OpenAI available)"""
        if not self.openai_client:
            return self._generate_simple_summary(project_data)
        
        try:
            prompt = f"""
Summarize this Saudi Arabian construction project in 2-3 sentences:

Project: {project_data.get('project_name')}
Category: {project_data.get('category')}
Location: {project_data.get('city', '')}, {project_data.get('region')}
Owner: {project_data.get('project_owner', 'N/A')}
Contractor: {project_data.get('main_contractor', 'N/A')}
Status: {project_data.get('status')}
Description: {project_data.get('description', '')}

Write a professional summary suitable for a business intelligence dashboard.
"""
            
            response = self.openai_client.chat.completions.create(
                model=AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return self._generate_simple_summary(project_data)
    
    def _generate_simple_summary(self, project_data: Dict[str, Any]) -> str:
        """Generate simple rule-based summary"""
        name = project_data.get('project_name', 'Unknown Project')
        category = project_data.get('category', 'Project')
        region = project_data.get('region', 'Saudi Arabia')
        status = project_data.get('status', 'Active')
        
        return f"{name} is a {category.lower()} project located in {region}, currently {status.lower()}."


# Global AI engine instance
ai_engine = AIEngine()
