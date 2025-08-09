"""
Streamlit Web App for Peer Review System
Main application with review submission and dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from database import DatabaseManager
from ml_pipeline import PeerReviewMLPipeline
from llm_integration import LLMInsightsGenerator

# Configure Streamlit page
st.set_page_config(
    page_title="Peer Review System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'ml_pipeline' not in st.session_state:
    st.session_state.ml_pipeline = PeerReviewMLPipeline(st.session_state.db_manager)
    # Try to load existing models
    st.session_state.ml_pipeline.load_models()

if 'llm_generator' not in st.session_state:
    st.session_state.llm_generator = LLMInsightsGenerator()

# Sidebar navigation
st.sidebar.title("🎯 Peer Review System")
page = st.sidebar.selectbox(
    "Navigate to:",
    ["📝 Submit Review", "📊 Dashboard", "👤 Individual View", "🔧 Admin"]
)

# Main app
def main():
    if page == "📝 Submit Review":
        submit_review_page()
    elif page == "📊 Dashboard":
        dashboard_page()
    elif page == "👤 Individual View":
        individual_view_page()
    elif page == "🔧 Admin":
        admin_page()

def submit_review_page():
    """Page for submitting peer reviews"""
    st.title("📝 Submit Peer Review")
    st.markdown("Provide daily feedback for your teammates")
    
    # Get employee list
    employees = st.session_state.db_manager.get_employees()
    
    if not employees:
        st.warning("No employees found. Please run the data generator first or add employees in the Admin section.")
        return
    
    # Review form
    with st.form("review_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            reviewer = st.selectbox("You are:", employees, key="reviewer")
            reviewee = st.selectbox("Reviewing:", [emp for emp in employees if emp != reviewer])
        
        with col2:
            review_date = st.date_input("Date:", value=date.today())
        
        st.markdown("### Today, this person was...")
        descriptor = st.radio(
            "Select the descriptor that best fits:",
            options=["collaborative", "neutral", "withdrawn", "blocking"],
            format_func=lambda x: {
                "collaborative": "🤝 Collaborative - Actively working with others",
                "neutral": "😐 Neutral - Standard engagement level",
                "withdrawn": "😔 Withdrawn - Less engaged than usual",
                "blocking": "🚫 Blocking - Creating obstacles or friction"
            }[x],
            horizontal=True
        )
        
        # Optional score
        st.markdown("### Optional Detailed Score")
        score = st.slider("Overall performance today (1-5):", 1, 5, 3)
        
        # Optional comment
        comment = st.text_area("Optional comment:", placeholder="Any additional context or feedback...")
        
        # Submit button
        submitted = st.form_submit_button("Submit Review", type="primary")
        
        if submitted:
            success = st.session_state.db_manager.add_review(
                reviewer, reviewee, review_date, descriptor, score, comment
            )
            
            if success:
                st.success(f"✅ Review submitted for {reviewee}!")
                st.balloons()
            else:
                st.error("❌ Error submitting review. You may have already reviewed this person today.")

def dashboard_page():
    """Team dashboard with overview metrics"""
    st.title("📊 Team Dashboard")
    
    # Get data
    employees = st.session_state.db_manager.get_employees()
    if not employees:
        st.warning("No data available. Please submit some reviews first.")
        return
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date:", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date:", value=date.today())
    
    # Get reviews data
    reviews_df = st.session_state.db_manager.get_reviews(start_date, end_date)
    
    if reviews_df.empty:
        st.warning("No reviews found for the selected date range.")
        return
    
    # Overview metrics
    st.markdown("### 📈 Team Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_reviews = len(reviews_df)
        st.metric("Total Reviews", total_reviews)
    
    with col2:
        avg_score = reviews_df['score'].mean()
        st.metric("Average Score", f"{avg_score:.2f}")
    
    with col3:
        collaboration_rate = (reviews_df['descriptor'] == 'collaborative').mean()
        st.metric("Collaboration Rate", f"{collaboration_rate:.1%}")
    
    with col4:
        unique_days = reviews_df['date'].nunique()
        st.metric("Active Days", unique_days)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Score trends over time
        daily_scores = reviews_df.groupby('date')['score'].mean().reset_index()
        fig_trend = px.line(
            daily_scores, 
            x='date', 
            y='score',
            title="📈 Daily Average Scores",
            labels={'score': 'Average Score', 'date': 'Date'}
        )
        fig_trend.update_layout(height=400)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Descriptor distribution
        descriptor_counts = reviews_df['descriptor'].value_counts()
        fig_desc = px.pie(
            values=descriptor_counts.values,
            names=descriptor_counts.index,
            title="🎯 Behavior Distribution"
        )
        fig_desc.update_layout(height=400)
        st.plotly_chart(fig_desc, use_container_width=True)
    
    # Employee summary table
    st.markdown("### 👥 Employee Summary")
    
    employee_stats = []
    for emp in employees:
        emp_data = reviews_df[reviews_df['reviewee_id'] == emp]
        if len(emp_data) > 0:
            stats = {
                'Employee': emp,
                'Avg Score': emp_data['score'].mean(),
                'Reviews': len(emp_data),
                'Collaboration %': (emp_data['descriptor'] == 'collaborative').mean() * 100,
                'Last Review': emp_data['date'].max().strftime('%Y-%m-%d')
            }
            employee_stats.append(stats)
    
    if employee_stats:
        stats_df = pd.DataFrame(employee_stats)
        stats_df = stats_df.sort_values('Avg Score', ascending=False)
        
        # Format the dataframe for display
        stats_df_formatted = stats_df.copy()
        stats_df_formatted['Avg Score'] = stats_df_formatted['Avg Score'].round(2)
        stats_df_formatted['Collaboration %'] = (stats_df_formatted['Collaboration %'] * 100).round(1)
        
        st.dataframe(stats_df_formatted, use_container_width=True)

def individual_view_page():
    """Individual employee analysis page"""
    st.title("👤 Individual Analysis")
    
    employees = st.session_state.db_manager.get_employees()
    if not employees:
        st.warning("No employees found.")
        return
    
    # Employee selector
    selected_employee = st.selectbox("Select Employee:", employees)
    
    # Date range
    days_back = st.slider("Days to analyze:", 7, 60, 14)
    
    # Get employee insights
    try:
        insights = st.session_state.ml_pipeline.get_employee_insights(selected_employee, days_back)
        
        if 'error' in insights:
            st.warning(insights['error'])
            return
        
        # Display metrics
        st.markdown("### 📊 Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Average Score", 
                f"{insights['avg_score']:.2f}",
                delta=f"{insights['score_trend_7d']:.3f}" if insights['score_trend_7d'] != 0 else None
            )
        
        with col2:
            composite = insights.get('composite_score', 0)
            st.metric("Composite Score", f"{composite:.2f}")
        
        with col3:
            st.metric("Collaboration Rate", f"{insights['collaboration_rate']:.1%}")
        
        with col4:
            st.metric("Total Reviews", insights['total_reviews'])
        
        # Anomaly alert
        if insights.get('is_anomaly', False):
            st.error("⚠️ Anomaly detected - unusual patterns in recent behavior")
        
        # Get detailed review data for visualization
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        reviews_df = st.session_state.db_manager.get_reviews(
            start_date=start_date, 
            reviewee_id=selected_employee
        )
        
        if not reviews_df.empty:
            # Daily score trend
            daily_scores = reviews_df.groupby('date')['score'].agg(['mean', 'count']).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_scores['date'],
                y=daily_scores['mean'],
                mode='lines+markers',
                name='Daily Average Score',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title=f"📈 Score Trend for {selected_employee}",
                xaxis_title="Date",
                yaxis_title="Score",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Behavior breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                behavior_counts = reviews_df['descriptor'].value_counts()
                fig_behavior = px.bar(
                    x=behavior_counts.index,
                    y=behavior_counts.values,
                    title="🎭 Behavior Patterns",
                    labels={'x': 'Descriptor', 'y': 'Count'}
                )
                st.plotly_chart(fig_behavior, use_container_width=True)
            
            with col2:
                score_counts = reviews_df['score'].value_counts().sort_index()
                fig_scores = px.bar(
                    x=score_counts.index,
                    y=score_counts.values,
                    title="⭐ Score Distribution",
                    labels={'x': 'Score', 'y': 'Count'}
                )
                st.plotly_chart(fig_scores, use_container_width=True)
        
        # LLM Insights
        st.markdown("### 🤖 AI-Generated Insights")
        
        with st.spinner("Generating insights..."):
            llm_insights = st.session_state.llm_generator.generate_employee_insights(insights)
        
        if llm_insights.get('summary'):
            st.info(f"**Summary:** {llm_insights['summary']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if llm_insights.get('likely_causes'):
                st.markdown("**🔍 Likely Causes:**")
                st.write(llm_insights['likely_causes'])
            
            if llm_insights.get('manager_actions'):
                st.markdown("**👔 Manager Actions:**")
                st.write(llm_insights['manager_actions'])
        
        with col2:
            if llm_insights.get('peer_actions'):
                st.markdown("**🤝 Peer Actions:**")
                st.write(llm_insights['peer_actions'])
            
            if llm_insights.get('positive_aspects'):
                st.markdown("**✨ Positive Aspects:**")
                st.write(llm_insights['positive_aspects'])
    
    except Exception as e:
        st.error(f"Error generating insights: {e}")

def admin_page():
    """Admin page for data management"""
    st.title("🔧 Admin Panel")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Database Stats", "📁 Data Management", "🤖 Train Models", "⚙️ Settings"])
    
    with tab1:
        st.markdown("### Database Statistics")
        stats = st.session_state.db_manager.get_summary_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Reviews", stats['total_reviews'])
            st.metric("Unique Employees", stats['unique_employees'])
        
        with col2:
            if stats['date_range'][0]:
                st.metric("Date Range", f"{stats['date_range'][0]} to {stats['date_range'][1]}")
            st.metric("Avg Reviews/Day", f"{stats['avg_reviews_per_day']:.1f}")
    
    with tab2:
        st.markdown("### Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Generate Synthetic Data", type="primary"):
                with st.spinner("Generating synthetic data..."):
                    try:
                        from data_generator import SyntheticDataGenerator
                        generator = SyntheticDataGenerator(n_employees=20, n_days=60)
                        df = generator.save_to_sqlite()
                        st.success(f"✅ Generated {len(df)} reviews!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            if st.button("📤 Export Data"):
                try:
                    filepath = st.session_state.db_manager.export_to_csv()
                    st.success(f"✅ Data exported to {filepath}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            # Add new employee
            st.markdown("**Add New Employee:**")
            new_emp_id = st.text_input("Employee ID:")
            if st.button("➕ Add Employee"):
                if new_emp_id:
                    success = st.session_state.db_manager.add_employee(new_emp_id)
                    if success:
                        st.success(f"✅ Added {new_emp_id}")
                    else:
                        st.error("Failed to add employee")
    
    with tab3:
        st.markdown("### Train ML Models")
        
        if st.button("🎯 Train Models", type="primary"):
            with st.spinner("Training models... This may take a minute."):
                try:
                    # Get data and train
                    df = st.session_state.db_manager.get_reviews()
                    
                    if len(df) == 0:
                        st.error("No data found. Generate synthetic data first.")
                    else:
                        features_df = st.session_state.ml_pipeline.engineer_features(df)
                        features_df = st.session_state.ml_pipeline.train_models(features_df)
                        st.session_state.ml_pipeline.save_models()
                        
                        st.success("✅ Models trained and saved successfully!")
                        
                        # Show sample predictions
                        employees = st.session_state.db_manager.get_employees()[:3]
                        st.markdown("**Sample Predictions:**")
                        
                        for emp in employees:
                            insights = st.session_state.ml_pipeline.get_employee_insights(emp)
                            st.write(f"**{emp}:** Score {insights['avg_score']:.2f}, Trend {insights.get('score_trend_7d', 0):.3f}")
                
                except Exception as e:
                    st.error(f"Training error: {e}")
        
        # Model status
        if st.session_state.ml_pipeline.models:
            st.success("✅ Models loaded and ready")
            st.write("Available models:", list(st.session_state.ml_pipeline.models.keys()))
        else:
            st.warning("⚠️ No trained models found")
    
    with tab4:
        st.markdown("### Settings")
        
        # LLM Settings
        st.markdown("**LLM Configuration:**")
        provider = st.selectbox("LLM Provider:", ["openai", "gemini", "fallback"])
        api_key = st.text_input("API Key:", type="password", 
                               help="Set your API key or use environment variables")
        
        if st.button("💾 Save LLM Settings"):
            st.session_state.llm_generator = LLMInsightsGenerator(provider, api_key)
            st.success("✅ LLM settings updated")

if __name__ == "__main__":
    main()
