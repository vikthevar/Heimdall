"""
Free text-to-speech using pyttsx3
"""
import pyttsx3
import asyncio
from loguru import logger
from typing import Optional
import threading


class VoiceOutput:
    def __init__(self, voice_index: int = 0, rate: int = 200, volume: float = 0.9):
        """Initialize TTS engine with pyttsx3"""
        self.voice_index = voice_index
        self.rate = rate
        self.volume = volume
        self.engine = None
        self._lock = threading.Lock()
        
    def initialize(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Set voice if available
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > self.voice_index:
                self.engine.setProperty('voice', voices[self.voice_index].id)
                logger.info(f"Using voice: {voices[self.voice_index].name}")
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise
    
    async def speak(self, text: str) -> bool:
        """Convert text to speech"""
        if not self.engine:
            self.initialize()
        
        try:
            logger.info(f"Speaking: {text}")
            
            # Run TTS in thread to avoid blocking
            def _speak():
                with self._lock:
                    self.engine.say(text)
                    self.engine.runAndWait()
            
            # Run in executor to make it async
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _speak)
            
            return True
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def get_available_voices(self):
        """Get list of available system voices"""
        if not self.engine:
            self.initialize()
        
        voices = self.engine.getProperty('voices')
        return [(i, voice.name, voice.id) for i, voice in enumerate(voices)]
    
    def set_voice(self, voice_index: int):
        """Change the voice"""
        if not self.engine:
            self.initialize()
        
        voices = self.engine.getProperty('voices')
        if voices and 0 <= voice_index < len(voices):
            self.engine.setProperty('voice', voices[voice_index].id)
            self.voice_index = voice_index
            logger.info(f"Voice changed to: {voices[voice_index].name}")
        else:
            logger.warning(f"Invalid voice index: {voice_index}")
    
    def set_rate(self, rate: int):
        """Change speaking rate"""
        if not self.engine:
            self.initialize()
        
        self.engine.setProperty('rate', rate)
        self.rate = rate
        logger.info(f"Speech rate set to: {rate}")
    
    def set_volume(self, volume: float):
        """Change volume (0.0 to 1.0)"""
        if not self.engine:
            self.initialize()
        
        volume = max(0.0, min(1.0, volume))  # Clamp to valid range
        self.engine.setProperty('volume', volume)
        self.volume = volume
        logger.info(f"Volume set to: {volume}")