from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional
import os
import tempfile
import aiofiles
from app.db import get_db
from models.user import User
from utils.auth import get_current_admin_user
from services.transcription_service import transcription_service
from services.tts_service import tts_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(
    media_id: str = Form(...),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Transcribe audio file using configured transcription service
    """
    try:
        # Get file from GridFS (assuming media_id is stored there)
        # For now, we'll work with file paths, but in production you'd use GridFS
        
        # Create a temporary file path for demonstration
        # In real implementation, you'd retrieve from GridFS
        temp_file_path = f"/tmp/{media_id}.wav"
        
        if not os.path.exists(temp_file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found"
            )
        
        # Transcribe the audio
        result = await transcription_service.transcribe_audio(temp_file_path)
        
        return {
            "success": True,
            "transcript": result["text"],
            "segments": result["segments"],
            "language": result["language"],
            "provider": result["provider"]
        }
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )

@router.post("/tts")
async def generate_speech(
    text: str = Form(...),
    voice: str = Form("default"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Generate speech from text using configured TTS service
    """
    try:
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        # Generate speech
        audio_file_path = await tts_service.generate_speech(text, voice)
        
        # Return the audio file
        return FileResponse(
            audio_file_path,
            media_type="audio/wav",
            filename="generated_speech.wav"
        )
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS generation failed: {str(e)}"
        )

@router.get("/voices")
async def get_available_voices(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get available voices for TTS service
    """
    try:
        voices = tts_service.get_available_voices()
        return voices
    except Exception as e:
        logger.error(f"Failed to get voices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get voices: {str(e)}"
        )

@router.get("/health")
async def ai_services_health():
    """
    Check health of AI services
    """
    try:
        health_status = {
            "transcription": {
                "provider": transcription_service.provider,
                "status": "healthy" if transcription_service.whisper_model or transcription_service.openai_api_key else "unhealthy"
            },
            "tts": {
                "provider": tts_service.provider,
                "status": "healthy" if (tts_service.coqui_tts or tts_service.hf_model) else "unhealthy"
            }
        }
        
        return {
            "status": "healthy",
            "services": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


