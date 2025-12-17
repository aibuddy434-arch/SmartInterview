# Replace the entire contents of your models file with this code

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
import uuid
from datetime import datetime

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="candidate")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    interview_configs = relationship("InterviewConfig", back_populates="creator")
    interview_sessions = relationship("InterviewSession", back_populates="user")

class InterviewConfig(Base):
    __tablename__ = "interview_configs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_role = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    interview_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    focus = Column(JSON, nullable=False)
    time_limit = Column(Integer, nullable=True)
    avatar = Column(String(50), nullable=False)
    voice = Column(String(50), nullable=False)
    number_of_questions = Column(Integer, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    total_candidates = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    shareable_link = Column(String(255), nullable=True)
    
    creator = relationship("User", back_populates="interview_configs")
    questions = relationship("Question", back_populates="interview_config", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="interview_config")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    text = Column(Text, nullable=False)
    tags = Column(JSON, nullable=False, default=list)
    generated_by = Column(String(50), nullable=False, default="manual")
    interview_config_id = Column(String(36), ForeignKey("interview_configs.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    interview_config = relationship("InterviewConfig", back_populates="questions")

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    resume_path = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    interview_sessions = relationship("InterviewSession", back_populates="candidate")
    reports = relationship("Report", back_populates="candidate")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), unique=True, nullable=False, index=True) # Added index for faster lookups
    interview_config_id = Column(String(36), ForeignKey("interview_configs.id"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(50), default="pending")
    current_question = Column(Integer, default=0)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    interview_config = relationship("InterviewConfig", back_populates="interview_sessions")
    candidate = relationship("Candidate", back_populates="interview_sessions")
    user = relationship("User", back_populates="interview_sessions")
    responses = relationship("Response", back_populates="interview_session", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="interview_session", uselist=False)

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    # This now correctly references the unique session_id string, not the internal primary key
    session_id = Column(String(36), ForeignKey("interview_sessions.session_id"), nullable=False) # <-- CORRECTED
    question_number = Column(Integer, nullable=False)
    transcript = Column(Text, nullable=True)
    audio_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    interview_session = relationship("InterviewSession", back_populates="responses")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    # This now correctly references the unique session_id string, not the internal primary key
    session_id = Column(String(36), ForeignKey("interview_sessions.session_id"), nullable=False) # <-- CORRECTED
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    overall_score = Column(Float, nullable=False)
    breakdown = Column(JSON, nullable=False)
    summary = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    interview_session = relationship("InterviewSession", back_populates="report")
    candidate = relationship("Candidate", back_populates="reports")