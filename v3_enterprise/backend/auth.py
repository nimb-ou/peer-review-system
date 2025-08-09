"""
Enterprise Authentication System for PeerPulse V3.0
JWT-based authentication with role-based access control
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from pydantic import BaseModel

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    email: str
    role: str
    employee_id: Optional[str] = None
    department: Optional[str] = None
    exp: datetime

class AuthManager:
    """Enterprise authentication manager"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "user_id": user_data["id"],
            "email": user_data["email"],
            "role": user_data["role"],
            "employee_id": user_data.get("employee_id"),
            "department": user_data.get("department"),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "user_id": user_data["id"],
            "email": user_data["email"],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            # Check expiration
            exp = datetime.fromtimestamp(payload["exp"])
            if exp < datetime.utcnow():
                return None
            
            return TokenData(
                user_id=payload["user_id"],
                email=payload["email"],
                role=payload.get("role", "employee"),
                employee_id=payload.get("employee_id"),
                department=payload.get("department"),
                exp=exp
            )
            
        except jwt.PyJWTError:
            return None
    
    async def authenticate(self, email: str, password: str) -> Optional[str]:
        """Authenticate user and return access token"""
        # In real implementation, get user from database
        from .database import DatabaseManager
        
        db = DatabaseManager()
        user = await db.get_user_by_email(email)
        
        if not user or not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account disabled"
            )
        
        # Update last login
        await db.update_user_last_login(user.id)
        
        # Create tokens
        user_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "employee_id": user.employee_id,
            "department": user.department
        }
        
        access_token = self.create_access_token(user_data)
        return access_token
    
    async def refresh_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        token_data = self.verify_token(refresh_token, "refresh")
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get fresh user data
        from .database import DatabaseManager
        db = DatabaseManager()
        user = await db.get_user(token_data.user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        user_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "employee_id": user.employee_id,
            "department": user.department
        }
        
        return self.create_access_token(user_data)

# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Get current authenticated user"""
    auth_manager = AuthManager()
    token_data = auth_manager.verify_token(credentials.credentials)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data

async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """Get current active user"""
    # In real implementation, check if user is still active in database
    return current_user

def require_role(required_roles: list):
    """Decorator to require specific roles"""
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Role-based dependencies
def require_admin(current_user: TokenData = Depends(get_current_user)):
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_manager(current_user: TokenData = Depends(get_current_user)):
    """Require manager or admin role"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user

def require_hr(current_user: TokenData = Depends(get_current_user)):
    """Require HR or admin role"""
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR access required"
        )
    return current_user

# SAML/SSO Integration (for enterprise environments)
class SAMLAuth:
    """SAML authentication for enterprise SSO"""
    
    def __init__(self, saml_settings: Dict[str, Any]):
        self.settings = saml_settings
        self.enabled = saml_settings.get("enabled", False)
    
    async def authenticate_saml(self, saml_response: str) -> Optional[Dict[str, Any]]:
        """Authenticate user via SAML response"""
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="SAML authentication not enabled"
            )
        
        # In real implementation:
        # 1. Validate SAML response signature
        # 2. Extract user attributes
        # 3. Map to internal user model
        # 4. Create/update user in database
        # 5. Return user data
        
        # Placeholder implementation
        return {
            "email": "user@company.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "employee",
            "department": "Engineering"
        }

# OAuth2 Integration (for third-party login)
class OAuth2Provider:
    """OAuth2 provider integration"""
    
    def __init__(self, provider_name: str, client_id: str, client_secret: str):
        self.provider_name = provider_name
        self.client_id = client_id
        self.client_secret = client_secret
    
    async def get_authorization_url(self, redirect_uri: str) -> str:
        """Get OAuth2 authorization URL"""
        # Implementation depends on provider (Google, Microsoft, etc.)
        pass
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        # Implementation depends on provider
        pass
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth2 provider"""
        # Implementation depends on provider
        pass

# API Key Authentication (for service-to-service communication)
class APIKeyAuth:
    """API key authentication for service integrations"""
    
    def __init__(self):
        self.api_keys = {}  # In real implementation, store in database
    
    def generate_api_key(self, user_id: int, name: str, permissions: list) -> str:
        """Generate new API key"""
        import secrets
        api_key = f"pk_{secrets.token_urlsafe(32)}"
        
        self.api_keys[api_key] = {
            "user_id": user_id,
            "name": name,
            "permissions": permissions,
            "created_at": datetime.utcnow(),
            "last_used": None
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return associated data"""
        key_data = self.api_keys.get(api_key)
        
        if key_data:
            # Update last used timestamp
            key_data["last_used"] = datetime.utcnow()
        
        return key_data

# Session Management
class SessionManager:
    """Manage user sessions for security"""
    
    def __init__(self):
        self.active_sessions = {}  # In real implementation, use Redis
    
    async def create_session(self, user_id: int, token: str, ip_address: str, user_agent: str):
        """Create new user session"""
        session_id = f"session_{user_id}_{datetime.utcnow().timestamp()}"
        
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "token": token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        return session_id
    
    async def validate_session(self, session_id: str) -> bool:
        """Validate if session is still active"""
        session = self.active_sessions.get(session_id)
        
        if not session:
            return False
        
        # Check if session expired (e.g., 24 hours of inactivity)
        if datetime.utcnow() - session["last_activity"] > timedelta(hours=24):
            await self.invalidate_session(session_id)
            return False
        
        # Update last activity
        session["last_activity"] = datetime.utcnow()
        return True
    
    async def invalidate_session(self, session_id: str):
        """Invalidate user session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    async def invalidate_user_sessions(self, user_id: int):
        """Invalidate all sessions for a user"""
        sessions_to_remove = [
            sid for sid, session in self.active_sessions.items()
            if session["user_id"] == user_id
        ]
        
        for session_id in sessions_to_remove:
            await self.invalidate_session(session_id)

# Multi-Factor Authentication
class MFAManager:
    """Multi-Factor Authentication manager"""
    
    def __init__(self):
        self.pending_verifications = {}
    
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret for authenticator apps"""
        import secrets
        return secrets.token_hex(16)
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        # Implementation would use pyotp library
        # import pyotp
        # totp = pyotp.TOTP(secret)
        # return totp.verify(token)
        return True  # Placeholder
    
    async def send_sms_code(self, phone_number: str) -> str:
        """Send SMS verification code"""
        import random
        code = f"{random.randint(100000, 999999)}"
        
        # Store code temporarily
        self.pending_verifications[phone_number] = {
            "code": code,
            "expires_at": datetime.utcnow() + timedelta(minutes=5)
        }
        
        # In real implementation, send SMS via service like Twilio
        print(f"SMS code for {phone_number}: {code}")
        
        return code
    
    def verify_sms_code(self, phone_number: str, code: str) -> bool:
        """Verify SMS code"""
        verification = self.pending_verifications.get(phone_number)
        
        if not verification:
            return False
        
        if verification["expires_at"] < datetime.utcnow():
            del self.pending_verifications[phone_number]
            return False
        
        if verification["code"] == code:
            del self.pending_verifications[phone_number]
            return True
        
        return False
