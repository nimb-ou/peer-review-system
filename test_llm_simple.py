#!/usr/bin/env python3
"""
Simple LLM API Test for PeerPulse
Quick test of LLM integration with sample data
"""

import os
import sys
sys.path.append('src')

from llm_integration import LLMInsightsGenerator
from database import DatabaseManager
import pandas as pd

def test_with_real_employee():
    """Test with a real employee from our database"""
    print("🔍 Testing LLM API with Real Employee Data")
    print("=" * 50)
    
    # Get a real employee from our V2.0 database
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        
        # Get employees from the database
        employees_df = pd.read_sql('SELECT name FROM employees LIMIT 5', conn)
        
        if employees_df.empty:
            print("❌ No employees found. Run setup first: python scripts/setup.py")
            return
        
        first_employee = employees_df.iloc[0]['name']
        print(f"📝 Testing with employee: {first_employee}")
        
        # Create sample data based on our V2.0 structure
        sample_data = {
            'employee_id': first_employee,
            'avg_score': 3.2,
            'composite_score': 3.1,
            'collaboration_rate': 0.65,  # 65% collaborative feedback
            'withdrawn_rate': 0.15,      # 15% withdrawn feedback
            'score_trend_7d': -0.1,      # Declining slightly
            'is_anomaly': True,          # Flagged for attention
            'total_reviews': 48
        }
        
        conn.close()
        return sample_data
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("📝 Using default test data instead")
        
        return {
            'employee_id': 'Jamie Brown',
            'avg_score': 3.2,
            'composite_score': 3.1,
            'collaboration_rate': 0.65,
            'withdrawn_rate': 0.15,
            'score_trend_7d': -0.1,
            'is_anomaly': True,
            'total_reviews': 48
        }

def test_fallback():
    """Test fallback insights (no API key needed)"""
    print("\n🔧 Testing Fallback LLM (No API Key)")
    print("-" * 40)
    
    employee_data = test_with_real_employee()
    
    llm = LLMInsightsGenerator(provider="openai")  # No API key = fallback
    insights = llm.generate_employee_insights(employee_data)
    
    print("✅ Fallback insights generated!")
    print(f"📊 Employee: {employee_data['employee_id']}")
    print(f"📈 Score: {employee_data['avg_score']}/5.0")
    print(f"🤝 Collaboration: {employee_data['collaboration_rate']:.1%}")
    print()
    
    for section, content in insights.items():
        print(f"📋 {section.upper().replace('_', ' ')}:")
        print(f"   {content}")
        print()

def test_openai_api():
    """Test OpenAI API if key is available"""
    print("\n🤖 Testing OpenAI API")
    print("-" * 40)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  No OPENAI_API_KEY found.")
        print("   To test OpenAI, set your API key:")
        print("   export OPENAI_API_KEY='sk-...'")
        return False
    
    employee_data = test_with_real_employee()
    
    try:
        llm = LLMInsightsGenerator(provider="openai", api_key=api_key)
        insights = llm.generate_employee_insights(employee_data)
        
        print("✅ OpenAI API call successful!")
        print(f"🔑 Using API key: {api_key[:8]}...{api_key[-4:]}")
        print(f"📊 Employee: {employee_data['employee_id']}")
        print()
        
        for section, content in insights.items():
            print(f"🧠 {section.upper().replace('_', ' ')}:")
            print(f"   {content}")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        return False

def test_gemini_api():
    """Test Gemini API if key is available"""
    print("\n💎 Testing Gemini API")
    print("-" * 40)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  No GEMINI_API_KEY found.")
        print("   To test Gemini, set your API key:")
        print("   export GEMINI_API_KEY='your-gemini-key'")
        return False
    
    employee_data = test_with_real_employee()
    
    try:
        llm = LLMInsightsGenerator(provider="gemini", api_key=api_key)
        insights = llm.generate_employee_insights(employee_data)
        
        print("✅ Gemini API call successful!")
        print(f"🔑 Using API key: {api_key[:8]}...{api_key[-4:]}")
        print(f"📊 Employee: {employee_data['employee_id']}")
        print()
        
        for section, content in insights.items():
            print(f"💡 {section.upper().replace('_', ' ')}:")
            print(f"   {content}")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        return False

def main():
    """Run LLM API tests"""
    print("🚀 PeerPulse LLM API Simple Test")
    print("=" * 40)
    
    # Test 1: Fallback (always works)
    test_fallback()
    
    # Test 2: OpenAI (if key available)
    openai_success = test_openai_api()
    
    # Test 3: Gemini (if key available)
    gemini_success = test_gemini_api()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 40)
    print("✅ Fallback LLM: Working")
    print(f"{'✅' if openai_success else '❌'} OpenAI API: {'Working' if openai_success else 'Not tested/failed'}")
    print(f"{'✅' if gemini_success else '❌'} Gemini API: {'Working' if gemini_success else 'Not tested/failed'}")
    
    if not openai_success and not gemini_success:
        print("\n💡 To test LLM APIs:")
        print("1. Get OpenAI API key: https://platform.openai.com/api-keys")
        print("2. Set: export OPENAI_API_KEY='sk-...'")
        print("3. Re-run this test")
        print("\nOR")
        print("1. Get Gemini API key: https://aistudio.google.com/app/apikey")
        print("2. Set: export GEMINI_API_KEY='your-key'") 
        print("3. Re-run this test")

if __name__ == "__main__":
    main()
