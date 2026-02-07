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
        st.info("No projects found matching the criteria. Run the data pipeline to discover projects.")
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
    
    if st.sidebar.button("▶️ Run Pipeline", disabled=st.session_state.pipeline_running):
        st.session_state.pipeline_running = True
        
        with st.spinner("Running data pipeline... This may take a few minutes."):
            try:
                # Run pipeline
                summary = data_pipeline.run_full_pipeline(parallel_scraping=False)
                
                # Show results
                st.success("✅ Pipeline completed successfully!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Scraped", summary['scraped'])
                    st.metric("Added", summary['added'])
                with col2:
                    st.metric("Updated", summary['updated'])
                    st.metric("Rejected", summary['rejected'])
                
                st.info(f"Duration: {summary['duration_seconds']:.2f} seconds")
                
                # Refresh data
                st.session_state.last_refresh = datetime.now()
                
            except Exception as e:
                st.error(f"❌ Pipeline failed: {str(e)}")
            
            finally:
                st.session_state.pipeline_running = False
                time.sleep(2)
                st.rerun()
    
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
