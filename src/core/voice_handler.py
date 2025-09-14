"""
Free voice input handler using local Whisper
"""
import asyncio
import whisper
import sounddevice as sd
import numpy as np
from loguru import logger
from typing import Optional
import tempfile
import wave
import os


class VoiceHandler:
    def __init__(self, model_size: str = "base"):
        """Initialize with local Whisper model"""
        self.model_size = model_size
        self.model = None
        self.is_listening = False
        self.sample_rate = 16000
        self.channels = 1
        
    async def initialize(self):
        """Load Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def listen_for_command(self, duration: int = 5) -> Optional[str]:
        """Record audio and transcribe using local Whisper"""
        if not self.model:
            await self.initialize()
        
        try:
            logger.info(f"Listening for {duration} seconds...")
            
            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()  # Wait for recording to complete
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Convert to 16-bit PCM
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(self.channels)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_int16.tobytes())
                
                # Transcribe with Whisper
                result = self.model.transcribe(temp_file.name)
                text = result["text"].strip()
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                if text:
                    logger.info(f"Transcribed: {text}")
                    return text
                else:
                    logger.warning("No speech detected")
                    return None
                    
        except Exception as e:
            logger.error(f"Voice recognition error: {e}")
            return None
    
    def get_available_devices(self):
        """Get list of available audio input devices"""
        return sd.query_devices()