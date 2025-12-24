# Replace the entire contents of backend/routes/public.py with this file

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.repositories.interview_repository import InterviewRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.session_repository import SessionRepository
from services.report_service import get_report_service # Assuming this exists
from models.interview import InterviewConfig, InterviewSessionOut, TTSRequest
from models.candidate import Candidate, CandidateCreate, CandidateResponse, CandidateOut
from models.interview import InterviewSession
from models.response import StandardResponse, success_response, error_response
import secrets
import aiofiles
import os
from datetime import datetime
import logging

# --- New/Updated Imports ---
from fastapi import Response
from services.tts_service import tts_service
from services.transcription_service import transcription_service
from services.resume_parser import resume_parser_service
from services.ai_question_service import ai_question_service
# --- End New/Updated Imports ---

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/interview/{interview_id}")
async def get_public_interview(
    interview_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get interview configuration for public access using interview ID"""
    interview_repository = InterviewRepository(db)
    interview = await interview_repository.get_interview_config_by_id(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if not interview.is_active:
        raise HTTPException(status_code=404, detail="Interview is no longer active")
    # Eager load questions if they aren't loaded by default
    await db.refresh(interview, ['questions'])
    
    # Calculate time per question
    time_per_question_seconds = None
    total_time_seconds = None
    if interview.time_limit and interview.number_of_questions and interview.number_of_questions > 0:
        total_time_seconds = interview.time_limit * 60
        time_per_question_seconds = total_time_seconds // interview.number_of_questions
    
    # Build response with time info
    response = {
        "id": interview.id,
        "job_role": interview.job_role,
        "job_description": interview.job_description,
        "interview_type": interview.interview_type,
        "difficulty": interview.difficulty,
        "focus": interview.focus,
        "time_limit": interview.time_limit,
        "avatar": interview.avatar,
        "voice": interview.voice,
        "number_of_questions": interview.number_of_questions,
        "questions": [{
            "id": q.id, 
            "text": q.text, 
            "tags": q.tags, 
            "generated_by": q.generated_by,
            "suggested_time_seconds": getattr(q, 'suggested_time_seconds', 120) or 120
        } for q in interview.questions],
        "created_by": interview.created_by,
        "created_at": interview.created_at,
        "updated_at": interview.updated_at,
        "is_active": interview.is_active,
        "shareable_link": interview.shareable_link,
        # New time fields for timer
        "time_per_question_seconds": time_per_question_seconds,
        "total_time_seconds": total_time_seconds,
        "estimated_duration": interview.time_limit  # In minutes
    }
    
    return response

@router.post("/interview/{interview_id}/register", response_model=StandardResponse)
async def register_candidate(
    interview_id: str,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    resume_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """Register a candidate for an interview and create session"""
    interview_repository = InterviewRepository(db)
    interview = await interview_repository.get_interview_config_by_id(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if not interview.is_active:
        raise HTTPException(status_code=404, detail="Interview is no longer active")
    
    candidate_repository = CandidateRepository(db)
    candidate_dict = {"name": name, "email": email, "phone": phone}
    
    if resume_file:
        try:
            upload_dir = "uploads/resumes"
            os.makedirs(upload_dir, exist_ok=True)
            # Use original filename extension if possible, or default to .pdf if unclear
            file_extension = os.path.splitext(resume_file.filename)[1] or '.pdf'
            resume_filename = f"resume_{interview_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{file_extension}"
            resume_path = os.path.join(upload_dir, resume_filename)
            
            async with aiofiles.open(resume_path, 'wb') as f:
                content = await resume_file.read()
                await f.write(content)
            candidate_dict["resume_path"] = resume_path
        except Exception as e:
            logger.error(f"Failed to save resume: {e}")
            # Decide if this should be a critical error or just a warning
            # For now, just log and continue without resume
            pass 
    
    candidate = await candidate_repository.create_candidate(candidate_dict)
    
    session_repository = SessionRepository(db)
    session_id = secrets.token_urlsafe(16)
    session_data = {
        "session_id": session_id,
        "interview_config_id": interview_id,
        "candidate_id": candidate.id,
        "status": "created",
        "current_question": 0, # Represents the index of the next question to be asked (0-based)
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await session_repository.create_session(session_data)
    candidate_out = CandidateOut.model_validate(candidate)
    
    return success_response(
        data={"candidate": candidate_out, "session_id": session_id},
        message="Candidate registered and session created successfully"
    )

@router.post("/session/{session_id}/start", response_model=StandardResponse)
async def start_interview_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Start an interview session"""
    session_repository = SessionRepository(db)
    session = await session_repository.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if not session.candidate_id:
        raise HTTPException(status_code=400, detail="No candidate registered for this session")

    update_data = {
        "status": "in_progress",
        "start_time": datetime.utcnow(),
        "current_question": 0, # Start at the beginning (index 0)
        "updated_at": datetime.utcnow()
    }
    await session_repository.update_session(session_id, update_data)
    return success_response(
        data={"session_id": session_id},
        message="Interview session started successfully"
    )

@router.get("/session/{session_id}", response_model=InterviewSessionOut)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get interview session details"""
    session_repository = SessionRepository(db)
    session = await session_repository.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return InterviewSessionOut.model_validate(session)

@router.post("/session/{session_id}/submit-response", response_model=StandardResponse)
async def submit_response(
    session_id: str,
    question_number: int = Form(...), # Number of the question JUST answered (1-based from frontend)
    audio_file: UploadFile = File(...),
    live_transcript: Optional[str] = Form(None), # NEW: Live transcript from browser as fallback
    question_text: Optional[str] = Form(None),  # NEW: The actual question text that was asked
    question_type: Optional[str] = Form("preset"),  # NEW: 'preset', 'follow_up', or 'resume'
    video_file: Optional[UploadFile] = File(None), # Keep video_file if you use it
    db: AsyncSession = Depends(get_db)
):
    """
    Submit audio response, transcribe, get AI decision for next step.
    Uses live_transcript from browser as fallback if audio transcription fails.
    """
    logger.info(f"Received response for session {session_id}, question number {question_number}")
    if live_transcript:
        logger.info(f"Received live transcript from browser: {len(live_transcript)} characters")
    
    session_repository = SessionRepository(db)
    interview_repository = InterviewRepository(db)
    candidate_repository = CandidateRepository(db)

    # 1. Verify session and get related data
    session = await session_repository.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session is not in progress")

    interview_config = await interview_repository.get_interview_config_by_id(session.interview_config_id)
    candidate = await candidate_repository.get_candidate_by_id(session.candidate_id)
    
    if not interview_config or not candidate:
        raise HTTPException(status_code=404, detail="Interview or candidate data not found")
    
    # Eager load questions for the interview config
    await db.refresh(interview_config, ['questions'])
    preset_questions = interview_config.questions
    
    # --- 2. Save and Transcribe Audio ---
    audio_path = None
    transcript_text = None  # Changed from default, we'll set based on best available
    try:
        upload_dir = "uploads/audio"
        os.makedirs(upload_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Detect correct file extension from content type
        content_type = audio_file.content_type or ""
        if "webm" in content_type:
            file_ext = ".webm"
        elif "ogg" in content_type:
            file_ext = ".ogg"
        elif "mp3" in content_type or "mpeg" in content_type:
            file_ext = ".mp3"
        else:
            file_ext = ".wav"
        
        audio_filename = f"audio_{session_id}_{question_number}_{timestamp}{file_ext}"
        audio_path = os.path.join(upload_dir, audio_filename)

        async with aiofiles.open(audio_path, 'wb') as f:
            content = await audio_file.read()
            await f.write(content)
        
        logger.info(f"Audio file saved: {audio_path}")
        
        # --- SPEED OPTIMIZATION: Use live transcript FIRST if available ---
        # Browser's live transcript is instant, server transcription takes 5-10 seconds
        if live_transcript and len(live_transcript.strip()) > 5:
            transcript_text = live_transcript.strip()
            logger.info(f"Using browser live transcript (fast): {len(transcript_text)} characters")
        else:
            # Only do server-side transcription if no live transcript
            logger.info(f"No live transcript, falling back to server transcription: {audio_path}")
            transcription_result = await transcription_service.transcribe_audio(audio_path)
            audio_transcript = transcription_result.get("text", "")
            
            # Check if transcription was successful (not empty or failed message)
            if audio_transcript and not audio_transcript.startswith("[") and len(audio_transcript.strip()) > 5:
                transcript_text = audio_transcript
                logger.info(f"Audio transcription successful: {len(transcript_text)} characters")
            else:
                logger.warning(f"Audio transcription failed or empty: '{audio_transcript}'")
                transcript_text = "[No response recorded]"

    except Exception as e:
        logger.error(f"Error during audio processing/transcription: {str(e)}")
        # Try to use live transcript as last resort
        if live_transcript and len(live_transcript.strip()) > 5:
            transcript_text = live_transcript.strip()
            logger.info(f"Using live transcript after error: {len(transcript_text)} characters")
        else:
            transcript_text = "[No response recorded]"

    # --- 3. Save Response to DB ---
    response_data = {
        "session_id": session_id,
        "question_number": question_number, # The 1-based number
        "question_text": question_text,  # NEW: Store actual question text
        "question_type": question_type or "preset",  # NEW: 'preset', 'follow_up', or 'resume'
        "transcript": transcript_text,
        "audio_path": audio_path,
        "created_at": datetime.utcnow()
    }
    # Handle video file if present
    if video_file:
        # ... (Your video saving logic) ...
        # response_data["video_path"] = video_path
        pass

    response = await session_repository.create_response(response_data)
    logger.info(f"Response record created with ID: {response.id}")

    # --- 4. Get Context for AI ---
    # Build session history
    session_history = []
    all_responses = await session_repository.get_session_responses(session_id)
    for resp in all_responses:
        q_index = resp.question_number - 1  # Convert to 0-based
        question_text = ""
        if q_index >= 0 and q_index < len(preset_questions):
            question_text = preset_questions[q_index].text
        
        session_history.append({
            "question": question_text,
            "answer": resp.transcript or ""
        })

    # Parse resume
    resume_text = ""
    if candidate.resume_path and os.path.exists(candidate.resume_path):
        try:
            logger.info(f"Parsing resume: {candidate.resume_path}")
            resume_text = await resume_parser_service.parse_resume(candidate.resume_path)
            logger.info(f"Resume parsed: {len(resume_text)} characters")
        except Exception as e:
            logger.error(f"Resume parsing failed: {str(e)}")
            resume_text = "" # Keep it as empty string on failure

    # --- 5. Call AI Decision Service ---
    # We pass the 0-based index of the question that was just answered
    current_question_idx = question_number - 1 
    
    # Calculate elapsed time since interview started
    elapsed_seconds = 0
    time_limit_seconds = (interview_config.time_limit or 10) * 60  # Default 10 min in seconds
    
    if session.start_time:
        elapsed_seconds = int((datetime.utcnow() - session.start_time).total_seconds())
        logger.info(f"Interview elapsed time: {elapsed_seconds}s of {time_limit_seconds}s remaining: {time_limit_seconds - elapsed_seconds}s")
    
    try:
        logger.info(f"Calling AI service to determine next step... (After Q index {current_question_idx})")
        
        next_step = await ai_question_service.determine_next_step(
            interview_config=interview_config,
            session_history=session_history,
            current_question_index=current_question_idx,
            candidate_transcript=transcript_text,
            resume_text=resume_text,
            elapsed_seconds=elapsed_seconds,  # NEW: Pass elapsed time
            time_limit_seconds=time_limit_seconds  # NEW: Pass time limit
        )
        # --- *** END OF CORRECTION *** ---
        
        logger.info(f"AI decision: {next_step}")
    except Exception as e:
        logger.error(f"AI decision service failed: {str(e)}")
        # Fallback: move to next preset question
        next_preset_idx = current_question_idx + 1
        if next_preset_idx < len(preset_questions):
            next_step = {
                "action": "preset",
                "question_text": preset_questions[next_preset_idx].text,
                "next_index": next_preset_idx + 1 # 1-based index
            }
        else:
            next_step = {"action": "complete"}
    
    # --- 6. Process the AI decision ---
    action = next_step.get("action", "complete")
    
    if action == "complete":
        logger.info("AI decided to complete the interview.")
        await session_repository.update_session(session_id, {
            "status": "completed",
            "end_time": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        return success_response(
            data={"action": "complete", "message": "Interview completed"},
            message="Interview completed successfully"
        )
    
    elif action in ["preset", "follow_up", "resume"]:
        question_text = next_step.get("question_text")
        next_index = next_step.get("next_index") # 1-based index from AI service
        
        if not question_text:
            logger.error(f"AI action '{action}' but no question text provided. Completing.")
            await complete_session(session_id, db) # Use the existing complete_session function
            return success_response(data={"action": "complete"}, message="Interview ended.")

        # Update session 'current_question' index *only* if it's a preset question
        # This index tracks our progress through the *preset* list
        if action == "preset" and next_index is not None:
            await session_repository.update_session(session_id, {
                "current_question": next_index, # Store 1-based index
                "updated_at": datetime.utcnow()
            })
        
        return success_response(
            data={
                "action": action,
                "question_text": question_text,
                "next_index": next_index, # Pass this to frontend
                "suggested_time_seconds": next_step.get("suggested_time_seconds", 120) # Dynamic timing
            },
            message="Response submitted, next question provided."
        )

    else:
        # Unknown action, fallback to complete
        logger.warning(f"Unknown action '{action}', completing interview.")
        await complete_session(session_id, db)
        return success_response(
            data={"action": "complete"},
            message="Interview completed."
        )

# --- complete_session function (slight modification for reuse) ---
@router.post("/session/{session_id}/complete", response_model=StandardResponse)
async def complete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Complete an interview session"""
    session_repository = SessionRepository(db)
    session = await session_repository.get_session_by_id(session_id)
    
    if not session:
        logger.warning(f"Attempted to complete non-existent session: {session_id}")
        # Return success as it's already "gone"
        return success_response(data={"session_id": session_id}, message="Session not found, presumed complete.")
    
    if session.status == "completed":
        # Already done, just return success
        return success_response(data={"session_id": session_id}, message="Session already completed.")

    if session.status != "in_progress":
        logger.warning(f"Attempted to complete session {session_id} from invalid state: {session.status}")
        raise HTTPException(status_code=400, detail=f"Session cannot be completed from state: {session.status}")
    
    update_data = {
        "status": "completed",
        "end_time": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await session_repository.update_session(session_id, update_data)
    
    return success_response(
        data={"session_id": session_id},
        message="Session completed successfully"
    )

# --- get_session_responses function ---
@router.get("/session/{session_id}/responses", response_model=List[CandidateResponse])
async def get_session_responses(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    session_repository = SessionRepository(db)
    session = await session_repository.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    responses = await session_repository.get_session_responses(session_id)
    return responses

# --- get_interview_report function ---
@router.get("/session/{session_id}/report")
async def get_interview_report(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = get_report_service(db)
        report = await report_service.generate_interview_report(session_id)
        report_id = await report_service.save_report(session_id, report)
        report["report_id"] = report_id
        return report
    except Exception as e:
        logger.error(f"Report generation failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

# --- public_text_to_speech function ---
@router.post("/tts", response_class=Response)
async def public_text_to_speech(
    payload: TTSRequest,
):
    """Public endpoint for Text-to-Speech synthesis. Accepts JSON."""
    try:
        if not payload.text or not payload.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        logger.info(f"TTS request for text: '{payload.text[:50]}...'")
        audio_file_path = await tts_service.generate_speech(payload.text, payload.voice or "default")
        
        if not audio_file_path or not os.path.exists(audio_file_path):
             logger.error(f"TTS service failed to return valid file path for: {payload.text[:50]}...")
             raise HTTPException(status_code=500, detail="Failed to generate speech file")

        logger.info(f"TTS generated file: {audio_file_path}")

        async with aiofiles.open(audio_file_path, 'rb') as f:
             audio_content = await f.read()

        # Detect content type from file extension
        file_ext = os.path.splitext(audio_file_path)[1].lower()
        if file_ext == ".mp3":
            media_type = "audio/mpeg"
        elif file_ext == ".wav":
            media_type = "audio/wav"
        elif file_ext == ".ogg":
            media_type = "audio/ogg"
        else:
            media_type = "audio/mpeg"  # Default for Edge TTS

        try:
            os.remove(audio_file_path)
        except OSError:
            logger.warning(f"Could not remove temporary TTS file: {audio_file_path}")
            
        logger.info(f"TTS returning {len(audio_content)} bytes as {media_type}")
        return Response(content=audio_content, media_type=media_type)
        
    except Exception as e:
        logger.error(f"Public TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS Error: {str(e)}")