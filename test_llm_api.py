#!/usr/bin/env python3
"""
LLM API Testing Script for PeerPulse
Tests OpenAI and Gemini API integrations with real employee data
"""

import os
import sys
import json
from typing import Dict, List
from datetime import datetime

# Add src to path
sys.path.append('src')

from llm_integration import LLMInsightsGenerator
from database import DatabaseManager
from ml_pipeline import PeerReviewMLPipeline
import pandas as pd

def test_api_keys():
    """Test if API keys are available"""
    print("🔑 Checking API Keys...")
    print("-" * 50)
    
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if openai_key:
        print(f"✅ OpenAI API Key: Found ({openai_key[:8]}...{openai_key[-4:]})")
    else:
        print("❌ OpenAI API Key: Not found")
        print("   Set with: export OPENAI_API_KEY='your-key-here'")
    
    if gemini_key:
        print(f"✅ Gemini API Key: Found ({gemini_key[:8]}...{gemini_key[-4:]})")
    else:
        print("❌ Gemini API Key: Not found") 
        print("   Set with: export GEMINI_API_KEY='your-key-here'")
    
    print()
    return openai_key, gemini_key

def get_real_employee_data():
    """Get real employee data from our V2.0 database"""
    print("📊 Loading Real Employee Data...")
    print("-" * 50)
    
    try:
        # Initialize database and ML pipeline
        db = DatabaseManager()
        ml_pipeline = PeerReviewMLPipeline(db)
        
        # Get employee insights 
        insights = ml_pipeline.get_employee_insights()
        
        if insights.empty:
            print("❌ No employee data found. Run setup first:")
            print("   python scripts/setup.py")
            return None
        
        # Convert to sample for testing
        sample_employee = insights.iloc[0].to_dict()
        
        print(f"✅ Found {len(insights)} employees in database")
        print(f"📝 Using sample employee: {sample_employee.get('employee_id', 'Unknown')}")
        print(f"   - Average Score: {sample_employee.get('avg_score', 0):.2f}")
        print(f"   - Collaboration Rate: {sample_employee.get('pct_collaborative', 0):.1%}")
        print(f"   - Total Reviews: {sample_employee.get('total_reviews', 0)}")
        print()
        
        return sample_employee
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def test_fallback_insights(sample_data):
    """Test fallback insights (no API key required)"""
    print("🔧 Testing Fallback Insights (No API Required)...")
    print("-" * 50)
    
    try:
        llm = LLMInsightsGenerator(provider="openai")  # No API key
        insights = llm.generate_employee_insights(sample_data)
        
        print("✅ Fallback insights generated successfully!")
        print()
        
        for section, content in insights.items():
            print(f"📋 {section.upper().replace('_', ' ')}:")
            print(f"   {content}")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False

def test_openai_api(sample_data, api_key):
    """Test OpenAI API integration"""
    if not api_key:
        print("⏭️  Skipping OpenAI test (no API key)")
        return False
        
    print("🤖 Testing OpenAI API...")
    print("-" * 50)
    
    try:
        llm = LLMInsightsGenerator(provider="openai", api_key=api_key)
        insights = llm.generate_employee_insights(sample_data)
        
        print("✅ OpenAI API call successful!")
        print()
        
        for section, content in insights.items():
            print(f"🧠 {section.upper().replace('_', ' ')}:")
            print(f"   {content}")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        print("   Check your API key and account credits")
        return False

def test_gemini_api(sample_data, api_key):
    """Test Gemini API integration"""
    if not api_key:
        print("⏭️  Skipping Gemini test (no API key)")
        return False
        
    print("💎 Testing Gemini API...")
    print("-" * 50)
    
    try:
        llm = LLMInsightsGenerator(provider="gemini", api_key=api_key)
        insights = llm.generate_employee_insights(sample_data)
        
        print("✅ Gemini API call successful!")
        print()
        
        for section, content in insights.items():
            print(f"💡 {section.upper().replace('_', ' ')}:")
            print(f"   {content}")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        print("   Check your API key and account setup")
        return False

def test_team_insights(sample_data):
    """Test team-level insights generation"""
    print("👥 Testing Team Insights...")
    print("-" * 50)
    
    try:
        # Create sample team data
        team_data = []
        for i in range(5):
            team_member = sample_data.copy()
            team_member['employee_id'] = f'emp_{i+1:02d}'
            team_member['avg_score'] = 2.5 + (i * 0.5)  # Range from 2.5 to 4.5
            team_member['is_anomaly'] = i == 4  # Last member has anomaly
            team_data.append(team_member)
        
        llm = LLMInsightsGenerator(provider="openai")
        team_summary = llm.generate_team_summary(team_data)
        
        print("✅ Team insights generated!")
        print(team_summary)
        
        return True
        
    except Exception as e:
        print(f"❌ Team insights test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all LLM API tests"""
    print("🚀 PeerPulse LLM API Comprehensive Test")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Check API keys
    openai_key, gemini_key = test_api_keys()
    
    # Test 2: Load real data
    sample_data = get_real_employee_data()
    if not sample_data:
        print("❌ Cannot proceed without employee data")
        return
    
    # Test results
    results = {}
    
    # Test 3: Fallback insights
    results['fallback'] = test_fallback_insights(sample_data)
    
    # Test 4: OpenAI API
    results['openai'] = test_openai_api(sample_data, openai_key)
    
    # Test 5: Gemini API  
    results['gemini'] = test_gemini_api(sample_data, gemini_key)
    
    # Test 6: Team insights
    results['team'] = test_team_insights(sample_data)
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.upper():<15} {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! LLM integration is working perfectly.")
    elif results['fallback']:
        print("⚠️  Basic functionality works. Set up API keys for full features.")
    else:
        print("🚨 Critical issues found. Check your setup.")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def interactive_test():
    """Interactive test where user can input custom data"""
    print("\n🎮 Interactive LLM Test Mode")
    print("-" * 40)
    
    # Get API provider choice
    provider = input("Choose provider (openai/gemini/fallback): ").lower()
    if provider not in ['openai', 'gemini', 'fallback']:
        provider = 'fallback'
    
    # Get custom employee data
    print("\nEnter employee data (press Enter for defaults):")
    
    try:
        emp_id = input("Employee ID [test_emp]: ") or "test_emp"
        avg_score = float(input("Average Score (1-5) [3.2]: ") or "3.2")
        collab_rate = float(input("Collaboration Rate (0-1) [0.6]: ") or "0.6")
        trend = float(input("7-day Trend (-1 to 1) [-0.1]: ") or "-0.1")
        is_anomaly = input("Anomaly detected? (y/n) [n]: ").lower().startswith('y')
        
        custom_data = {
            'employee_id': emp_id,
            'avg_score': avg_score,
            'composite_score': avg_score * 0.9,
            'collaboration_rate': collab_rate,
            'withdrawn_rate': 1 - collab_rate - 0.2,
            'score_trend_7d': trend,
            'is_anomaly': is_anomaly,
            'total_reviews': 42
        }
        
        print(f"\n🔍 Testing with {provider.upper()} provider...")
        
        if provider == 'fallback':
            llm = LLMInsightsGenerator(provider="openai")  # No API key
        else:
            api_key = os.getenv(f"{provider.upper()}_API_KEY")
            if not api_key:
                print(f"❌ No {provider.upper()}_API_KEY found. Using fallback.")
                llm = LLMInsightsGenerator(provider="openai")
            else:
                llm = LLMInsightsGenerator(provider=provider, api_key=api_key)
        
        insights = llm.generate_employee_insights(custom_data)
        
        print("\n🎯 Generated Insights:")
        print("=" * 40)
        
        for section, content in insights.items():
            print(f"\n📝 {section.upper().replace('_', ' ')}:")
            print(f"   {content}")
        
    except Exception as e:
        print(f"❌ Interactive test failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        run_comprehensive_test()
        
        # Offer interactive mode
        if input("\n🎮 Run interactive test? (y/n): ").lower().startswith('y'):
            interactive_test()
