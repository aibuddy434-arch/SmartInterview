import os
import tempfile
import asyncio
from typing import Dict, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.provider = settings.tts_provider
        self.huggingface_api_key = settings.huggingface_api_key
        
        # Initialize TTS models
        self.coqui_tts = None
        self.hf_tts = None
        self.edge_tts_available = False
        
        # ALWAYS try Edge TTS first (it's the fastest and best quality)
        self._init_edge_tts()
        
        # If Edge TTS not available, try other providers
        if not self.edge_tts_available:
            if self.provider == "coqui" or self.provider == "edge":
                self._init_coqui_tts()
            elif self.provider == "hf":
                self._init_huggingface_tts()
    
    def _init_edge_tts(self):
        """Initialize Edge TTS (Microsoft's free cloud TTS)"""
        try:
            import edge_tts
            self.edge_tts_available = True
            logger.info("✅ Edge TTS initialized successfully (fast cloud-based TTS)")
        except ImportError as e:
            logger.warning(f"Edge TTS not available: {e}. Will fall back to other TTS providers.")
            self.edge_tts_available = False
    
    def _init_coqui_tts(self):
        """Initialize Coqui TTS with Windows compatibility"""
        try:
            import platform
            import warnings
            
            # Suppress specific warnings during initialization
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="TTS")
                warnings.filterwarnings("ignore", category=FutureWarning, module="TTS")
                
                from TTS.api import TTS
                
                if platform.system() == "Windows":
                    logger.info("Initializing Coqui TTS on Windows with explicit model selection...")
                
                # Use a lightweight model that works better on Windows
                # Try multiple models in order of preference
                models_to_try = [
                    "tts_models/en/ljspeech/tacotron2-DDC",
                    "tts_models/en/ljspeech/fast_pitch",
                    "tts_models/en/vctk/vits"
                ]
                
                for model_name in models_to_try:
                    try:
                        # Initialize with explicit parameters to avoid fallback warnings
                        self.coqui_tts = TTS(
                            model_name=model_name, 
                            progress_bar=False,
                            gpu=False  # Explicitly disable GPU to avoid CUDA warnings
                        )
                        logger.info(f"Coqui TTS initialized successfully with model: {model_name}")
                        break
                    except Exception as model_error:
                        logger.warning(f"Failed to load model {model_name}: {model_error}")
                        continue
                
                if not self.coqui_tts:
                    raise Exception("No Coqui TTS models could be loaded")
                
        except ImportError as e:
            logger.warning(f"Coqui TTS not available: {e}. TTS functionality will be disabled.")
            self.coqui_tts = None
        except Exception as e:
            logger.warning(f"Failed to initialize Coqui TTS: {e}. TTS functionality will be disabled.")
            self.coqui_tts = None
    
    def _init_huggingface_tts(self):
        """Initialize HuggingFace TTS"""
        try:
            from transformers import VitsModel, AutoTokenizer
            import torch
            
            model_name = "facebook/mms-tts-eng"
            self.hf_model = VitsModel.from_pretrained(model_name)
            self.hf_tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            if torch.cuda.is_available():
                self.hf_model = self.hf_model.to("cuda")
            
            logger.info("HuggingFace TTS initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace TTS: {e}")
            self.hf_model = None
            self.hf_tokenizer = None
    
    async def generate_speech(self, text: str, voice: str = "default") -> str:
        """
        Generate speech from text and return the file path
        """
        try:
            # Try Edge TTS first (fastest)
            if self.edge_tts_available:
                return await self._generate_with_edge_tts(text, voice)
            elif self.provider == "coqui" and self.coqui_tts:
                return await self._generate_with_coqui(text, voice)
            elif self.provider == "hf" and self.hf_model:
                return await self._generate_with_huggingface(text, voice)
            else:
                # Fallback: return a placeholder file or raise a clear error
                logger.warning(f"TTS provider {self.provider} not available. Using fallback.")
                return await self._generate_fallback(text, voice)
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            # Try fallback before giving up
            try:
                return await self._generate_fallback(text, voice)
            except Exception as fallback_error:
                logger.error(f"Fallback TTS also failed: {fallback_error}")
                raise RuntimeError(f"TTS generation failed: {e}. Fallback also failed: {fallback_error}")
    
    async def _generate_with_edge_tts(self, text: str, voice: str) -> str:
        """Generate speech using Edge TTS (Microsoft's free cloud TTS) - FAST"""
        import edge_tts
        
        # Map voice parameter to Edge TTS voice names
        voice_map = {
            "default": "en-US-AriaNeural",
            "male": "en-US-GuyNeural", 
            "male_1": "en-US-GuyNeural",
            "male_2": "en-US-ChristopherNeural",
            "female": "en-US-AriaNeural",
            "female_1": "en-US-AriaNeural",
            "female_2": "en-US-JennyNeural",
            "professional": "en-US-JennyNeural",
            "friendly": "en-US-AriaNeural",
            "neutral": "en-US-AriaNeural"
        }
        
        edge_voice = voice_map.get(voice, "en-US-AriaNeural")
        
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                output_path = temp_file.name
            
            # Generate speech using Edge TTS
            communicate = edge_tts.Communicate(text, edge_voice)
            await communicate.save(output_path)
            
            logger.info(f"Edge TTS generated speech successfully: {len(text)} chars -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Edge TTS generation failed: {e}")
            raise
    
    async def _generate_with_coqui(self, text: str, voice: str) -> str:
        """Generate speech using Coqui TTS (using tts() method directly)"""
        if not self.coqui_tts:
            raise RuntimeError("Coqui TTS not initialized")

        output_path = None
        try:
            # Create temporary file path
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                output_path = temp_file.name

            # Run the core tts() method in executor
            loop = asyncio.get_event_loop()
            logger.info(f"Calling Coqui TTS.tts() for text: '{text[:50]}...'")

            # --- NEW APPROACH: Call tts() instead of tts_to_file ---
            # tts() returns audio samples directly. No speaker arg needed for single-speaker model.
            wav_samples = await loop.run_in_executor(
                None,             # Use default executor
                self.coqui_tts.tts,
                text              # Pass only the text
            )
            # --- END OF NEW APPROACH ---
            
            if not wav_samples:
                 raise RuntimeError("Coqui TTS.tts() returned no samples.")

            logger.info(f"Coqui TTS.tts() completed. Saving samples to {output_path}")

            # Manually save the audio samples to the file
            # Use soundfile library (ensure it's installed: pip install soundfile numpy)
            import soundfile as sf
            import numpy as np
            
            # Coqui TTS returns a list, convert to numpy array if needed
            # Assuming the sample rate is stored in the model's config
            sample_rate = self.coqui_tts.synthesizer.output_sample_rate if hasattr(self.coqui_tts, 'synthesizer') else 22050
            
            # --- Save audio using soundfile ---
            await loop.run_in_executor(
                None, 
                sf.write, 
                output_path, 
                np.array(wav_samples), # Ensure it's a numpy array
                sample_rate
            )
            # --- End of saving ---

            logger.info(f"Coqui TTS generated speech successfully to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Coqui TTS generation failed with tts() method: {e}")
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            raise
    
    async def _generate_with_huggingface(self, text: str, voice: str) -> str:
        """Generate speech using HuggingFace TTS"""
        if not self.hf_model or not self.hf_tokenizer:
            raise RuntimeError("HuggingFace TTS not initialized")
        
        try:
            import torch
            import soundfile as sf
            
            # Tokenize and generate
            inputs = self.hf_tokenizer(text, return_tensors="pt")
            
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            with torch.no_grad():
                output = self.hf_model(**inputs).waveform
            
            # Convert to numpy and save
            audio = output.cpu().numpy().squeeze()
            
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                output_path = temp_file.name
            
            # Save as WAV file
            sf.write(output_path, audio, self.hf_model.config.sampling_rate)
            
            return output_path
        except Exception as e:
            logger.error(f"HuggingFace TTS generation failed: {e}")
            raise
    
    async def _generate_fallback(self, text: str, voice: str) -> str:
        """Generate fallback audio using Google TTS (gTTS) - FREE and high quality"""
        
        # Try gTTS first (Google Text-to-Speech - free, high quality)
        try:
            from gtts import gTTS
            import asyncio
            
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                output_path = temp_file.name
            
            # Generate speech using gTTS (runs in threadpool as it's blocking)
            loop = asyncio.get_event_loop()
            
            def generate_gtts():
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(output_path)
            
            await loop.run_in_executor(None, generate_gtts)
            
            logger.info(f"gTTS fallback generated speech: '{text[:50]}...'")
            return output_path
            
        except ImportError:
            logger.warning("gTTS not installed. Trying pyttsx3...")
        except Exception as e:
            logger.warning(f"gTTS failed: {e}. Trying pyttsx3...")
        
        # Try pyttsx3 as second fallback (offline, uses system voice)
        try:
            import pyttsx3
            import asyncio
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                output_path = temp_file.name
            
            loop = asyncio.get_event_loop()
            
            def generate_pyttsx3():
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)  # Speed
                engine.save_to_file(text, output_path)
                engine.runAndWait()
            
            await loop.run_in_executor(None, generate_pyttsx3)
            
            logger.info(f"pyttsx3 fallback generated speech: '{text[:50]}...'")
            return output_path
            
        except ImportError:
            logger.warning("pyttsx3 not installed.")
        except Exception as e:
            logger.warning(f"pyttsx3 failed: {e}")
        
        # Last resort: Return error (no more silent/noise fallback)
        raise RuntimeError("No TTS providers available. Please install edge-tts or gtts.")
    
    def get_available_voices(self) -> Dict[str, list]:
        """Get available voices for the current provider"""
        if self.provider == "coqui" and self.coqui_tts:
            try:
                models = self.coqui_tts.list_models()
                return {
                    "provider": "coqui",
                    "voices": models
                }
            except:
                return {"provider": "coqui", "voices": ["default"]}
        elif self.provider == "hf":
            return {
                "provider": "huggingface",
                "voices": ["default", "male", "female"]
            }
        else:
            return {"provider": self.provider, "voices": ["default"]}

# Global instance
tts_service = TTSService()


