from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime
from uuid import uuid4

class UserRole(str, Enum):
    ADMIN = "admin"
    INTERVIEWER = "interviewer"
    CANDIDATE = "candidate"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.CANDIDATE

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserInDB(User):
    password_hash: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[User] = None

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

