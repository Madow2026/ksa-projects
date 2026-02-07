"""
Main Entry Point for Saudi Projects Intelligence Platform
Can be run directly or imported as a module
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import logger
from database.db_manager import db_manager
from data_processing.pipeline import data_pipeline
from utils.demo_data import DemoDataGenerator


def run_pipeline():
    """Run the data collection pipeline"""
    logger.info("Starting data collection pipeline...")
    summary = data_pipeline.run_full_pipeline(parallel_scraping=False)
    
    print("\n" + "="*50)
    print("Pipeline Execution Summary")
    print("="*50)
    print(f"Scraped:    {summary['scraped']}")
    print(f"Processed:  {summary['processed']}")
    print(f"Added:      {summary['added']}")
    print(f"Updated:    {summary['updated']}")
    print(f"Rejected:   {summary['rejected']}")
    print(f"Errors:     {summary['errors']}")
    print(f"Duration:   {summary['duration_seconds']:.2f} seconds")
    print("="*50)


def generate_demo_data():
    """Generate demo data"""
    logger.info("Generating demo data...")
    generator = DemoDataGenerator()
    count = generator.generate_sample_projects(count=15)
    
    print("\n" + "="*50)
    print(f"Demo Data Generated: {count} projects")
    print("="*50)


def show_stats():
    """Show database statistics"""
    stats = db_manager.get_dashboard_stats()
    
    print("\n" + "="*50)
    print("Database Statistics")
    print("="*50)
    print(f"Total Projects:     {stats['total_projects']}")
    print(f"New This Month:     {stats['new_this_month']}")
    print(f"Avg Confidence:     {stats['avg_confidence_score']:.1%}")
    print("\nProjects by Region:")
    for region in stats['projects_by_region'][:5]:
        print(f"  {region['region']}: {region['count']}")
    print("="*50)


def main():
    """Main entry point with CLI"""
    parser = argparse.ArgumentParser(
        description="Saudi Projects Intelligence Platform - CLI Tool"
    )
    
    parser.add_argument(
        'command',
        choices=['pipeline', 'demo', 'stats', 'web'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    if args.command == 'pipeline':
        run_pipeline()
    elif args.command == 'demo':
        generate_demo_data()
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'web':
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "app.py"]
        sys.exit(stcli.main())


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - show help
        print("\n" + "="*70)
        print("  Saudi Projects Intelligence Platform")
        print("  AI-Powered Active Projects Discovery System")
        print("="*70)
        print("\nUsage:")
        print("  python main.py <command>")
        print("\nCommands:")
        print("  web       - Launch Streamlit web dashboard")
        print("  pipeline  - Run data collection pipeline")
        print("  demo      - Generate demo data")
        print("  stats     - Show database statistics")
        print("\nExamples:")
        print("  python main.py web")
        print("  python main.py pipeline")
        print("  python main.py demo")
        print("="*70 + "\n")
    else:
        main()
