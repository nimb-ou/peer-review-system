#!/usr/bin/env python3
"""
PeerPulse V3.0 Enterprise Demo Server
Working FastAPI server with Gemini AI integration
"""

import os
import sys
sys.path.append('src')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from datetime import datetime

# Set Gemini API key
os.environ['GEMINI_API_KEY'] = "AIzaSyBBtqc1ZXs1r2tc2MupV_bzmu600WYpxzU"

from llm_integration import LLMInsightsGenerator
from database import DatabaseManager
import pandas as pd

# Create FastAPI app
app = FastAPI(
    title="PeerPulse V3.0 Enterprise API",
    description="AI-powered peer review system with Gemini integration",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class EmployeeAnalysisRequest(BaseModel):
    employee_id: str
    avg_score: float = 3.0
    collaboration_rate: float = 0.5
    withdrawn_rate: float = 0.2
    score_trend_7d: float = 0.0
    is_anomaly: bool = False
    total_reviews: int = 30

class AIInsightResponse(BaseModel):
    employee_id: str
    insights: Dict[str, str]
    ai_provider: str
    timestamp: str
    words_count: int

@app.get("/", response_class=HTMLResponse)
async def root():
    """Welcome page with API documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PeerPulse V3.0 Enterprise API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }
            .feature { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .endpoint { background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 5px; }
            code { background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 PeerPulse V3.0 Enterprise API</h1>
            <p>AI-powered peer review system with Google Gemini integration</p>
        </div>
        
        <h2>🎯 Available Endpoints</h2>
        
        <div class="endpoint">
            <strong>GET /</strong> - This welcome page
        </div>
        
        <div class="endpoint">
            <strong>GET /health</strong> - System health check
        </div>
        
        <div class="endpoint">
            <strong>GET /employees</strong> - List all employees from V2.0 database
        </div>
        
        <div class="endpoint">
            <strong>POST /analyze/employee</strong> - Get AI insights for employee
            <br><small>Body: {"employee_id": "Jamie Brown", "avg_score": 3.2, ...}</small>
        </div>
        
        <div class="endpoint">
            <strong>GET /analyze/bulk</strong> - Analyze all employees with AI
        </div>
        
        <div class="endpoint">
            <strong>GET /demo/scenarios</strong> - Pre-built employee scenarios
        </div>
        
        <h2>🧠 AI Features</h2>
        <div class="feature">
            <strong>Gemini AI Integration:</strong> Advanced behavioral analysis and recommendations
        </div>
        <div class="feature">
            <strong>Real Data Integration:</strong> Your V2.0 database with 25 employees and reviews
        </div>
        <div class="feature">
            <strong>Enterprise Analytics:</strong> Performance metrics and trend analysis
        </div>
        
        <h2>📚 Documentation</h2>
        <p>Visit <a href="/docs">/docs</a> for interactive API documentation</p>
        <p>Visit <a href="/redoc">/redoc</a> for alternative documentation</p>
        
        <p><em>PeerPulse V3.0 - Built with FastAPI, powered by Gemini AI</em></p>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "ai_provider": "Google Gemini",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/employees")
async def get_employees():
    """Get all employees from V2.0 database"""
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        
        employees_df = pd.read_sql('SELECT name, department FROM employees', conn)
        employees = employees_df.to_dict('records')
        
        conn.close()
        
        return {
            "total_employees": len(employees),
            "employees": employees,
            "source": "V2.0 Database"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/analyze/employee", response_model=AIInsightResponse)
async def analyze_employee(request: EmployeeAnalysisRequest):
    """Get AI insights for a specific employee"""
    try:
        # Convert request to dictionary
        employee_data = request.dict()
        
        # Generate AI insights
        llm = LLMInsightsGenerator(provider="gemini", api_key=os.getenv('GEMINI_API_KEY'))
        insights = llm.generate_employee_insights(employee_data)
        
        # Count words in insights
        total_words = sum(len(insight.split()) for insight in insights.values() if insight)
        
        return AIInsightResponse(
            employee_id=request.employee_id,
            insights=insights,
            ai_provider="Google Gemini",
            timestamp=datetime.now().isoformat(),
            words_count=total_words
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis error: {str(e)}")

@app.get("/analyze/bulk")
async def bulk_analyze():
    """Analyze all employees with AI insights"""
    try:
        # Get employees from database
        db = DatabaseManager()
        conn = db.get_connection()
        employees_df = pd.read_sql('SELECT name, department FROM employees LIMIT 5', conn)
        conn.close()
        
        # Create analysis scenarios
        scenarios = [
            {"avg_score": 4.2, "collaboration_rate": 0.85, "score_trend_7d": 0.1, "is_anomaly": False},
            {"avg_score": 2.8, "collaboration_rate": 0.35, "score_trend_7d": -0.2, "is_anomaly": True},
            {"avg_score": 3.5, "collaboration_rate": 0.65, "score_trend_7d": 0.05, "is_anomaly": False},
            {"avg_score": 2.1, "collaboration_rate": 0.25, "score_trend_7d": -0.35, "is_anomaly": True},
            {"avg_score": 4.8, "collaboration_rate": 0.92, "score_trend_7d": 0.15, "is_anomaly": False}
        ]
        
        llm = LLMInsightsGenerator(provider="gemini", api_key=os.getenv('GEMINI_API_KEY'))
        results = []
        
        for i, employee in employees_df.iterrows():
            if i < len(scenarios):
                scenario = scenarios[i]
                scenario.update({
                    'employee_id': employee['name'],
                    'withdrawn_rate': 1 - scenario['collaboration_rate'] - 0.3,
                    'total_reviews': 40 + (i * 5)
                })
                
                insights = llm.generate_employee_insights(scenario)
                words_count = sum(len(insight.split()) for insight in insights.values() if insight)
                
                results.append({
                    'employee_id': employee['name'],
                    'department': employee['department'],
                    'scenario_type': 'high_performer' if scenario['avg_score'] > 4.0 else 
                                   'at_risk' if scenario['avg_score'] < 3.0 else 'steady',
                    'insights': insights,
                    'words_count': words_count,
                    'metrics': scenario
                })
        
        return {
            "total_analyzed": len(results),
            "analysis_results": results,
            "ai_provider": "Google Gemini",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk analysis error: {str(e)}")

@app.get("/demo/scenarios")
async def demo_scenarios():
    """Get pre-built employee scenarios for testing"""
    scenarios = [
        {
            "name": "High Performer",
            "description": "Top performer with excellent collaboration",
            "data": {
                "employee_id": "Jamie Brown",
                "avg_score": 4.2,
                "collaboration_rate": 0.85,
                "withdrawn_rate": 0.05,
                "score_trend_7d": 0.1,
                "is_anomaly": False,
                "total_reviews": 52
            }
        },
        {
            "name": "At Risk Employee",
            "description": "Declining performance, needs support",
            "data": {
                "employee_id": "Quinn Davis",
                "avg_score": 2.8,
                "collaboration_rate": 0.35,
                "withdrawn_rate": 0.40,
                "score_trend_7d": -0.2,
                "is_anomaly": True,
                "total_reviews": 38
            }
        },
        {
            "name": "Steady Performer",
            "description": "Consistent performance, room for growth",
            "data": {
                "employee_id": "River Anderson",
                "avg_score": 3.5,
                "collaboration_rate": 0.65,
                "withdrawn_rate": 0.20,
                "score_trend_7d": 0.05,
                "is_anomaly": False,
                "total_reviews": 45
            }
        }
    ]
    
    return {
        "scenarios": scenarios,
        "usage": "POST these data objects to /analyze/employee for AI insights"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
