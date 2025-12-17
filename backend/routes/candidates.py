from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.session_repository import SessionRepository
from models.candidate import Candidate, CandidateCreate, CandidateUpdate, CandidateResponse, CandidateReport, CandidateOut
from models.interview import InterviewSessionOut
from utils.auth import get_current_admin_user
from models.user import User
import aiofiles
import os
from datetime import datetime

router = APIRouter()

# Get all candidates (admin/interviewer only)
@router.get("/", response_model=List[CandidateOut])
async def get_all_candidates(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all candidates"""
    candidate_repository = CandidateRepository(db)
    candidates = await candidate_repository.get_all_candidates()
    return [CandidateOut.model_validate(candidate) for candidate in candidates]

# Get specific candidate
@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(
    candidate_id: str, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific candidate details"""
    candidate_repository = CandidateRepository(db)
    candidate = await candidate_repository.get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return CandidateOut.model_validate(candidate)

# Update candidate
@router.put("/{candidate_id}", response_model=CandidateOut)
async def update_candidate(
    candidate_id: str, 
    candidate_update: CandidateUpdate, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update candidate information"""
    candidate_repository = CandidateRepository(db)
    update_data = candidate_update.model_dump(exclude_unset=True)
    
    updated_candidate = await candidate_repository.update_candidate(candidate_id, update_data)
    if not updated_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return CandidateOut.model_validate(updated_candidate)

# Get candidate sessions
@router.get("/{candidate_id}/sessions", response_model=List[InterviewSessionOut])
async def get_candidate_sessions(
    candidate_id: str, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all interview sessions for a candidate"""
    session_repository = SessionRepository(db)
    sessions = await session_repository.get_sessions_by_candidate(candidate_id)
    return [InterviewSessionOut.model_validate(session) for session in sessions]

# Get candidate responses
@router.get("/{candidate_id}/responses")
async def get_candidate_responses(
    candidate_id: str, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all responses from a candidate"""
    session_repository = SessionRepository(db)
    sessions = await session_repository.get_sessions_by_candidate(candidate_id)
    
    # Get all responses for these sessions
    all_responses = []
    for session in sessions:
        responses = await session_repository.get_session_responses(session.id)
        all_responses.extend(responses)
    
    return all_responses

# Upload candidate resume
@router.post("/{candidate_id}/resume")
async def upload_resume(
    candidate_id: str, 
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload resume for a candidate"""
    candidate_repository = CandidateRepository(db)
    
    # Verify candidate exists
    candidate = await candidate_repository.get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Validate file type
    allowed_extensions = [".pdf", ".doc", ".docx"]
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads/resumes", exist_ok=True)
    
    # Generate unique filename
    filename = f"resume_{candidate_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{file_extension}"
    file_path = os.path.join("uploads/resumes", filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Update candidate with resume path
    await candidate_repository.update_resume_path(candidate_id, file_path)
    
    return {"message": "Resume uploaded successfully", "resume_path": file_path}

# Get candidate report
@router.get("/{candidate_id}/report")
async def get_candidate_report(
    candidate_id: str, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive report for a candidate"""
    candidate_repository = CandidateRepository(db)
    session_repository = SessionRepository(db)
    
    # Get candidate details
    candidate = await candidate_repository.get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get all sessions for the candidate
    sessions = await session_repository.get_sessions_by_candidate(candidate_id)
    
    # Get all responses
    all_responses = []
    for session in sessions:
        responses = await session_repository.get_session_responses(session.id)
        all_responses.extend(responses)
    
    # Calculate basic statistics
    total_sessions = len(sessions)
    completed_sessions = len([s for s in sessions if s.status == "completed"])
    total_responses = len(all_responses)
    
    # Mock scoring (in real implementation, this would use AI analysis)
    overall_score = 0
    communication_score = 0
    technical_score = 0
    
    if total_responses > 0:
        # Simple scoring based on response count and session completion
        overall_score = min(100, (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0)
        communication_score = min(100, (total_responses / (total_sessions * 5)) * 100)  # Assuming 5 questions per interview
        technical_score = overall_score * 0.8  # Mock technical score
    
    report = {
        "candidate_id": candidate_id,
        "candidate_name": candidate.name,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "total_responses": total_responses,
        "overall_score": round(overall_score, 2),
        "communication_score": round(communication_score, 2),
        "technical_score": round(technical_score, 2),
        "strengths": ["Good response rate", "Consistent participation"] if overall_score > 70 else ["Room for improvement"],
        "areas_for_improvement": ["Complete more sessions", "Provide detailed responses"] if overall_score < 70 else ["Maintain current performance"],
        "detailed_feedback": f"Candidate has participated in {total_sessions} interviews with {completed_sessions} completed sessions.",
        "recommendations": [
            "Continue participating in interviews",
            "Focus on completing full interview sessions",
            "Provide comprehensive responses"
        ],
        "generated_at": datetime.utcnow()
    }
    
    return report

# Delete candidate
@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: str, 
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a candidate and all associated data"""
    candidate_repository = CandidateRepository(db)
    session_repository = SessionRepository(db)
    
    # Verify candidate exists
    candidate = await candidate_repository.get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Delete all sessions for this candidate (this will cascade delete responses)
    sessions = await session_repository.get_sessions_by_candidate(candidate_id)
    for session in sessions:
        await session_repository.delete_session(session.id)
    
    # Delete the candidate
    success = await candidate_repository.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete candidate")
    
    return {"message": "Candidate and all associated data deleted successfully"}
