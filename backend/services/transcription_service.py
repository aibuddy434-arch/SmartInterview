import os
import logging
from typing import Dict, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self):
        self.provider = settings.transcription_provider
        self.google_api_key = settings.google_api_key
        self.openai_api_key = settings.openai_api_key
        self.huggingface_api_key = settings.huggingface_api_key
        self.whisper_model = None
        
        # Log which transcription method will be used
        if self.google_api_key:
            logger.info("Using Google Speech-to-Text for transcription (API key available)")
        elif self.provider == "whisper" and not self.openai_api_key:
            try:
                import whisper
                self.whisper_model = whisper.load_model("base")
                logger.info("Loaded local Whisper model for transcription")
            except Exception as e:
                logger.warning(f"Failed to load Whisper model: {e}. Will try Google STT if available.")
    
    async def transcribe_audio(self, audio_file_path: str) -> Dict:
        """
        Transcribe audio file using best available provider.
        Priority: Google STT > OpenAI Whisper > Local Whisper > HuggingFace
        """
        logger.info(f"Transcribing audio file: {audio_file_path}")
        
        # Try Google Speech-to-Text first (most reliable with existing API key)
        if self.google_api_key:
            try:
                return await self._transcribe_with_google(audio_file_path)
            except Exception as e:
                logger.warning(f"Google STT failed: {e}. Trying fallback...")
        
        # Fallback to OpenAI Whisper API
        if self.openai_api_key:
            try:
                return await self._transcribe_with_openai_whisper(audio_file_path)
            except Exception as e:
                logger.warning(f"OpenAI Whisper failed: {e}. Trying fallback...")
        
        # Fallback to local Whisper
        if self.whisper_model:
            try:
                return await self._transcribe_with_local_whisper(audio_file_path)
            except Exception as e:
                logger.warning(f"Local Whisper failed: {e}. Trying fallback...")
        
        # Final fallback - return empty transcript with error
        logger.error("All transcription methods failed!")
        return {
            "text": "[No transcription available - all methods failed]",
            "segments": [],
            "language": "en",
            "provider": "none"
        }
    
    async def _transcribe_with_google(self, audio_file_path: str) -> Dict:
        """
        Use Google Cloud Speech-to-Text API for transcription.
        Uses the existing GOOGLE_API_KEY from settings.
        """
        import aiohttp
        import base64
        
        logger.info(f"Transcribing {audio_file_path} using Google Speech-to-Text...")
        
        # Read and encode audio file
        with open(audio_file_path, "rb") as audio_file:
            audio_content = base64.b64encode(audio_file.read()).decode("utf-8")
        
        # Determine audio encoding based on file extension
        file_ext = os.path.splitext(audio_file_path)[1].lower()
        
        # Browser typically records as webm/opus or wav
        # Google STT supports: LINEAR16, FLAC, MULAW, AMR, OGG_OPUS, WEBM_OPUS
        if file_ext == ".webm":
            encoding = "WEBM_OPUS"
        elif file_ext == ".ogg":
            encoding = "OGG_OPUS"
        elif file_ext == ".mp3":
            encoding = "MP3"
        elif file_ext == ".flac":
            encoding = "FLAC"
        else:
            # Default for WAV - try to detect sample rate
            encoding = "LINEAR16"
        
        # For webm/opus, we don't need sample rate
        sample_rate = None if encoding in ["WEBM_OPUS", "OGG_OPUS", "MP3"] else 48000
        
        # Build request payload
        config = {
            "encoding": encoding,
            "languageCode": "en-US",
            "enableAutomaticPunctuation": True,
            "model": "default"
        }
        
        # Only add sample rate for formats that need it
        if sample_rate:
            config["sampleRateHertz"] = sample_rate
        
        payload = {
            "config": config,
            "audio": {
                "content": audio_content
            }
        }
        
        logger.info(f"Sending to Google STT with encoding: {encoding}")
        
        # Make API request
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={self.google_api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Google STT API error: {response.status} - {error_text}")
                    raise RuntimeError(f"Google STT API error: {response.status} - {error_text}")
                
                result = await response.json()
        
        # Parse response
        full_text = ""
        segments = []
        
        if "results" in result:
            for res in result["results"]:
                if "alternatives" in res and len(res["alternatives"]) > 0:
                    alt = res["alternatives"][0]
                    full_text += alt.get("transcript", "") + " "
                    
                    # Extract word-level timestamps if available
                    if "words" in alt:
                        for word_info in alt["words"]:
                            start_time = float(word_info.get("startTime", "0s").rstrip("s"))
                            end_time = float(word_info.get("endTime", "0s").rstrip("s"))
                            segments.append({
                                "start": start_time,
                                "end": end_time,
                                "text": word_info.get("word", "")
                            })
        
        full_text = full_text.strip()
        if not full_text:
            full_text = "[Empty response - no speech detected]"
        
        logger.info(f"Google STT successful: {len(full_text)} characters transcribed")
        
        return {
            "text": full_text,
            "segments": segments,
            "language": "en",
            "provider": "google_stt"
        }

    async def _transcribe_with_openai_whisper(self, audio_file_path: str) -> Dict:
        """
        Use OpenAI Whisper API for transcription
        """
        try:
            from openai import AsyncOpenAI, OpenAIError
            if not self.openai_api_key: 
                raise ValueError("OpenAI API key not configured.")
            client = AsyncOpenAI(api_key=self.openai_api_key)
        except ImportError:
            logger.error("OpenAI library not installed")
            raise RuntimeError("OpenAI transcription dependency missing.")
        except Exception as client_err:
            logger.error(f"Failed to initialize OpenAI client: {client_err}")
            raise RuntimeError("OpenAI client initialization failed.")

        try:
            logger.info(f"Transcribing {audio_file_path} using OpenAI Whisper API...")
            with open(audio_file_path, "rb") as audio_file:
                transcript_response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json", 
                )

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
        except Exception as e:
            logger.error(f"OpenAI Whisper transcription failed: {e}")
            raise
    
    async def _transcribe_with_local_whisper(self, audio_file_path: str) -> Dict:
        """
        Use local Whisper model for transcription
        """
        if not self.whisper_model:
            raise RuntimeError("Local Whisper model not loaded")
        
        try:
            logger.info(f"Transcribing {audio_file_path} using local Whisper...")
            result = self.whisper_model.transcribe(
                audio_file_path,
                verbose=False,
                word_timestamps=True
            )
            
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "").strip()
                })
            
            logger.info(f"Local Whisper transcription successful")
            return {
                "text": result.get("text", ""),
                "segments": segments,
                "language": result.get("language", "en"),
                "provider": "local_whisper"
            }
        except Exception as e:
            logger.error(f"Local Whisper transcription failed: {e}")
            raise

# Global instance
transcription_service = TranscriptionService()
