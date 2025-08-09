"""
Pydantic Models for PeerPulse V3.0 Enterprise
Data validation and serialization models
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

# Enums
class UserRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR = "hr"
    ADMIN = "admin"

class ReviewStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"

# Base models
class BaseEntity(BaseModel):
    """Base model with common fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

# User models
class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.EMPLOYEE
    is_active: bool = True

class UserCreate(UserBase):
    """User creation model"""
    password: str
    employee_id: Optional[str] = None
    department: Optional[str] = None
    manager_id: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    department: Optional[str] = None
    manager_id: Optional[str] = None

class User(UserBase, BaseEntity):
    """Complete user model"""
    id: int
    employee_id: Optional[str] = None
    department: Optional[str] = None
    manager_id: Optional[str] = None
    last_login: Optional[datetime] = None

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role in [UserRole.MANAGER, UserRole.ADMIN]

    @property
    def is_hr(self) -> bool:
        return self.role in [UserRole.HR, UserRole.ADMIN]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

# Employee models
class EmployeeBase(BaseModel):
    """Base employee model"""
    name: str
    email: EmailStr
    department: str
    position: Optional[str] = None
    manager_id: Optional[str] = None
    hire_date: Optional[date] = None
    status: EmployeeStatus = EmployeeStatus.ACTIVE

class EmployeeCreate(EmployeeBase):
    """Employee creation model"""
    employee_id: Optional[str] = None  # Auto-generated if not provided

class EmployeeUpdate(BaseModel):
    """Employee update model"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    position: Optional[str] = None
    manager_id: Optional[str] = None
    status: Optional[EmployeeStatus] = None

class EmployeeResponse(EmployeeBase, BaseEntity):
    """Complete employee response model"""
    employee_id: str
    user_id: Optional[int] = None

# Review models
class ReviewBase(BaseModel):
    """Base review model"""
    reviewee_id: str
    descriptor: str
    score: Optional[int] = None
    comment: Optional[str] = None

    @validator('score')
    def validate_score(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Score must be between 1 and 5')
        return v

    @validator('descriptor')
    def validate_descriptor(cls, v):
        valid_descriptors = ['collaborative', 'neutral', 'withdrawn', 'blocking']
        if v not in valid_descriptors:
            raise ValueError(f'Descriptor must be one of: {valid_descriptors}')
        return v

class ReviewCreate(ReviewBase):
    """Review creation model"""
    reviewer_id: str

class ReviewUpdate(BaseModel):
    """Review update model"""
    descriptor: Optional[str] = None
    score: Optional[int] = None
    comment: Optional[str] = None
    status: Optional[ReviewStatus] = None

class ReviewResponse(ReviewBase, BaseEntity):
    """Complete review response model"""
    id: int
    reviewer_id: str
    date: date
    status: ReviewStatus = ReviewStatus.SUBMITTED
    ai_insights: Optional[Dict[str, Any]] = None

# Analytics models
class EmployeeMetrics(BaseModel):
    """Employee performance metrics"""
    employee_id: str
    avg_score: float
    composite_score: float
    collaboration_rate: float
    withdrawn_rate: float
    neutral_rate: float
    blocking_rate: float
    score_trend_7d: float
    score_trend_14d: float
    total_reviews: int
    is_anomaly: bool
    risk_level: str  # low, medium, high
    performance_category: str  # high_performer, steady, needs_attention, at_risk

class TeamMetrics(BaseModel):
    """Team-level metrics"""
    department: str
    team_size: int
    avg_team_score: float
    high_performers: int
    at_risk_members: int
    collaboration_index: float
    team_health_score: float
    turnover_risk: float

class AnalyticsResponse(BaseModel):
    """Comprehensive analytics response"""
    employee_id: str
    metrics: EmployeeMetrics
    insights: Dict[str, str]
    recommendations: List[str]
    period_days: int
    last_updated: datetime

class TeamInsights(BaseModel):
    """Team insights and recommendations"""
    department: str
    metrics: TeamMetrics
    top_performers: List[str]
    at_risk_employees: List[str]
    team_recommendations: List[str]
    collaboration_network: Dict[str, Any]

class ExecutiveDashboard(BaseModel):
    """Executive-level dashboard data"""
    organization_metrics: Dict[str, float]
    department_performance: List[TeamMetrics]
    key_insights: List[str]
    action_items: List[str]
    trends: Dict[str, List[float]]

# Notification models
class NotificationBase(BaseModel):
    """Base notification model"""
    title: str
    message: str
    type: str  # info, warning, alert, success
    priority: str = "normal"  # low, normal, high, urgent

class NotificationCreate(NotificationBase):
    """Notification creation model"""
    user_id: int
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None

class NotificationResponse(NotificationBase, BaseEntity):
    """Complete notification response"""
    id: int
    user_id: int
    status: NotificationStatus = NotificationStatus.UNREAD
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

# Integration models
class HRSyncData(BaseModel):
    """HR system sync data model"""
    employees: List[EmployeeCreate]
    departments: List[str]
    organizational_chart: Dict[str, Any]
    sync_timestamp: datetime

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

# Bulk operations
class BulkReviewCreate(BaseModel):
    """Bulk review creation"""
    reviews: List[ReviewCreate]
    batch_id: Optional[str] = None

class BulkEmployeeCreate(BaseModel):
    """Bulk employee creation"""
    employees: List[EmployeeCreate]
    validate_emails: bool = True
    send_invitations: bool = False

# Export models
class ExportRequest(BaseModel):
    """Data export request"""
    format: str = "csv"  # csv, xlsx, json
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None
    include_sensitive: bool = False

class ExportResponse(BaseModel):
    """Export response with download link"""
    export_id: str
    download_url: str
    expires_at: datetime
    file_size: int
    record_count: int

# Search models
class SearchQuery(BaseModel):
    """Advanced search query"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = None
    sort_order: str = "desc"
    limit: int = 50
    offset: int = 0

class SearchResult(BaseModel):
    """Search result item"""
    type: str  # employee, review, insight
    id: str
    title: str
    description: str
    relevance_score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    """Complete search response"""
    query: str
    total_results: int
    results: List[SearchResult]
    facets: Dict[str, List[str]]
    suggestions: List[str]

# Performance tracking
class PerformancePeriod(BaseModel):
    """Performance tracking period"""
    start_date: date
    end_date: date
    name: str
    type: str  # quarterly, annual, project
    status: str  # active, completed, draft

class PerformanceGoal(BaseModel):
    """Individual performance goal"""
    employee_id: str
    period_id: int
    title: str
    description: str
    target_value: float
    current_value: Optional[float] = None
    weight: float = 1.0
    status: str = "active"

# Configuration models
class SystemConfig(BaseModel):
    """System configuration"""
    review_cycle_days: int = 90
    min_reviews_per_employee: int = 5
    anomaly_detection_enabled: bool = True
    ai_insights_enabled: bool = True
    notification_preferences: Dict[str, bool]
    privacy_settings: Dict[str, Any]
