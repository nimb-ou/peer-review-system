"""
Enhanced Streamlit Web App for Peer Review System V2
Improved UX, realistic data, and advanced features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import sys
from pathlib import Path
import sqlite3

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from database import DatabaseManager
from ml_pipeline import PeerReviewMLPipeline
from llm_integration import LLMInsightsGenerator

# Configure Streamlit page
st.set_page_config(
    page_title="PeerPulse - Team Review System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .warning-message {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'ml_pipeline' not in st.session_state:
    st.session_state.ml_pipeline = PeerReviewMLPipeline(st.session_state.db_manager)
    st.session_state.ml_pipeline.load_models()

if 'llm_generator' not in st.session_state:
    st.session_state.llm_generator = LLMInsightsGenerator()

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'selected_employee' not in st.session_state:
    st.session_state.selected_employee = None

def get_employee_info():
    """Get enhanced employee information with names and departments"""
    conn = st.session_state.db_manager.get_connection()
    try:
        employees_df = pd.read_sql_query("""
            SELECT id, name, department, role, email 
            FROM employees 
            WHERE active != 0 OR active IS NULL
            ORDER BY name
        """, conn)
        return employees_df
    except:
        # Fallback to basic employee list
        employees = st.session_state.db_manager.get_employees()
        return pd.DataFrame([{'id': emp, 'name': emp, 'department': 'Unknown', 'role': 'Employee'} 
                           for emp in employees])
    finally:
        conn.close()

def render_onboarding():
    """Render user onboarding and role selection"""
    st.markdown('<h1 class="main-header">👥 Welcome to PeerPulse</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 Your AI-Powered Team Review System
    
    **PeerPulse** helps teams build stronger collaboration through:
    - ⚡ **Quick Daily Reviews** (30 seconds per person)
    - 🤖 **AI-Powered Insights** from behavioral patterns  
    - 📊 **Real-time Dashboards** for managers and individuals
    - 🔒 **Privacy-First** design with anonymization options
    """)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👤 Individual Contributor", use_container_width=True):
            st.session_state.user_role = "individual"
            st.rerun()
    
    with col2:
        if st.button("👔 Manager", use_container_width=True):
            st.session_state.user_role = "manager"
            st.rerun()
    
    with col3:
        if st.button("⚙️ Administrator", use_container_width=True):
            st.session_state.user_role = "admin"
            st.rerun()

def render_sidebar():
    """Enhanced sidebar with user context"""
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        if st.session_state.user_role:
            st.info(f"Role: {st.session_state.user_role.title()}")
            
            if st.button("🔄 Switch Role"):
                st.session_state.user_role = None
                st.rerun()
        
        # Role-based navigation
        if st.session_state.user_role == "individual":
            pages = {
                "📝 Submit Review": "submit_review",
                "📊 My Insights": "my_insights",
                "👥 Team Overview": "team_overview"
            }
        elif st.session_state.user_role == "manager":
            pages = {
                "📊 Team Dashboard": "team_dashboard", 
                "👤 Individual Reports": "individual_reports",
                "🎯 Team Insights": "team_insights",
                "📝 Submit Review": "submit_review"
            }
        else:  # admin
            pages = {
                "📊 System Overview": "system_overview",
                "👥 Team Dashboard": "team_dashboard",
                "👤 Individual Reports": "individual_reports", 
                "📝 Submit Review": "submit_review",
                "⚙️ Admin Panel": "admin_panel"
            }
        
        selected_page = st.radio("", list(pages.keys()), key="navigation")
        
        # Quick stats in sidebar
        st.divider()
        st.markdown("### 📈 Quick Stats")
        
        stats = st.session_state.db_manager.get_summary_stats()
        st.metric("Total Reviews", stats['total_reviews'])
        st.metric("Active Users", stats['unique_employees'])
        st.metric("Avg Daily Reviews", f"{stats['avg_reviews_per_day']:.0f}")
        
        return pages[selected_page]

def submit_review_page():
    """Enhanced review submission with better UX"""
    st.markdown("### 📝 Submit Daily Review")
    
    employees_df = get_employee_info()
    
    if employees_df.empty:
        st.error("No employees found. Please check the database.")
        return
    
    # Create name to ID mapping
    employee_options = {}
    for _, emp in employees_df.iterrows():
        display_name = f"{emp['name']} ({emp['department']})"
        employee_options[display_name] = emp['id']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Review Details")
        reviewer_display = st.selectbox(
            "You are:", 
            list(employee_options.keys()),
            key="reviewer_select"
        )
        reviewer_id = employee_options[reviewer_display]
        
        # Filter out self from reviewee options
        reviewee_options = {k: v for k, v in employee_options.items() if v != reviewer_id}
        
        reviewee_display = st.selectbox(
            "Reviewing:", 
            list(reviewee_options.keys()),
            key="reviewee_select"
        )
        reviewee_id = reviewee_options[reviewee_display]
        
        review_date = st.date_input("Date:", value=date.today())
    
    with col2:
        st.markdown("#### 🎭 Behavior Assessment")
        
        descriptor_options = {
            "🤝 Collaborative": "collaborative",
            "😐 Neutral": "neutral", 
            "😔 Withdrawn": "withdrawn",
            "🚫 Blocking": "blocking"
        }
        
        descriptor_display = st.radio(
            "Today, this person was:",
            list(descriptor_options.keys()),
            help="Select the behavior that best describes their interactions today"
        )
        descriptor = descriptor_options[descriptor_display]
        
        score = st.slider(
            "Overall performance (1-5):", 
            1, 5, 3,
            help="1 = Needs improvement, 5 = Exceptional"
        )
    
    st.markdown("#### 💬 Additional Context (Optional)")
    comment = st.text_area(
        "Comments:", 
        placeholder="Any specific examples or context that would help understand the rating...",
        height=100
    )
    
    # Submit button with better feedback
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("✅ Submit Review", type="primary", use_container_width=True):
            success = st.session_state.db_manager.add_review(
                reviewer_id, reviewee_id, review_date, descriptor, score, comment
            )
            
            if success:
                st.markdown("""
                <div class="success-message">
                    ✅ <strong>Review submitted successfully!</strong><br>
                    Thank you for contributing to team insights.
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
                
                # Show what was submitted
                reviewee_name = employees_df[employees_df['id'] == reviewee_id]['name'].iloc[0]
                st.info(f"📝 Recorded: {reviewee_name} was {descriptor} (Score: {score}/5)")
                
            else:
                st.markdown("""
                <div class="warning-message">
                    ⚠️ <strong>Could not submit review</strong><br>
                    You may have already reviewed this person today.
                </div>
                """, unsafe_allow_html=True)

def team_dashboard_page():
    """Enhanced team dashboard with better visualizations"""
    st.markdown("### 📊 Team Performance Dashboard")
    
    employees_df = get_employee_info()
    
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
    
    # Merge with employee names
    reviews_df = reviews_df.merge(
        employees_df[['id', 'name', 'department']], 
        left_on='reviewee_id', 
        right_on='id', 
        how='left'
    )
    
    # Overview metrics
    st.markdown("#### 📈 Team Overview")
    
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
        active_days = reviews_df['date'].nunique()
        st.metric("Active Days", active_days)
    
    # Department performance
    st.markdown("#### 🏢 Department Performance")
    
    dept_stats = reviews_df.groupby('department').agg({
        'score': ['mean', 'count'],
        'descriptor': lambda x: (x == 'collaborative').mean()
    }).round(2)
    
    dept_stats.columns = ['Avg Score', 'Review Count', 'Collaboration Rate']
    dept_stats['Collaboration Rate'] = (dept_stats['Collaboration Rate'] * 100).round(1)
    
    st.dataframe(dept_stats, use_container_width=True)
    
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
        # Department comparison
        dept_scores = reviews_df.groupby('department')['score'].mean().reset_index()
        fig_dept = px.bar(
            dept_scores,
            x='department',
            y='score',
            title="🏢 Average Score by Department",
            labels={'score': 'Average Score', 'department': 'Department'}
        )
        fig_dept.update_layout(height=400)
        st.plotly_chart(fig_dept, use_container_width=True)

def individual_reports_page():
    """Enhanced individual employee reports"""
    st.markdown("### 👤 Individual Performance Reports")
    
    employees_df = get_employee_info()
    
    # Employee selector with search
    employee_options = {}
    for _, emp in employees_df.iterrows():
        display_name = f"{emp['name']} ({emp['department']} - {emp['role']})"
        employee_options[display_name] = emp['id']
    
    selected_employee_display = st.selectbox(
        "Select Employee:",
        list(employee_options.keys()),
        key="individual_employee_select"
    )
    selected_employee_id = employee_options[selected_employee_display]
    
    # Date range
    days_back = st.slider("Days to analyze:", 7, 90, 30)
    
    # Get employee insights
    try:
        insights = st.session_state.ml_pipeline.get_employee_insights(selected_employee_id, days_back)
        
        if 'error' in insights:
            st.warning(insights['error'])
            return
        
        # Employee info header
        emp_info = employees_df[employees_df['id'] == selected_employee_id].iloc[0]
        
        st.markdown(f"""
        #### 👤 {emp_info['name']}
        **{emp_info['role']}** • **{emp_info['department']}** Department  
        *Analysis for last {days_back} days*
        """)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trend_indicator = "📈" if insights.get('score_trend_7d', 0) > 0 else "📉" if insights.get('score_trend_7d', 0) < 0 else "➡️"
            st.metric(
                "Average Score", 
                f"{insights['avg_score']:.2f}",
                delta=f"{insights.get('score_trend_7d', 0):.3f}",
                help="7-day trend"
            )
        
        with col2:
            st.metric("Collaboration Rate", f"{insights['collaboration_rate']:.1%}")
        
        with col3:
            st.metric("Total Reviews", insights['total_reviews'])
        
        with col4:
            composite = insights.get('composite_score', 0)
            st.metric("Composite Score", f"{composite:.2f}")
        
        # Anomaly alert
        if insights.get('is_anomaly', False):
            st.error("⚠️ **Anomaly Detected** - Unusual patterns in recent behavior require attention")
        
        # Detailed visualizations
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        reviews_df = st.session_state.db_manager.get_reviews(
            start_date=start_date, 
            reviewee_id=selected_employee_id
        )
        
        if not reviews_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Daily score trend
                daily_scores = reviews_df.groupby('date')['score'].agg(['mean', 'count']).reset_index()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily_scores['date'],
                    y=daily_scores['mean'],
                    mode='lines+markers',
                    name='Daily Average Score',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title=f"📈 Score Trend - {emp_info['name']}",
                    xaxis_title="Date",
                    yaxis_title="Score",
                    height=400,
                    yaxis=dict(range=[1, 5])
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Behavior breakdown
                behavior_counts = reviews_df['descriptor'].value_counts()
                
                fig_behavior = px.pie(
                    values=behavior_counts.values,
                    names=behavior_counts.index,
                    title="🎭 Behavior Distribution",
                    height=400
                )
                st.plotly_chart(fig_behavior, use_container_width=True)
        
        # AI Insights
        st.markdown("#### 🤖 AI-Generated Insights")
        
        with st.spinner("Generating personalized insights..."):
            llm_insights = st.session_state.llm_generator.generate_employee_insights(insights)
        
        if llm_insights.get('summary'):
            st.info(f"**📝 Summary:** {llm_insights['summary']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if llm_insights.get('likely_causes'):
                st.markdown("**🔍 Likely Causes:**")
                st.write(llm_insights['likely_causes'])
            
            if llm_insights.get('manager_actions'):
                st.markdown("**👔 Recommended Manager Actions:**")
                st.write(llm_insights['manager_actions'])
        
        with col2:
            if llm_insights.get('peer_actions'):
                st.markdown("**🤝 Recommended Peer Actions:**")
                st.write(llm_insights['peer_actions'])
            
            if llm_insights.get('positive_aspects'):
                st.markdown("**✨ Positive Aspects:**")
                st.write(llm_insights['positive_aspects'])
    
    except Exception as e:
        st.error(f"Error generating insights: {e}")

def admin_panel_page():
    """Enhanced admin panel"""
    st.markdown("### ⚙️ System Administration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 System Stats", "🔄 Data Management", "🤖 ML Operations", "⚙️ Settings"])
    
    with tab1:
        st.markdown("#### 📊 System Statistics")
        stats = st.session_state.db_manager.get_summary_stats()
        employees_df = get_employee_info()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Reviews", stats['total_reviews'])
            st.metric("Active Employees", len(employees_df))
        
        with col2:
            if stats['date_range'][0]:
                st.metric("Data Range", f"{stats['date_range'][0]} to {stats['date_range'][1]}")
            st.metric("Avg Reviews/Day", f"{stats['avg_reviews_per_day']:.1f}")
        
        with col3:
            # Calculate review completion rate
            total_possible = len(employees_df) * (len(employees_df) - 1) * stats.get('unique_days', 1)
            completion_rate = (stats['total_reviews'] / total_possible * 100) if total_possible > 0 else 0
            st.metric("Review Completion Rate", f"{completion_rate:.1f}%")
    
    with tab2:
        st.markdown("#### 🔄 Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Generate Enhanced Sample Data", type="primary"):
                with st.spinner("Generating enhanced data..."):
                    try:
                        # Import and run enhanced data generator
                        from enhanced_data_generator import EnhancedDataGenerator
                        generator = EnhancedDataGenerator(n_employees=25, n_days=90)
                        df = generator.save_enhanced_data()
                        st.success(f"✅ Generated {len(df)} enhanced reviews!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            if st.button("📤 Export All Data"):
                try:
                    filepath = st.session_state.db_manager.export_to_csv()
                    st.success(f"✅ Data exported to {filepath}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            st.markdown("**🆕 Add New Employee:**")
            new_name = st.text_input("Full Name:")
            new_dept = st.selectbox("Department:", 
                                   ['Engineering', 'Product', 'Design', 'Marketing', 'Sales', 'Operations'])
            new_role = st.text_input("Role:")
            
            if st.button("➕ Add Employee"):
                if new_name:
                    # Generate ID from name
                    import re
                    clean_name = re.sub(r'[^a-zA-Z]', '', new_name.lower())
                    new_id = f"emp_{clean_name[:10]}"
                    
                    success = st.session_state.db_manager.add_employee(new_id, new_name, new_dept, new_role)
                    if success:
                        st.success(f"✅ Added {new_name}")
                    else:
                        st.error("Failed to add employee")
    
    with tab3:
        st.markdown("#### 🤖 ML Model Operations")
        
        if st.button("🎯 Retrain All Models", type="primary"):
            with st.spinner("Training models... This may take a minute."):
                try:
                    df = st.session_state.db_manager.get_reviews()
                    
                    if len(df) == 0:
                        st.error("No data found. Generate data first.")
                    else:
                        features_df = st.session_state.ml_pipeline.engineer_features(df)
                        features_df = st.session_state.ml_pipeline.train_models(features_df)
                        st.session_state.ml_pipeline.save_models()
                        
                        st.success("✅ Models retrained successfully!")
                        
                        # Show model performance
                        employees = st.session_state.db_manager.get_employees()[:3]
                        st.markdown("**🎯 Model Performance Sample:**")
                        
                        for emp in employees:
                            insights = st.session_state.ml_pipeline.get_employee_insights(emp)
                            emp_name = employees_df[employees_df['id'] == emp]['name'].iloc[0] if not employees_df.empty else emp
                            st.write(f"• **{emp_name}:** Score {insights['avg_score']:.2f}, Trend {insights.get('score_trend_7d', 0):.3f}")
                
                except Exception as e:
                    st.error(f"Training error: {e}")
        
        # Model status
        if st.session_state.ml_pipeline.models:
            st.success("✅ Models loaded and operational")
            st.write("**Available models:**", list(st.session_state.ml_pipeline.models.keys()))
        else:
            st.warning("⚠️ No trained models found")
    
    with tab4:
        st.markdown("#### ⚙️ Application Settings")
        
        # LLM Settings
        st.markdown("**🤖 LLM Configuration:**")
        provider = st.selectbox("LLM Provider:", ["openai", "gemini", "fallback"])
        api_key = st.text_input("API Key:", type="password", 
                               help="Set your API key for enhanced insights")
        
        if st.button("💾 Save LLM Settings"):
            st.session_state.llm_generator = LLMInsightsGenerator(provider, api_key)
            st.success("✅ LLM settings updated")
        
        # Privacy settings
        st.markdown("**🔒 Privacy Settings:**")
        anonymize_data = st.checkbox("Anonymize employee names in exports")
        data_retention_days = st.number_input("Data retention (days):", min_value=30, max_value=365, value=90)
        
        if st.button("💾 Save Privacy Settings"):
            st.success("✅ Privacy settings saved")

def main():
    """Main application logic with role-based routing"""
    if not st.session_state.user_role:
        render_onboarding()
        return
    
    # Render sidebar and get selected page
    selected_page = render_sidebar()
    
    # Route to appropriate page
    if selected_page == "submit_review":
        submit_review_page()
    elif selected_page == "team_dashboard":
        team_dashboard_page()
    elif selected_page == "individual_reports":
        individual_reports_page()
    elif selected_page == "my_insights":
        # Individual view of their own data
        if 'selected_employee' not in st.session_state:
            st.session_state.selected_employee = st.session_state.db_manager.get_employees()[0]
        individual_reports_page()
    elif selected_page == "team_overview":
        team_dashboard_page()
    elif selected_page == "team_insights":
        team_dashboard_page()
    elif selected_page == "system_overview":
        team_dashboard_page()
    elif selected_page == "admin_panel":
        admin_panel_page()

if __name__ == "__main__":
    main()
