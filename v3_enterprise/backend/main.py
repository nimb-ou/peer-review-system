"""
PeerPulse V3.0 Enterprise - Main FastAPI Application
High-performance REST API for enterprise peer review system
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import List, Optional
import os
from datetime import datetime

# Internal imports
from .auth import AuthManager, get_current_user
from .database import DatabaseManager, get_db
from .models import (
    User, UserCreate, UserUpdate,
    Review, ReviewCreate, ReviewResponse,
    Employee, EmployeeCreate, EmployeeResponse,
    TeamInsights, AnalyticsResponse
)
from .analytics import AdvancedAnalytics
from .ml_service import MLService
from .notifications import NotificationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 PeerPulse V3.0 Enterprise starting up...")
    
    # Initialize services
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    ml_service = MLService()
    await ml_service.initialize()
    
    notification_service = NotificationService()
    await notification_service.initialize()
    
    logger.info("✅ All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 PeerPulse V3.0 Enterprise shutting down...")
    await db_manager.close()
    await ml_service.close()
    await notification_service.close()
    logger.info("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="PeerPulse Enterprise API",
    description="Advanced peer review system with AI-powered insights",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "3.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Authentication endpoints
@app.post("/api/v3/auth/login", tags=["Authentication"])
async def login(credentials: dict, auth_manager: AuthManager = Depends()):
    """User login endpoint"""
    try:
        token = await auth_manager.authenticate(
            credentials["email"], 
            credentials["password"]
        )
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.post("/api/v3/auth/refresh", tags=["Authentication"])
async def refresh_token(
    token: HTTPAuthorizationCredentials = Depends(security),
    auth_manager: AuthManager = Depends()
):
    """Refresh access token"""
    try:
        new_token = await auth_manager.refresh_token(token.credentials)
        return {"access_token": new_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# User management
@app.post("/api/v3/users", response_model=User, tags=["Users"])
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """Create new user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return await db.create_user(user_data)

@app.get("/api/v3/users", response_model=List[User], tags=["Users"])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """Get all users (admin/manager only)"""
    if not (current_user.is_admin or current_user.is_manager):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    
    return await db.get_users(skip=skip, limit=limit)

@app.get("/api/v3/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """Get user by ID"""
    # Users can view their own profile, managers can view team members
    if not (current_user.id == user_id or current_user.is_manager or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

# Employee management
@app.post("/api/v3/employees", response_model=EmployeeResponse, tags=["Employees"])
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """Create new employee profile"""
    if not (current_user.is_admin or current_user.is_hr):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or admin access required"
        )
    
    return await db.create_employee(employee_data)

@app.get("/api/v3/employees", response_model=List[EmployeeResponse], tags=["Employees"])
async def get_employees(
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """Get employees with optional department filter"""
    return await db.get_employees(
        department=department,
        skip=skip,
        limit=limit
    )

# Review system
@app.post("/api/v3/reviews", response_model=ReviewResponse, tags=["Reviews"])
async def submit_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db),
    ml_service: MLService = Depends()
):
    """Submit a peer review"""
    # Validate reviewer permissions
    if review_data.reviewer_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only submit reviews as yourself"
        )
    
    # Create review
    review = await db.create_review(review_data)
    
    # Trigger ML analysis (async)
    await ml_service.analyze_review(review)
    
    return review

@app.get("/api/v3/reviews", response_model=List[ReviewResponse], tags=["Reviews"])
async def get_reviews(
    employee_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """Get reviews with filters"""
    return await db.get_reviews(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

# Analytics and insights
@app.get("/api/v3/analytics/employee/{employee_id}", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_employee_analytics(
    employee_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    analytics: AdvancedAnalytics = Depends(),
    ml_service: MLService = Depends()
):
    """Get comprehensive employee analytics"""
    # Check permissions
    if not (current_user.employee_id == employee_id or 
            current_user.is_manager or 
            current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get analytics data
    metrics = await analytics.get_employee_metrics(employee_id, days)
    insights = await ml_service.generate_insights(employee_id)
    
    return AnalyticsResponse(
        employee_id=employee_id,
        metrics=metrics,
        insights=insights,
        period_days=days
    )

@app.get("/api/v3/analytics/team", response_model=TeamInsights, tags=["Analytics"])
async def get_team_analytics(
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    analytics: AdvancedAnalytics = Depends()
):
    """Get team-level analytics"""
    if not (current_user.is_manager or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    
    return await analytics.get_team_insights(department)

@app.get("/api/v3/analytics/executive", tags=["Analytics"])
async def get_executive_dashboard(
    current_user: User = Depends(get_current_user),
    analytics: AdvancedAnalytics = Depends()
):
    """Executive dashboard with organization-wide metrics"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Executive access required"
        )
    
    return await analytics.get_executive_dashboard()

# AI/ML endpoints
@app.post("/api/v3/ml/retrain", tags=["Machine Learning"])
async def retrain_models(
    current_user: User = Depends(get_current_user),
    ml_service: MLService = Depends()
):
    """Trigger ML model retraining"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    job_id = await ml_service.schedule_retraining()
    return {"job_id": job_id, "status": "scheduled"}

@app.get("/api/v3/ml/models/status", tags=["Machine Learning"])
async def get_model_status(
    current_user: User = Depends(get_current_user),
    ml_service: MLService = Depends()
):
    """Get ML model training status and metrics"""
    if not (current_user.is_admin or current_user.is_manager):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    
    return await ml_service.get_model_status()

# Notification endpoints
@app.get("/api/v3/notifications", tags=["Notifications"])
async def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Get user notifications"""
    return await notification_service.get_user_notifications(
        current_user.id, unread_only
    )

@app.post("/api/v3/notifications/{notification_id}/read", tags=["Notifications"])
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Mark notification as read"""
    await notification_service.mark_read(notification_id, current_user.id)
    return {"status": "success"}

# Integration endpoints
@app.post("/api/v3/integrations/hr-sync", tags=["Integrations"])
async def sync_hr_data(
    hr_data: dict,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """Sync data from external HR systems"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.sync_hr_data(hr_data)
    return result

# Export endpoints
@app.get("/api/v3/export/reviews", tags=["Export"])
async def export_reviews(
    format: str = "csv",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """Export review data"""
    if not (current_user.is_admin or current_user.is_hr):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or admin access required"
        )
    
    return await db.export_reviews(format, start_date, end_date)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
