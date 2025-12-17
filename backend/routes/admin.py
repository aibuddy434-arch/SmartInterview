from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.session_repository import SessionRepository
from models.user import User, UserCreate, UserUpdate
from models.interview import Interview, InterviewCreate, InterviewUpdate
from models.candidate import Candidate, CandidateCreate
from utils.auth import get_current_admin_only, get_current_admin_user
import secrets
import aiofiles
import os
from datetime import datetime

router = APIRouter()

# User Management
@router.get("/users", response_model=List[User])
async def get_all_users(
    current_user: User = Depends(get_current_admin_only),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (admin only)"""
    user_repository = UserRepository(db)
    users = await user_repository.get_all_users()
    return users

@router.post("/users", response_model=User)
async def create_user(
    user: UserCreate, 
    current_user: User = Depends(get_current_admin_only),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (admin only)"""
    user_repository = UserRepository(db)
    
    # Check if user already exists
    existing_user = await user_repository.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    from utils.auth import get_password_hash
    hashed_password = get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict["password_hash"] = hashed_password
    
    created_user = await user_repository.create_user(user_dict)
    return created_user

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str, 
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_admin_only),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only)"""
    user_repository = UserRepository(db)
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        from utils.auth import get_password_hash
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    updated_user = await user_repository.update_user(user_id, update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str, 
    current_user: User = Depends(get_current_admin_only),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (admin only)"""
    user_repository = UserRepository(db)
    success = await user_repository.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Interview Management
@router.post("/interviews", response_model=Interview)
async def create_interview(
    interview: InterviewCreate, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new interview session"""
    interview_repository = InterviewRepository(db)
    
    interview_dict = interview.model_dump()
    interview_dict["created_by"] = current_user.id
    interview_dict["interview_id"] = str(secrets.token_urlsafe(16))
    interview_dict["shareable_link"] = f"/interview/{interview_dict['interview_id']}"
    interview_dict["created_at"] = datetime.utcnow()
    interview_dict["updated_at"] = datetime.utcnow()
    
    created_interview = await interview_repository.create_interview(interview_dict)
    return created_interview

@router.get("/interviews", response_model=List[Interview])
async def get_all_interviews(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all interviews"""
    interview_repository = InterviewRepository(db)
    interviews = await interview_repository.get_all_interviews()
    return interviews

@router.get("/interviews/{interview_id}", response_model=Interview)
async def get_interview(
    interview_id: str, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific interview"""
    interview_repository = InterviewRepository(db)
    interview = await interview_repository.get_interview_by_id(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.put("/interviews/{interview_id}", response_model=Interview)
async def update_interview(
    interview_id: str, 
    interview_update: InterviewUpdate, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update interview"""
    interview_repository = InterviewRepository(db)
    update_data = interview_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
    
    updated_interview = await interview_repository.update_interview(interview_id, update_data)
    if not updated_interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return updated_interview

@router.delete("/interviews/{interview_id}")
async def delete_interview(
    interview_id: str, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete interview"""
    interview_repository = InterviewRepository(db)
    success = await interview_repository.delete_interview(interview_id)
    if not success:
        raise HTTPException(status_code=404, detail="Interview not found")
    return {"message": "Interview deleted successfully"}

# System Statistics
@router.get("/stats")
async def get_system_stats(
    current_user: User = Depends(get_current_admin_only),
    db: AsyncSession = Depends(get_db)
):
    """Get system statistics (admin only)"""
    user_repository = UserRepository(db)
    interview_repository = InterviewRepository(db)
    candidate_repository = CandidateRepository(db)
    session_repository = SessionRepository(db)
    
    # Get counts (you might need to add count methods to repositories)
    users = await user_repository.get_all_users()
    interviews = await interview_repository.get_active_interview_configs()
    candidates = await candidate_repository.get_all_candidates()
    
    # For sessions, you might need to add a count method
    # For now, we'll use a simple approach
    total_users = len(users)
    total_interviews = len(interviews)
    total_candidates = len(candidates)
    total_sessions = 0  # You can add a count method to session repository
    
    return {
        "total_users": total_users,
        "total_interviews": total_interviews,
        "total_candidates": total_candidates,
        "total_sessions": total_sessions
    }

