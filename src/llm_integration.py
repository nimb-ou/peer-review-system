"""
LLM Integration for Peer Review System
Handles API calls to generate human-readable insights and recommendations
"""

import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
# OpenAI will be imported when needed
from pathlib import Path

class LLMInsightsGenerator:
    def __init__(self, provider="openai", api_key=None):
        """
        Initialize LLM integration
        
        Args:
            provider: LLM provider ("openai", "gemini", "anthropic")
            api_key: API key for the provider
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        
        # API key will be used when creating client instances
    
    def generate_employee_insights(self, employee_data: Dict) -> Dict[str, str]:
        """
        Generate human-readable insights for an employee
        
        Args:
            employee_data: Dictionary with employee metrics and trends
            
        Returns:
            Dictionary with summary, causes, and recommendations
        """
        # Create context for the LLM
        context = self._create_employee_context(employee_data)
        
        # Generate insights based on provider
        if self.provider == "openai":
            return self._generate_openai_insights(context)
        elif self.provider == "gemini":
            return self._generate_gemini_insights(context)
        else:
            return self._generate_fallback_insights(employee_data)
    
    def _create_employee_context(self, data: Dict) -> str:
        """Create formatted context for LLM prompt"""
        employee_id = data.get('employee_id', 'Unknown')
        avg_score = data.get('avg_score', 0)
        composite_score = data.get('composite_score', 0)
        collaboration_rate = data.get('collaboration_rate', 0)
        withdrawn_rate = data.get('withdrawn_rate', 0)
        score_trend = data.get('score_trend_7d', 0)
        is_anomaly = data.get('is_anomaly', False)
        total_reviews = data.get('total_reviews', 0)
        
        context = f"""Employee Analysis for {employee_id}:

METRICS:
- Average Score: {avg_score:.2f}/5.0
- Composite Behavioral Score: {composite_score:.2f}/5.0
- Collaboration Rate: {collaboration_rate:.1%}
- Withdrawn Behavior Rate: {withdrawn_rate:.1%}
- 7-day Score Trend: {score_trend:.3f} (positive = improving)
- Anomaly Detected: {'Yes' if is_anomaly else 'No'}
- Total Reviews (last 14 days): {total_reviews}

CONTEXT:
- Scores range from 1-5 (5 = excellent, 1 = concerning)
- Collaboration rate shows percentage of "collaborative" feedback
- Withdrawn rate shows percentage of "withdrawn" feedback
- Trend shows slope of performance over last 7 days
- Anomaly detection flags unusual patterns
"""
        return context
    
    def _generate_openai_insights(self, context: str) -> Dict[str, str]:
        """Generate insights using OpenAI API"""
        if not self.api_key:
            return self._generate_fallback_insights({})
        
        try:
            prompt = f"""You are an HR analyst expert in workplace psychology and team dynamics. 

{context}

Based on this data, provide:

1. SUMMARY: One sentence summary of this employee's current behavioral state
2. LIKELY_CAUSES: Top 2 most likely causes for the current patterns (be specific but not accusatory)
3. MANAGER_ACTIONS: 2 specific, actionable steps for the manager
4. PEER_ACTIONS: 2 specific, actionable steps for team members
5. POSITIVE_ASPECTS: 1-2 positive patterns worth highlighting

Keep responses professional, constructive, and focused on growth. Avoid negative judgments."""

            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst focused on constructive feedback and team development."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return self._parse_llm_response(content)
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_fallback_insights({})
    
    def _generate_gemini_insights(self, context: str) -> Dict[str, str]:
        """Generate insights using Google Gemini API"""
        if not self.api_key:
            return self._generate_fallback_insights({})
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"
            
            prompt = f"""You are an HR analyst expert in workplace psychology. 

{context}

Provide constructive analysis with:
1. SUMMARY: Current behavioral state (1 sentence)
2. LIKELY_CAUSES: 2 specific possible causes
3. MANAGER_ACTIONS: 2 actionable manager steps
4. PEER_ACTIONS: 2 actionable peer steps
5. POSITIVE_ASPECTS: Positive patterns to highlight

Be professional and growth-focused."""

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            return self._parse_llm_response(content)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_fallback_insights({})
    
    def _parse_llm_response(self, content: str) -> Dict[str, str]:
        """Parse structured response from LLM"""
        sections = {
            'summary': '',
            'likely_causes': '',
            'manager_actions': '',
            'peer_actions': '',
            'positive_aspects': ''
        }
        
        # Simple parsing logic
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if 'SUMMARY' in line.upper():
                current_section = 'summary'
            elif 'LIKELY_CAUSES' in line.upper() or 'CAUSES' in line.upper():
                current_section = 'likely_causes'
            elif 'MANAGER_ACTIONS' in line.upper() or 'MANAGER' in line.upper():
                current_section = 'manager_actions'
            elif 'PEER_ACTIONS' in line.upper() or 'PEER' in line.upper():
                current_section = 'peer_actions'
            elif 'POSITIVE_ASPECTS' in line.upper() or 'POSITIVE' in line.upper():
                current_section = 'positive_aspects'
            elif current_section and line:
                # Add content to current section
                if sections[current_section]:
                    sections[current_section] += '\n' + line
                else:
                    sections[current_section] = line
        
        return sections
    
    def _generate_fallback_insights(self, data: Dict) -> Dict[str, str]:
        """Generate basic insights without LLM (fallback)"""
        avg_score = data.get('avg_score', 3.0)
        collaboration_rate = data.get('collaboration_rate', 0.5)
        trend = data.get('score_trend_7d', 0)
        is_anomaly = data.get('is_anomaly', False)
        
        # Rule-based insights
        if avg_score >= 4.0:
            summary = "Employee showing strong positive performance and collaboration."
        elif avg_score >= 3.5:
            summary = "Employee performing well with room for growth."
        elif avg_score >= 2.5:
            summary = "Employee showing mixed performance patterns requiring attention."
        else:
            summary = "Employee performance indicates need for support and intervention."
        
        causes = []
        if collaboration_rate < 0.3:
            causes.append("Low collaboration rate may indicate stress or disengagement")
        if trend < -0.1:
            causes.append("Declining trend suggests emerging challenges")
        if is_anomaly:
            causes.append("Unusual pattern detected - possible life event or work pressure")
        if not causes:
            causes.append("Performance appears stable")
        
        manager_actions = [
            "Schedule regular one-on-one check-ins",
            "Provide clear feedback and support resources"
        ]
        
        peer_actions = [
            "Include in collaborative activities",
            "Offer peer mentoring and team bonding"
        ]
        
        positive_aspects = "Regular peer feedback shows team engagement" if avg_score > 2.5 else "Opportunity for growth and development"
        
        return {
            'summary': summary,
            'likely_causes': '\n'.join(causes),
            'manager_actions': '\n'.join(manager_actions),
            'peer_actions': '\n'.join(peer_actions),
            'positive_aspects': positive_aspects
        }
    
    def generate_team_summary(self, team_data: List[Dict]) -> str:
        """Generate team-level insights"""
        if not team_data:
            return "No team data available for analysis."
        
        # Calculate team metrics
        avg_team_score = sum(emp.get('avg_score', 0) for emp in team_data) / len(team_data)
        high_performers = [emp for emp in team_data if emp.get('avg_score', 0) >= 4.0]
        concerns = [emp for emp in team_data if emp.get('is_anomaly', False) or emp.get('avg_score', 0) < 2.5]
        
        summary = f"""TEAM OVERVIEW:
- Team Size: {len(team_data)} members
- Average Team Score: {avg_team_score:.2f}/5.0
- High Performers: {len(high_performers)} members
- Members Needing Attention: {len(concerns)} members

RECOMMENDATIONS:
- Continue recognizing high performers
- Provide targeted support for struggling members
- Foster team collaboration and peer mentoring
- Monitor trends and provide proactive interventions
"""
        
        return summary

def main():
    """Test LLM integration with sample data"""
    # Sample employee data for testing
    sample_data = {
        'employee_id': 'emp_01',
        'avg_score': 3.2,
        'composite_score': 3.1,
        'collaboration_rate': 0.35,
        'withdrawn_rate': 0.25,
        'score_trend_7d': -0.05,
        'is_anomaly': True,
        'total_reviews': 45
    }
    
    # Test with fallback (no API key)
    llm = LLMInsightsGenerator(provider="openai")
    insights = llm.generate_employee_insights(sample_data)
    
    print("=== Employee Insights (Fallback) ===")
    for key, value in insights.items():
        print(f"{key.upper()}:")
        print(value)
        print()

if __name__ == "__main__":
    main()
