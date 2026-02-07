"""
Saudi Projects Intelligence Platform - Main Streamlit Dashboard
A modern, premium AI-powered web application for discovering active Saudi projects
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Dict, Any, List

# Page configuration
st.set_page_config(
    page_title="Saudi Projects Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import backend modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database.db_manager import db_manager
from data_processing.pipeline import data_pipeline
from ai_engine.nlp_engine import ai_engine
from config import (
    APP_TITLE, SAUDI_REGIONS, PROJECT_CATEGORIES,
    PROJECT_STATUS_OPTIONS, AUTO_REFRESH_ENABLED,
    REFRESH_INTERVAL_MINUTES
)

# Custom CSS for premium look
st.markdown("""
<style>
    /* Main theme */
    .main {
        background-color: #0e1117;
    }
    
    /* Headers */
    h1 {
        color: #00d4aa;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    h2, h3 {
        color: #e0e0e0;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Cards */
    .css-1r6slb0 {
        background-color: #1a1d24;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00d4aa 0%, #00a896 100%);
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 212, 170, 0.3);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #161a22;
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Status badges */
    .status-active {
        background-color: #00d4aa;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-ongoing {
        background-color: #4a90e2;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Confidence indicator */
    .confidence-high {
        color: #00d4aa;
        font-weight: 700;
    }
    
    .confidence-medium {
        color: #f39c12;
        font-weight: 600;
    }
    
    .confidence-low {
        color: #e74c3c;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = AUTO_REFRESH_ENABLED
    if 'pipeline_running' not in st.session_state:
        st.session_state.pipeline_running = False


def render_header():
    """Render the header section"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🏗️ Saudi Projects Intelligence Platform")
        st.markdown("*AI-Powered Active Projects Discovery & Intelligence*")
    
    with col2:
        st.markdown(f"**Last Updated:** {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M')}")
        if st.button("🔄 Refresh Data"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()


def render_kpi_cards():
    """Render KPI metric cards"""
    stats = db_manager.get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Active Projects",
            value=f"{stats['total_projects']:,}",
            delta=f"+{stats['new_this_month']} this month",
            delta_color="normal"
        )
    
    with col2:
        # Most active region
        if stats['projects_by_region']:
            top_region = max(stats['projects_by_region'], key=lambda x: x['count'])
            st.metric(
                label="🌍 Top Region",
                value=top_region['region'],
                delta=f"{top_region['count']} projects"
            )
        else:
            st.metric(label="🌍 Top Region", value="N/A")
    
    with col3:
        st.metric(
            label="✨ Avg Confidence",
            value=f"{stats['avg_confidence_score']:.1%}",
            help="AI confidence in data accuracy"
        )
    
    with col4:
        st.metric(
            label="🆕 New This Month",
            value=stats['new_this_month'],
            delta="Active discoveries"
        )


def render_charts(stats: Dict[str, Any]):
    """Render visualization charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Projects by Region")
        if stats['projects_by_region']:
            df_region = pd.DataFrame(stats['projects_by_region'])
            
            fig = px.bar(
                df_region,
                x='region',
                y='count',
                color='count',
                color_continuous_scale='Teal',
                labels={'count': 'Project Count', 'region': 'Region'},
                height=400
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#2a2e37')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available yet. Run the pipeline to collect projects.")
    
    with col2:
        st.subheader("🏢 Projects by Category")
        if stats['projects_by_category']:
            df_category = pd.DataFrame(stats['projects_by_category'])
            
            fig = px.pie(
                df_category,
                values='count',
                names='category',
                color_discrete_sequence=px.colors.sequential.Teal,
                height=400
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available yet.")


def render_filters() -> Dict[str, Any]:
    """Render filter sidebar and return selected filters"""
    st.sidebar.header("🔍 Filters")
    
    filters = {}
    
    # Region filter
    filters['region'] = st.sidebar.selectbox(
        "Region",
        options=["All"] + SAUDI_REGIONS,
        index=0
    )
    if filters['region'] == "All":
        filters['region'] = None
    
    # City filter
    filters['city'] = st.sidebar.text_input("City", placeholder="Enter city name...")
    if not filters['city']:
        filters['city'] = None
    
    # Category filter
    filters['category'] = st.sidebar.selectbox(
        "Category",
        options=["All"] + PROJECT_CATEGORIES,
        index=0
    )
    if filters['category'] == "All":
        filters['category'] = None
    
    # Contractor filter
    filters['contractor'] = st.sidebar.text_input("Contractor", placeholder="Search by contractor...")
    if not filters['contractor']:
        filters['contractor'] = None
    
    # Status filter
    filters['status'] = st.sidebar.selectbox(
        "Status",
        options=["All"] + PROJECT_STATUS_OPTIONS,
        index=0
    )
    if filters['status'] == "All":
        filters['status'] = None
    
    return filters


def format_confidence(confidence: float) -> str:
    """Format confidence score with color"""
    if confidence >= 0.8:
        color_class = "confidence-high"
        icon = "🟢"
    elif confidence >= 0.6:
        color_class = "confidence-medium"
        icon = "🟡"
    else:
        color_class = "confidence-low"
        icon = "🔴"
    
    return f'{icon} <span class="{color_class}">{confidence:.0%}</span>'


def render_projects_table(filters: Dict[str, Any]):
    """Render the main projects table"""
    st.subheader("📋 Active Projects")
    
    # Search bar
    search_term = st.text_input("🔎 Smart Search", placeholder="Search by project name, owner, contractor, or location...")
    
    # Get projects
    if search_term:
        projects = db_manager.search_projects(search_term)
    else:
        projects = db_manager.get_all_projects(
            region=filters.get('region'),
            city=filters.get('city'),
            category=filters.get('category'),
            contractor=filters.get('contractor'),
            status=filters.get('status'),
            limit=500
        )
    
    if not projects:
        st.markdown(
            \"\"\"
            <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #1e3a5f 0%, #2a5298 100%); border-radius: 10px; margin: 20px 0;'>
                <h3 style='color: #ffd700;'>🎯 No Projects Found!</h3>
                <p style='color: #e0e0e0; font-size: 16px; margin: 20px 0;'>
                    Get started by generating demo data or running the scraper
                </p>
                <div style='display: flex; justify-content: center; gap: 20px; margin-top: 20px;'>
                    <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;'>
                        <p style='color: #4CAF50; font-size: 18px; margin: 0;'>\u261d\ufe0f Step 1</p>
                        <p style='color: #e0e0e0; margin: 5px 0;'>Click "Generate Demo Projects"</p>
                    </div>
                    <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;'>
                        <p style='color: #2196F3; font-size: 18px; margin: 0;'>\u270c\ufe0f Step 2</p>
                        <p style='color: #e0e0e0; margin: 5px 0;'>Explore dashboard & analytics</p>
                    </div>
                </div>
            </div>
            \"\"\",
            unsafe_allow_html=True
        )
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(projects)
    
    # Display count
    st.markdown(f"**Found {len(df)} projects**")
    
    # Format columns for display
    display_columns = [
        'project_name', 'status', 'region', 'city', 'category',
        'project_owner', 'main_contractor', 'confidence_score'
    ]
    
    # Filter existing columns
    display_columns = [col for col in display_columns if col in df.columns]
    df_display = df[display_columns].copy()
    
    # Rename columns
    df_display.columns = [
        'Project Name', 'Status', 'Region', 'City', 'Category',
        'Owner', 'Contractor', 'Confidence'
    ]
    
    # Format confidence as percentage
    if 'Confidence' in df_display.columns:
        df_display['Confidence'] = df_display['Confidence'].apply(lambda x: f"{x:.0%}")
    
    # Display table
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Export button
    if st.button("📥 Export to Excel"):
        # Create Excel file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saudi_projects_{timestamp}.xlsx"
        
        df_export = df.copy()
        df_export.to_excel(filename, index=False, engine='openpyxl')
        
        st.success(f"✅ Exported to {filename}")


def render_pipeline_control():
    """Render pipeline control section"""
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Data Pipeline")
    
    # Check if database has projects
    projects_count = len(db_manager.get_all_projects())
    
    if projects_count == 0:
        st.sidebar.warning("⚠️ No projects in database yet!")
        st.sidebar.info("👉 Generate demo data to test the platform")
    else:
        st.sidebar.success(f"✅ {projects_count} projects in database")
    
    # Add demo data button - prominently displayed
    if st.sidebar.button("📊 Generate 15 Demo Projects", 
                         disabled=st.session_state.pipeline_running,
                         type="primary",
                         use_container_width=True):
        with st.spinner("Generating demo data..."):
            try:
                from utils.demo_data import DemoDataGenerator
                generator = DemoDataGenerator()
                count = generator.generate_sample_projects(count=15)
                st.sidebar.success(f"✅ Generated {count} projects!")
                st.session_state.last_refresh = datetime.now()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Failed: {str(e)}")
                logger.error(f"Demo data generation failed: {e}")
    
    st.sidebar.markdown("---")
    
    # Run pipeline button
    if st.sidebar.button("🔍 Run Live Scraper", 
                         disabled=st.session_state.pipeline_running,
                         use_container_width=True):
        st.session_state.pipeline_running = True
        st.rerun()  # Trigger rerun to start streaming
    
    # Show last scraping logs
    st.sidebar.markdown("### Recent Activity")
    logs = db_manager.get_recent_scraping_logs(limit=5)
    
    if logs:
        for log in logs:
            with st.sidebar.expander(f"{log['source_type']} - {log['status']}"):
                st.caption(f"Time: {log['timestamp']}")
                st.caption(f"Found: {log['projects_found']}")
                st.caption(f"Added: {log['projects_added']}")
    else:
        st.sidebar.info("No recent activity")


def main():
    """Main application entry point"""
    # Initialize
    init_session_state()
    
    # Render header
    render_header()
    
    st.markdown("---")
    
    # Render KPI cards
    render_kpi_cards()
    
    st.markdown("---")
    
    # Get stats for charts
    stats = db_manager.get_dashboard_stats()
    
    # Render charts
    render_charts(stats)
    
    st.markdown("---")
    
    # Render filters (sidebar)
    filters = render_filters()
    
    # Render pipeline control (sidebar)
    render_pipeline_control()
    
    # Real-time streaming display if pipeline is running
    if st.session_state.pipeline_running:
        st.markdown("---")
        st.subheader("🔄 Live Project Discovery")
        st.info("🌐 Searching for projects from Saudi Arabian sources...")
        
        # Create placeholders
        status_container = st.empty()
        progress_bar = st.progress(0)
        projects_container = st.container()
        
        try:
            from data_processing.pipeline import DataPipeline
            pipeline = DataPipeline()
            
            discovered_projects = []
            total_discovered = 0
            
            # Stream results
            for result in pipeline.run_streaming_pipeline():
                # Update progress
                if result.get('scraped', 0) > 0:
                    progress = result.get('processed', 0) / result.get('scraped', 1)
                    progress_bar.progress(min(progress, 1.0))
                else:
                    # Still searching
                    progress_bar.progress(0.1)
                
                # Update status metrics
                with status_container.container():
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("🔍 Found", result.get('scraped', 0))
                    col2.metric("✅ Added", result.get('added', 0))
                    col3.metric("🔄 Updated", result.get('updated', 0))
                    col4.metric("❌ Rejected", result.get('rejected', 0))
                
                # Display new project immediately
                if result.get('project'):
                    proj = result['project']
                    discovered_projects.append(proj)
                    total_discovered += 1
                    
                    with projects_container:
                        # Clear and show latest 5 discoveries
                        st.markdown(f"### 🎯 Latest Discoveries (Total: {total_discovered})")
                        for idx, p in enumerate(reversed(discovered_projects[-5:]), 1):
                            status_emoji = "✨" if p.get('status_type') == 'new' else "🔄"
                            with st.container():
                                st.markdown(f"**{idx}. {status_emoji} {p.get('project_name', 'Unknown')}**")
                                
                                col_a, col_b, col_c = st.columns(3)
                                col_a.text(f"📍 {p.get('region', 'N/A')}")
                                col_b.text(f"🏢 {p.get('project_owner', 'N/A')[:30]}")
                                col_c.text(f"💰 {p.get('project_value', 'N/A')}")
                                st.markdown("---")
                
                # Check completion
                if result.get('completed'):
                    progress_bar.progress(1.0)
                    
                    if result.get('added', 0) > 0:
                        st.success(f"🎉 Pipeline completed! Found {result.get('added', 0)} new projects in {result.get('duration', 0)}s")
                    else:
                        st.warning(f"⚠️ Pipeline completed but no new projects found. Duration: {result.get('duration', 0)}s")
                        st.info("💡 Tip: The scrapers search live websites. Try generating demo data for instant results!")
                    
                    st.session_state.pipeline_running = False
                    time.sleep(3)
                    st.rerun()
                    break
                
                # Check for errors
                if result.get('error'):
                    st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
                    st.session_state.pipeline_running = False
                    break
            
        except Exception as e:
            st.error(f"❌ Pipeline error: {str(e)}")
            logger.error(f"Streaming pipeline failed: {e}")
            st.session_state.pipeline_running = False
            st.info("💡 Try generating demo data instead for instant results!")
    
    # Render projects table
    render_projects_table(filters)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>Saudi Projects Intelligence Platform | Powered by AI & Advanced Web Scraping</p>
            <p>© 2026 | Built with Streamlit, OpenAI, and Python</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
