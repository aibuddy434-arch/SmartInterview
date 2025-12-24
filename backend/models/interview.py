from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Union
from enum import Enum
from datetime import datetime
from uuid import uuid4

class InterviewType(str, Enum):
    GENERAL = "general"
    SPECIFIC = "specific"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class FocusArea(str, Enum):
    COMMUNICATION = "communication"
    TECHNICAL = "technical"
    OVERALL = "overall"

class AvatarChoice(str, Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    CASUAL = "casual"

class VoiceChoice(str, Enum):
    MALE_1 = "male_1"
    MALE_2 = "male_2"
    FEMALE_1 = "female_1"
    FEMALE_2 = "female_2"
    NEUTRAL = "neutral"

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    tags: List[str] = []
    generated_by: str = "manual"  # manual, ai, template
    suggested_time_seconds: Optional[int] = 120  # AI-determined time for this question (default 2 min)

class InterviewConfigBase(BaseModel):
    job_role: str
    job_description: str
    interview_type: InterviewType
    difficulty: DifficultyLevel
    focus: List[FocusArea]
    time_limit: Optional[int] = None  # in minutes
    avatar: AvatarChoice
    voice: VoiceChoice
    number_of_questions: int
    questions: List[Question] = []
    created_by: str  # user ID
    
    @field_validator('time_limit', mode='before')
    @classmethod
    def validate_time_limit(cls, v):
        """Convert empty string to None and validate time_limit"""
        if v == "" or v is None:
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("time_limit must be a valid integer or None")
        if isinstance(v, int) and v < 0:
            raise ValueError("time_limit must be a positive integer or None")
        return v
    
    @field_validator('created_by')
    @classmethod
    def validate_created_by(cls, v):
        """Ensure created_by is always provided"""
        if not v or v.strip() == "":
            raise ValueError("created_by is required and cannot be empty")
        return v.strip()

class InterviewConfigCreate(BaseModel):
    job_role: str
    job_description: str
    interview_type: InterviewType
    difficulty: DifficultyLevel
    focus: List[FocusArea]
    time_limit: Optional[int] = None  # in minutes
    avatar: AvatarChoice
    voice: VoiceChoice
    number_of_questions: int
    questions: List[Question] = []
    # created_by is not required in the request - will be set by backend from authenticated user
    
    @field_validator('time_limit', mode='before')
    @classmethod
    def validate_time_limit(cls, v):
        """Convert empty string to None and validate time_limit"""
        if v == "" or v is None:
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("time_limit must be a valid integer or None")
        if isinstance(v, int) and v < 0:
            raise ValueError("time_limit must be a positive integer or None")
        return v

class InterviewConfigUpdate(BaseModel):
    job_role: Optional[str] = None
    job_description: Optional[str] = None
    interview_type: Optional[InterviewType] = None
    difficulty: Optional[DifficultyLevel] = None
    focus: Optional[List[FocusArea]] = None
    time_limit: Optional[int] = None
    avatar: Optional[AvatarChoice] = None
    voice: Optional[VoiceChoice] = None
    number_of_questions: Optional[int] = None
    questions: Optional[List[Question]] = None

class InterviewConfig(InterviewConfigBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    total_candidates: int = 0
    completed_sessions: int = 0
    shareable_link: Optional[str] = None
    
    @property
    def time_per_question_seconds(self) -> Optional[int]:
        """Calculate time per question in seconds based on total time limit and number of questions"""
        if self.time_limit and self.number_of_questions and self.number_of_questions > 0:
            return (self.time_limit * 60) // self.number_of_questions
        return None

# Keep existing models for backward compatibility
class HardnessLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class InterviewBase(BaseModel):
    title: str
    role: str
    job_description: str
    hardness_level: HardnessLevel
    duration: int  # in minutes
    number_of_questions: int
    ai_avatar: AvatarChoice
    focus_area: FocusArea
    created_by: str  # user ID

class InterviewCreate(InterviewBase):
    pass

class InterviewUpdate(BaseModel):
    title: Optional[str] = None
    role: Optional[str] = None
    job_description: Optional[str] = None
    hardness_level: Optional[HardnessLevel] = None
    duration: Optional[int] = None
    number_of_questions: Optional[int] = None
    ai_avatar: Optional[AvatarChoice] = None
    focus_area: Optional[FocusArea] = None

class Interview(InterviewBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    interview_id: str = Field(default_factory=lambda: str(uuid4()))
    shareable_link: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    total_candidates: int = 0
    completed_sessions: int = 0

class InterviewSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    interview_id: str
    candidate_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, cancelled
    current_question: int = 0
    responses: List[dict] = []
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InterviewSessionOut(BaseModel):
    """Response schema for InterviewSession ORM model serialization"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    session_id: str
    interview_config_id: str
    candidate_id: str
    user_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str
    current_question: int
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "default" # Optional voice parameter

