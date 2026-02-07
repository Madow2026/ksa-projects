"""
Demo Data Generator for Saudi Projects Intelligence Platform
Creates sample projects for testing and demonstration
"""

from datetime import datetime, timedelta
import random
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import db_manager
from config import SAUDI_REGIONS, PROJECT_CATEGORIES, PROJECT_STATUS_OPTIONS


class DemoDataGenerator:
    """Generate demo project data"""
    
    def __init__(self):
        self.contractors = [
            "Saudi Binladin Group",
            "Al-Rashid Trading & Contracting Company",
            "Arabian Construction Company",
            "Saudi Oger Ltd.",
            "El Seif Engineering Contracting",
            "Nesma & Partners",
            "Shapoorji Pallonji Group",
            "Larsen & Toubro",
            "China State Construction Engineering Corporation",
            "Samsung C&T Corporation"
        ]
        
        self.owners = [
            "Ministry of Transport and Logistics",
            "Royal Commission for Riyadh City",
            "Public Investment Fund (PIF)",
            "Saudi Arabian Oil Company (Aramco)",
            "Ministry of Housing",
            "King Abdullah Financial District",
            "Red Sea Development Company",
            "NEOM",
            "Qiddiya Investment Company",
            "Saudi Electricity Company"
        ]
        
        self.consultants = [
            "Dar Al-Handasah",
            "Khatib & Alami",
            "Parsons Corporation",
            "Arup",
            "AECOM",
            "Atkins",
            "Jacobs Engineering",
            "WSP Global",
            "Hill International",
            "Mace Group"
        ]
        
        self.project_templates = [
            {
                'name': 'King Salman Park Development',
                'category': 'Mega Project',
                'description': 'One of the largest urban parks in the world, spanning 13.4 square kilometers in Riyadh.',
                'value': 'SAR 86 billion',
                'size': '13.4 million sqm'
            },
            {
                'name': 'Riyadh Metro Network',
                'category': 'Transportation',
                'description': 'A comprehensive metro system with 6 lines covering 176 kilometers.',
                'value': 'SAR 90 billion',
                'size': '176 km'
            },
            {
                'name': 'Jeddah Tower',
                'category': 'Mega Project',
                'description': 'The worlds tallest tower under construction in Jeddah.',
                'value': 'SAR 4.5 billion',
                'size': '1,000+ meters height'
            },
            {
                'name': 'King Abdullah Sports City Expansion',
                'category': 'Sports & Entertainment',
                'description': 'Expansion of sports facilities and entertainment venues.',
                'value': 'SAR 2.3 billion',
                'size': '500,000 sqm'
            },
            {
                'name': 'Red Sea Luxury Resort Development',
                'category': 'Tourism',
                'description': 'Luxury tourism project along the Red Sea coast with 50+ resorts.',
                'value': 'SAR 75 billion',
                'size': '28,000 sqkm'
            },
            {
                'name': 'Qiddiya Entertainment City',
                'category': 'Sports & Entertainment',
                'description': 'Major entertainment, sports, and cultural destination near Riyadh.',
                'value': 'SAR 30 billion',
                'size': '366 sqkm'
            },
            {
                'name': 'King Fahad Medical City Expansion',
                'category': 'Healthcare',
                'description': 'Expansion of one of the largest medical complexes in the region.',
                'value': 'SAR 5 billion',
                'size': '300,000 sqm'
            },
            {
                'name': 'Dammam Industrial City Phase 3',
                'category': 'Industrial',
                'description': 'Industrial zone development in the Eastern Province.',
                'value': 'SAR 8 billion',
                'size': '2 million sqm'
            },
            {
                'name': 'King Abdulaziz International Airport Expansion',
                'category': 'Transportation',
                'description': 'Major expansion to accommodate 80 million passengers annually.',
                'value': 'SAR 27 billion',
                'size': '15 sqkm'
            },
            {
                'name': 'Riyadh Green Project',
                'category': 'Infrastructure',
                'description': 'Initiative to plant 7.5 million trees across Riyadh.',
                'value': 'SAR 11 billion',
                'size': 'City-wide'
            }
        ]
    
    def generate_sample_projects(self, count: int = 15) -> int:
        """Generate sample projects in database"""
        logger.info(f"Generating {count} sample projects...")
        
        created_count = 0
        
        for i in range(count):
            # Select template or create random
            if i < len(self.project_templates):
                template = self.project_templates[i]
            else:
                template = random.choice(self.project_templates)
            
            # Create project
            project_data = {
                'project_name': template['name'] + (f" Phase {i+1}" if i >= len(self.project_templates) else ""),
                'status': random.choice(PROJECT_STATUS_OPTIONS),
                'project_owner': random.choice(self.owners),
                'main_contractor': random.choice(self.contractors),
                'consultant': random.choice(self.consultants),
                'region': random.choice(SAUDI_REGIONS),
                'city': self._get_city_for_region(random.choice(SAUDI_REGIONS)),
                'category': template['category'],
                'description': template['description'],
                'project_value': template.get('value', ''),
                'project_size': template.get('size', ''),
                'confidence_score': round(random.uniform(0.7, 0.98), 2),
                'data_completeness': round(random.uniform(0.7, 1.0), 2),
                'is_verified': random.choice([True, False]),
                'start_date': datetime.now() - timedelta(days=random.randint(30, 730)),
                'announcement_date': datetime.now() - timedelta(days=random.randint(1, 180))
            }
            
            try:
                project_id = db_manager.add_project(project_data)
                
                if project_id:
                    # Add sources
                    for j in range(random.randint(1, 3)):
                        db_manager.add_source(project_id, {
                            'source_url': f'https://example-source{j+1}.com/project/{project_id}',
                            'source_type': random.choice(['News', 'Website', 'Portal']),
                            'reliability_score': round(random.uniform(0.6, 0.95), 2)
                        })
                    
                    created_count += 1
                    logger.info(f"Created: {project_data['project_name']}")
            
            except Exception as e:
                logger.error(f"Error creating project: {e}")
        
        logger.info(f"Successfully created {created_count} sample projects")
        return created_count
    
    def _get_city_for_region(self, region: str) -> str:
        """Get a sample city for a region"""
        city_map = {
            'Riyadh': 'Riyadh',
            'Makkah': 'Jeddah',
            'Madinah': 'Medina',
            'Eastern Province': 'Dammam',
            'Asir': 'Abha',
            'Tabuk': 'Tabuk',
            'Qassim': 'Buraidah',
            "Ha'il": 'Hail',
            'Northern Borders': 'Arar',
            'Jazan': 'Jazan',
            'Najran': 'Najran',
            'Al-Bahah': 'Al-Bahah',
            'Al-Jawf': 'Sakaka'
        }
        return city_map.get(region, 'Riyadh')


def main():
    """Main entry point for demo data generation"""
    logger.info("===== Demo Data Generator =====")
    
    generator = DemoDataGenerator()
    count = generator.generate_sample_projects(count=15)
    
    logger.info(f"Demo data generation complete: {count} projects created")
    
    # Show stats
    stats = db_manager.get_dashboard_stats()
    logger.info(f"Total projects in database: {stats['total_projects']}")


if __name__ == "__main__":
    main()
