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
        
        if self.provider == "coqui":
            self._init_coqui_tts()
        elif self.provider == "hf":
            self._init_huggingface_tts()
    
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
            if self.provider == "coqui" and self.coqui_tts:
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
        """Generate a fallback audio file when TTS is not available"""
        try:
            import numpy as np
            import soundfile as sf
            
            # Generate a more sophisticated fallback audio
            duration = max(2.0, len(text) * 0.15)  # Rough estimate based on text length
            sample_rate = 22050
            samples = int(duration * sample_rate)
            
            # Generate a more natural-sounding tone sequence
            t = np.linspace(0, duration, samples)
            
            # Create a sequence of tones that sounds more like speech
            audio = np.zeros(samples)
            num_segments = max(3, len(text.split()) // 2)  # More segments for longer text
            segment_length = samples // num_segments
            
            # Frequencies that sound more speech-like
            frequencies = [200, 300, 400, 500, 600, 700]  # Lower frequencies for more natural sound
            
            for i in range(num_segments):
                start_idx = i * segment_length
                end_idx = min((i + 1) * segment_length, samples)
                segment_samples = end_idx - start_idx
                
                if segment_samples > 0:
                    # Choose frequency based on text character at this position
                    char_index = min(i * len(text) // num_segments, len(text) - 1)
                    freq = frequencies[ord(text[char_index]) % len(frequencies)]
                    
                    # Generate tone with some variation
                    segment_t = np.linspace(0, segment_samples / sample_rate, segment_samples)
                    tone = 0.05 * np.sin(2 * np.pi * freq * segment_t)
                    
                    # Add some envelope to make it sound more natural
                    envelope = np.exp(-segment_t * 2)  # Decay envelope
                    tone *= envelope
                    
                    # Add some noise for more natural sound
                    noise = 0.01 * np.random.normal(0, 1, segment_samples)
                    tone += noise
                    
                    audio[start_idx:end_idx] = tone
            
            # Normalize audio
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.3  # Keep volume low
            
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                output_path = temp_file.name
            
            # Save as WAV file
            sf.write(output_path, audio, sample_rate)
            
            logger.warning(f"Generated fallback audio for text: '{text[:50]}...'")
            return output_path
            
        except Exception as e:
            logger.error(f"Fallback audio generation failed: {e}")
            raise RuntimeError(f"All TTS methods failed. Last error: {e}")
    
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


