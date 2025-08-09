#!/usr/bin/env python3
"""
Setup script for Peer Review System
Initializes database, generates sample data, and trains models
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from data_generator import SyntheticDataGenerator
from database import DatabaseManager
from ml_pipeline import PeerReviewMLPipeline

def main():
    """Initialize the complete system"""
    print("🚀 Setting up Peer Review System...")
    
    # 1. Initialize database
    print("\n📊 Initializing database...")
    db = DatabaseManager()
    
    # 2. Generate synthetic data
    print("\n📁 Generating synthetic data...")
    generator = SyntheticDataGenerator(n_employees=20, n_days=60)
    df = generator.save_to_sqlite()
    print(f"✅ Generated {len(df)} reviews for {generator.n_employees} employees")
    
    # 3. Train ML models
    print("\n🤖 Training ML models...")
    pipeline = PeerReviewMLPipeline(db)
    
    # Get data and train
    reviews_df = db.get_reviews()
    features_df = pipeline.engineer_features(reviews_df)
    features_df = pipeline.train_models(features_df)
    pipeline.save_models()
    
    print("✅ Models trained and saved")
    
    # 4. Show summary
    stats = db.get_summary_stats()
    employees = db.get_employees()
    
    print("\n" + "="*50)
    print("🎉 SETUP COMPLETE!")
    print("="*50)
    print(f"📊 Total reviews: {stats['total_reviews']}")
    print(f"👥 Employees: {len(employees)}")
    print(f"📅 Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
    print(f"🤖 Models trained: {len(pipeline.models)}")
    
    print("\n🚀 Next steps:")
    print("1. Run: streamlit run streamlit_app/app.py")
    print("2. Navigate to http://localhost:8501")
    print("3. Explore the dashboard and submit reviews!")
    
    # Show sample insights
    print("\n📈 Sample Employee Insights:")
    for emp in employees[:3]:
        insights = pipeline.get_employee_insights(emp, days=14)
        print(f"  {emp}: Score {insights['avg_score']:.2f}, "
              f"Collab {insights['collaboration_rate']:.1%}, "
              f"Trend {insights.get('score_trend_7d', 0):.3f}")

if __name__ == "__main__":
    main()
