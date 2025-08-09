"""
Enterprise Database Manager for PeerPulse V3.0
PostgreSQL-based database with advanced features
"""

import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Float, Text, 
    ForeignKey, JSON, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import os
import logging
from contextlib import asynccontextmanager

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://peerpulse:password@localhost/peerpulse_v3"
)

# SQLAlchemy setup
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

logger = logging.getLogger(__name__)

# Database Models
class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(String, default="employee")  # employee, manager, hr, admin
    is_active = Column(Boolean, default=True)
    employee_id = Column(String, index=True)
    department = Column(String, index=True)
    manager_id = Column(String, index=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_dept_role', 'department', 'role'),
        Index('idx_user_manager', 'manager_id'),
    )

class Employee(Base):
    """Employee profile model"""
    __tablename__ = "employees"
    
    employee_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String, index=True)
    position = Column(String)
    manager_id = Column(String, index=True)
    hire_date = Column(Date)
    status = Column(String, default="active")  # active, inactive, on_leave, terminated
    user_id = Column(Integer, ForeignKey("users.id"))
    metadata = Column(JSON)  # Additional employee data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_employee_dept_status', 'department', 'status'),
        Index('idx_employee_manager', 'manager_id'),
    )

class Review(Base):
    """Peer review model"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(String, index=True)
    reviewee_id = Column(String, index=True)
    date = Column(Date, default=date.today)
    descriptor = Column(String, index=True)  # collaborative, neutral, withdrawn, blocking
    score = Column(Integer)  # 1-5 optional rating
    comment = Column(Text)
    status = Column(String, default="submitted")  # draft, submitted, reviewed, archived
    ai_insights = Column(JSON)  # AI-generated insights
    metadata = Column(JSON)  # Additional review data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_review_reviewee_date', 'reviewee_id', 'date'),
        Index('idx_review_reviewer_date', 'reviewer_id', 'date'),
        Index('idx_review_descriptor', 'descriptor'),
        UniqueConstraint('reviewer_id', 'reviewee_id', 'date', name='unique_daily_review'),
    )

class AnalyticsCache(Base):
    """Cached analytics results for performance"""
    __tablename__ = "analytics_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, unique=True, index=True)
    cache_type = Column(String, index=True)  # employee, team, executive
    data = Column(JSON)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cache_type_expires', 'cache_type', 'expires_at'),
    )

class MLModel(Base):
    """ML model metadata and versioning"""
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    version = Column(String)
    type = Column(String)  # regressor, classifier, clusterer, anomaly_detector
    parameters = Column(JSON)
    metrics = Column(JSON)
    file_path = Column(String)
    is_active = Column(Boolean, default=False)
    trained_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_model_name_version', 'name', 'version'),
        UniqueConstraint('name', 'is_active', name='unique_active_model'),
    )

class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String)
    message = Column(Text)
    type = Column(String)  # info, warning, alert, success
    priority = Column(String, default="normal")  # low, normal, high, urgent
    status = Column(String, default="unread")  # unread, read, archived
    action_url = Column(String)
    expires_at = Column(DateTime)
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_notification_user_status', 'user_id', 'status'),
        Index('idx_notification_expires', 'expires_at'),
    )

class AuditLog(Base):
    """Audit log for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action = Column(String, index=True)
    resource_type = Column(String, index=True)
    resource_id = Column(String, index=True)
    details = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_timestamp', 'timestamp'),
    )

# Database Manager
class DatabaseManager:
    """Enterprise database manager with connection pooling and caching"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
        
    async def initialize(self):
        """Initialize database and create tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with proper cleanup"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("Database connections closed")
    
    # User management
    async def create_user(self, user_data: dict) -> User:
        """Create new user"""
        async with self.get_session() as session:
            user = User(**user_data)
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return user
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        async with self.get_session() as session:
            result = await session.get(User, user_id)
            return result
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async with self.get_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE email = :email",
                {"email": email}
            )
            return result.fetchone()
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users with pagination"""
        async with self.get_session() as session:
            result = await session.execute(
                "SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :skip",
                {"limit": limit, "skip": skip}
            )
            return result.fetchall()
    
    # Employee management
    async def create_employee(self, employee_data: dict) -> Employee:
        """Create new employee"""
        if not employee_data.get('employee_id'):
            employee_data['employee_id'] = f"EMP_{uuid.uuid4().hex[:8].upper()}"
        
        async with self.get_session() as session:
            employee = Employee(**employee_data)
            session.add(employee)
            await session.flush()
            await session.refresh(employee)
            return employee
    
    async def get_employees(
        self, 
        department: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Employee]:
        """Get employees with filters"""
        query = "SELECT * FROM employees WHERE status = 'active'"
        params = {"skip": skip, "limit": limit}
        
        if department:
            query += " AND department = :department"
            params["department"] = department
        
        query += " ORDER BY name LIMIT :limit OFFSET :skip"
        
        async with self.get_session() as session:
            result = await session.execute(query, params)
            return result.fetchall()
    
    # Review management
    async def create_review(self, review_data: dict) -> Review:
        """Create new review"""
        async with self.get_session() as session:
            review = Review(**review_data)
            session.add(review)
            await session.flush()
            await session.refresh(review)
            
            # Log audit event
            await self._log_audit(
                user_id=None,  # Will be set from context
                action="create_review",
                resource_type="review",
                resource_id=str(review.id),
                details={"reviewer": review.reviewer_id, "reviewee": review.reviewee_id}
            )
            
            return review
    
    async def get_reviews(
        self,
        employee_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """Get reviews with filters"""
        query = "SELECT * FROM reviews WHERE 1=1"
        params = {"skip": skip, "limit": limit}
        
        if employee_id:
            query += " AND (reviewer_id = :employee_id OR reviewee_id = :employee_id)"
            params["employee_id"] = employee_id
        
        if start_date:
            query += " AND date >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            query += " AND date <= :end_date"
            params["end_date"] = end_date
        
        query += " ORDER BY date DESC LIMIT :limit OFFSET :skip"
        
        async with self.get_session() as session:
            result = await session.execute(query, params)
            return result.fetchall()
    
    # Analytics caching
    async def get_cached_analytics(self, cache_key: str) -> Optional[dict]:
        """Get cached analytics data"""
        async with self.get_session() as session:
            result = await session.execute(
                "SELECT data FROM analytics_cache WHERE cache_key = :key AND expires_at > NOW()",
                {"key": cache_key}
            )
            row = result.fetchone()
            return row.data if row else None
    
    async def cache_analytics(self, cache_key: str, cache_type: str, data: dict, ttl_hours: int = 1):
        """Cache analytics data"""
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        async with self.get_session() as session:
            # Upsert cache entry
            await session.execute(
                """
                INSERT INTO analytics_cache (cache_key, cache_type, data, expires_at)
                VALUES (:key, :type, :data, :expires_at)
                ON CONFLICT (cache_key) 
                DO UPDATE SET data = :data, expires_at = :expires_at
                """,
                {
                    "key": cache_key,
                    "type": cache_type,
                    "data": data,
                    "expires_at": expires_at
                }
            )
    
    # ML model management
    async def save_ml_model(self, model_data: dict) -> MLModel:
        """Save ML model metadata"""
        async with self.get_session() as session:
            # Deactivate previous models of same name
            await session.execute(
                "UPDATE ml_models SET is_active = FALSE WHERE name = :name",
                {"name": model_data["name"]}
            )
            
            model = MLModel(**model_data)
            session.add(model)
            await session.flush()
            await session.refresh(model)
            return model
    
    async def get_active_model(self, model_name: str) -> Optional[MLModel]:
        """Get active ML model"""
        async with self.get_session() as session:
            result = await session.execute(
                "SELECT * FROM ml_models WHERE name = :name AND is_active = TRUE",
                {"name": model_name}
            )
            return result.fetchone()
    
    # Audit logging
    async def _log_audit(self, user_id: int, action: str, resource_type: str, resource_id: str, details: dict):
        """Log audit event"""
        async with self.get_session() as session:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details
            )
            session.add(audit_log)
    
    # HR system integration
    async def sync_hr_data(self, hr_data: dict) -> dict:
        """Sync data from external HR systems"""
        results = {"employees_created": 0, "employees_updated": 0, "errors": []}
        
        async with self.get_session() as session:
            for emp_data in hr_data.get("employees", []):
                try:
                    # Check if employee exists
                    existing = await session.execute(
                        "SELECT employee_id FROM employees WHERE email = :email",
                        {"email": emp_data["email"]}
                    )
                    
                    if existing.fetchone():
                        # Update existing employee
                        await session.execute(
                            "UPDATE employees SET name = :name, department = :dept WHERE email = :email",
                            {
                                "name": emp_data["name"],
                                "dept": emp_data["department"],
                                "email": emp_data["email"]
                            }
                        )
                        results["employees_updated"] += 1
                    else:
                        # Create new employee
                        employee = Employee(**emp_data)
                        session.add(employee)
                        results["employees_created"] += 1
                        
                except Exception as e:
                    results["errors"].append(f"Error processing {emp_data.get('email', 'unknown')}: {str(e)}")
        
        return results
    
    # Data export
    async def export_reviews(self, format: str, start_date: Optional[date], end_date: Optional[date]) -> dict:
        """Export review data"""
        query = "SELECT * FROM reviews WHERE 1=1"
        params = {}
        
        if start_date:
            query += " AND date >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            query += " AND date <= :end_date"
            params["end_date"] = end_date
        
        async with self.get_session() as session:
            result = await session.execute(query, params)
            reviews = result.fetchall()
            
            # Convert to desired format
            if format == "csv":
                # Convert to CSV format
                return {"format": "csv", "data": reviews, "count": len(reviews)}
            elif format == "json":
                # Convert to JSON format
                return {"format": "json", "data": reviews, "count": len(reviews)}
            else:
                raise ValueError(f"Unsupported format: {format}")

# Dependency injection
async def get_db() -> DatabaseManager:
    """Get database manager instance"""
    return DatabaseManager()
