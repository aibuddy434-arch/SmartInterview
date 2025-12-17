import os
import tempfile
import whisper
from typing import Dict, List, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self):
        self.provider = settings.transcription_provider
        self.openai_api_key = settings.openai_api_key
        self.huggingface_api_key = settings.huggingface_api_key
        
        # Initialize Whisper model if using local Whisper
        if self.provider == "whisper" and not self.openai_api_key:
            try:
                self.whisper_model = whisper.load_model("base")
                logger.info("Loaded local Whisper model")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                self.whisper_model = None
    
    async def transcribe_audio(self, audio_file_path: str) -> Dict:
        """
        Transcribe audio file using configured provider
        """
        try:
            if self.provider == "whisper":
                if self.openai_api_key:
                    return await self._transcribe_with_openai_whisper(audio_file_path)
                else:
                    return await self._transcribe_with_local_whisper(audio_file_path)
            elif self.provider == "hf":
                return await self._transcribe_with_huggingface(audio_file_path)
            else:
                raise ValueError(f"Unsupported transcription provider: {self.provider}")
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
# In backend/services/transcription_service.py

    async def _transcribe_with_openai_whisper(self, audio_file_path: str) -> Dict:
        """
        Use OpenAI Whisper API for transcription (using openai>=1.0.0 syntax)
        """
        try:
            from openai import AsyncOpenAI, OpenAIError # Import specific error
            # Ensure API key is loaded from settings
            if not self.openai_api_key: 
                raise ValueError("OpenAI API key not configured.")
            client = AsyncOpenAI(api_key=self.openai_api_key) 
        except ImportError:
             logger.error("OpenAI v1.0+ library not installed (`pip install openai>=1.0.0`).")
             raise RuntimeError("OpenAI transcription dependency missing.")
        except Exception as client_err:
             logger.error(f"Failed to initialize OpenAI client: {client_err}")
             raise RuntimeError("OpenAI client initialization failed.")

        try:
            logger.info(f"Transcribing {audio_file_path} using OpenAI Whisper API...")
            with open(audio_file_path, "rb") as audio_file:
                # --- NEW OpenAI v1.0+ Syntax ---
                transcript_response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json", 
                )
                # --- End New Syntax ---

            full_text = transcript_response.text
            language = transcript_response.language
            segments_data = transcript_response.segments or [] 

            segments = [{"start": seg.get("start", 0), "end": seg.get("end", 0), "text": seg.get("text", "").strip()} for seg in segments_data]
            
            logger.info(f"OpenAI Transcription successful. Language: {language}")
            return {
                "text": full_text or "[Empty Transcript]", 
                "segments": segments,
                "language": language,
                "provider": "openai_whisper"
            }
        except OpenAIError as api_error:
             logger.error(f"OpenAI API error during transcription: {api_error}")
             if 'insufficient_quota' in str(api_error):
                 logger.error("OpenAI Quota Exceeded during transcription.")
             raise RuntimeError(f"OpenAI API Error: {api_error}")
        except Exception as e:
            logger.error(f"OpenAI Whisper transcription failed unexpectedly: {e}")
            raise
    
    async def _transcribe_with_local_whisper(self, audio_file_path: str) -> Dict:
        """
        Use local Whisper model for transcription
        """
        if not self.whisper_model:
            raise RuntimeError("Local Whisper model not loaded")
        
        try:
            result = self.whisper_model.transcribe(
                audio_file_path,
                verbose=False,
                word_timestamps=True
            )
            
            # Extract segments with timestamps
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "").strip()
                })
            
            return {
                "text": result.get("text", ""),
                "segments": segments,
                "language": result.get("language", "en"),
                "provider": "local_whisper"
            }
        except Exception as e:
            logger.error(f"Local Whisper transcription failed: {e}")
            raise
    
    async def _transcribe_with_huggingface(self, audio_file_path: str) -> Dict:
        """
        Use HuggingFace models for transcription
        """
        try:
            from transformers import pipeline
            
            # Use a pre-trained speech recognition model
            transcriber = pipeline(
                "automatic-speech-recognition",
                model="facebook/wav2vec2-base-960h",
                token=self.huggingface_api_key if self.huggingface_api_key else None
            )
            
            result = transcriber(audio_file_path, return_timestamps="word")
            
            # Extract segments with timestamps
            segments = []
            if "chunks" in result:
                for chunk in result["chunks"]:
                    segments.append({
                        "start": chunk.get("timestamp", [0, 0])[0],
                        "end": chunk.get("timestamp", [0, 0])[1],
                        "text": chunk.get("text", "").strip()
                    })
            
            return {
                "text": result.get("text", ""),
                "segments": segments,
                "language": "en",  # Default for wav2vec2
                "provider": "huggingface"
            }
        except Exception as e:
            logger.error(f"HuggingFace transcription failed: {e}")
            raise

# Global instance
transcription_service = TranscriptionService()


