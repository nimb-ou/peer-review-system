#!/usr/bin/env python3
"""
Quick Gemini API Test
Test your Gemini API key setup
"""

import os
import sys
sys.path.append('src')

from llm_integration import LLMInsightsGenerator

def test_gemini():
    """Quick test of Gemini API"""
    print("💎 Testing Gemini API Integration")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        print("\n📋 To set up Gemini API:")
        print("1. Go to: https://aistudio.google.com/app/apikey")
        print("2. Create API key")
        print("3. Run: export GEMINI_API_KEY='your-key-here'")
        print("4. Run this test again")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test data
    sample_data = {
        'employee_id': 'Jamie Brown',
        'avg_score': 2.8,  # Below average
        'composite_score': 2.7,
        'collaboration_rate': 0.35,  # Low collaboration
        'withdrawn_rate': 0.40,      # High withdrawn rate
        'score_trend_7d': -0.2,      # Declining trend
        'is_anomaly': True,          # Flagged for attention
        'total_reviews': 38
    }
    
    print(f"📊 Testing with employee: {sample_data['employee_id']}")
    print(f"   Score: {sample_data['avg_score']}/5.0 (concerning)")
    print(f"   Collaboration: {sample_data['collaboration_rate']:.1%} (low)")
    print(f"   Trend: {sample_data['score_trend_7d']:.2f} (declining)")
    print()
    
    # Test Gemini API
    try:
        print("🔄 Calling Gemini API...")
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
        print(f"❌ Gemini API failed: {e}")
        print("\n🔧 Common issues:")
        print("- Check API key is correct")
        print("- Verify API is enabled in Google Cloud")
        print("- Check internet connection")
        return False

if __name__ == "__main__":
    success = test_gemini()
    
    if success:
        print("🎉 Gemini integration working perfectly!")
        print("Ready to use AI-powered insights in V3.0!")
    else:
        print("🔧 Fix the issues above and try again")
