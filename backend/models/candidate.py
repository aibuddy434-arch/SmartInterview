from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    resume_path: Optional[str] = None

class Candidate(CandidateBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    resume_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CandidateOut(BaseModel):
    """Response schema for Candidate ORM model serialization"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    resume_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class CandidateResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    question_number: int
    response_url: Optional[str] = None
    response_text: Optional[str] = None
    media_id: Optional[str] = None  # GridFS file ID for media files
    duration: Optional[int] = None  # in seconds
    transcript: Optional[str] = None  # AI-generated transcript
    timestamps: Optional[List[dict]] = None  # Word-level timestamps from transcript
    confidence_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CandidateReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    candidate_id: str
    overall_score: float
    breakdown: dict  # {"communication": 8.5, "technical": 7.2, "overall": 7.8}
    summary: Optional[str] = None
    recommendations: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

