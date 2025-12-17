from fastapi import APIRouter, HTTPException, status, Depends, Form
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.interview import InterviewConfigCreate, InterviewConfig, Question
from models.user import User
from utils.auth import get_current_admin_user
from app.db import get_db
from services.interview_service import get_interview_service
from services.ai_question_service import ai_question_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/create", response_model=InterviewConfig, status_code=status.HTTP_201_CREATED)
async def create_interview_config(
    config_data: InterviewConfigCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new interview configuration
    """
    try:
        # Validate that the user is an admin or interviewer
        if current_user.role not in ["admin", "interviewer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins and interviewers can create interview configurations"
            )
        
        # Get interview service with db session
        interview_service = get_interview_service(db)
        
        # Create the interview configuration (service will set created_by from current_user.id)
        created_config = await interview_service.create_interview_config(
            config_data, str(current_user.id)
        )
        
        logger.info(f"Interview config created by user {current_user.id}: {created_config.id}")
        
        return created_config
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in create interview config: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to create interview config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview configuration: {str(e)}"
        )

@router.post("/generate-questions")
async def generate_questions(
    job_role: str = Form(...),
    job_description: str = Form(...),
    focus_areas: List[str] = Form(...),
    difficulty: str = Form(...),
    number_of_questions: int = Form(...),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Generate AI-powered interview questions
    """
    try:
        # Validate that the user is an admin or interviewer
        if current_user.role not in ["admin", "interviewer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins and interviewers can generate questions"
            )
        
        # Convert focus areas to enum values
        from models.interview import FocusArea, DifficultyLevel
        
        try:
            focus_area_enums = [FocusArea(focus) for focus in focus_areas]
            difficulty_enum = DifficultyLevel(difficulty)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid enum values: {str(e)}"
            )
        
        # Generate questions using AI service
        questions = await ai_question_service.generate_questions(
            job_role=job_role,
            job_description=job_description,
            focus_areas=focus_area_enums,
            difficulty=difficulty_enum,
            number_of_questions=number_of_questions
        )
        
        logger.info(f"Generated {len(questions)} questions for user {current_user.id}")
        
        return {
            "success": True,
            "questions": questions,
            "count": len(questions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions: {str(e)}"
        )

@router.get("/configs", response_model=List[InterviewConfig])
async def get_user_interview_configs(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all interview configurations created by the current user
    """
    try:
        interview_service = get_interview_service(db)
        configs = await interview_service.get_interview_configs_by_user(str(current_user.id))
        return configs
        
    except Exception as e:
        logger.error(f"Failed to get interview configs for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview configurations"
        )

@router.get("/configs/{config_id}", response_model=InterviewConfig)
async def get_interview_config(
    config_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific interview configuration by ID
    """
    try:
        interview_service = get_interview_service(db)
        config = await interview_service.get_interview_config(config_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview configuration not found"
            )
        
        # Check if user owns this config
        if config.created_by != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this interview configuration"
            )
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get interview config {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview configuration"
        )

@router.put("/configs/{config_id}", response_model=InterviewConfig)
async def update_interview_config(
    config_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an interview configuration
    """
    try:
        interview_service = get_interview_service(db)
        updated_config = await interview_service.update_interview_config(
            config_id, update_data, str(current_user.id)
        )
        
        if not updated_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview configuration not found or access denied"
            )
        
        logger.info(f"Interview config {config_id} updated by user {current_user.id}")
        return updated_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update interview config {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update interview configuration"
        )

@router.delete("/configs/{config_id}")
async def delete_interview_config(
    config_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an interview configuration
    """
    try:
        interview_service = get_interview_service(db)
        success = await interview_service.delete_interview_config(
            config_id, str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview configuration not found or access denied"
            )
        
        logger.info(f"Interview config {config_id} deleted by user {current_user.id}")
        
        return {"success": True, "message": "Interview configuration deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete interview config {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete interview configuration"
        )

@router.post("/configs/{config_id}/questions")
async def add_questions_to_config(
    config_id: str,
    questions: List[Question],
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add or update questions for an interview configuration
    """
    try:
        interview_service = get_interview_service(db)
        updated_config = await interview_service.add_questions_to_config(
            config_id, questions, str(current_user.id)
        )
        
        if not updated_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview configuration not found or access denied"
            )
        
        logger.info(f"Questions added to config {config_id} by user {current_user.id}")
        
        return {
            "success": True,
            "config": updated_config,
            "message": f"Added {len(questions)} questions to interview configuration"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add questions to config {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add questions to interview configuration"
        )

@router.get("/sessions/completed")
async def get_completed_sessions(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all completed interview sessions for the current user's interviews
    """
    try:
        from app.repositories.session_repository import SessionRepository
        from app.repositories.interview_repository import InterviewRepository
        from app.repositories.candidate_repository import CandidateRepository
        
        interview_repository = InterviewRepository(db)
        session_repository = SessionRepository(db)
        candidate_repository = CandidateRepository(db)
        
        # Get all interview configs for this user
        configs = await interview_repository.get_interview_configs_by_user(str(current_user.id))
        
        completed_sessions = []
        for config in configs:
            sessions = await session_repository.get_sessions_by_interview_config(config.id)
            for session in sessions:
                if session.status == "completed":
                    candidate = await candidate_repository.get_candidate_by_id(session.candidate_id)
                    completed_sessions.append({
                        "session_id": session.session_id,
                        "interview_config_id": config.id,
                        "job_role": config.job_role,
                        "candidate_name": candidate.name if candidate else "Unknown",
                        "candidate_email": candidate.email if candidate else "",
                        "start_time": session.start_time,
                        "end_time": session.end_time,
                        "status": session.status,
                        "score": session.score
                    })
        
        # Sort by end_time descending
        completed_sessions.sort(key=lambda x: x.get("end_time") or "", reverse=True)
        
        return {"sessions": completed_sessions, "count": len(completed_sessions)}
        
    except Exception as e:
        logger.error(f"Failed to get completed sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve completed sessions"
        )

@router.get("/configs/{config_id}/sessions")
async def get_config_sessions(
    config_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all sessions for a specific interview configuration
    """
    try:
        from app.repositories.session_repository import SessionRepository
        from app.repositories.interview_repository import InterviewRepository
        from app.repositories.candidate_repository import CandidateRepository
        
        interview_repository = InterviewRepository(db)
        session_repository = SessionRepository(db)
        candidate_repository = CandidateRepository(db)
        
        # Verify user owns this config
        config = await interview_repository.get_interview_config(config_id)
        if not config or config.created_by != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview configuration not found"
            )
        
        sessions = await session_repository.get_sessions_by_interview_config(config_id)
        
        session_list = []
        for session in sessions:
            candidate = await candidate_repository.get_candidate_by_id(session.candidate_id)
            session_list.append({
                "session_id": session.session_id,
                "candidate_name": candidate.name if candidate else "Unknown",
                "candidate_email": candidate.email if candidate else "",
                "start_time": session.start_time,
                "end_time": session.end_time,
                "status": session.status,
                "score": session.score,
                "current_question": session.current_question
            })
        
        return {"sessions": session_list, "config": {"id": config.id, "job_role": config.job_role}}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sessions for config {config_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )
