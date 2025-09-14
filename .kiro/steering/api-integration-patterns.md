---
inclusion: always
---

# API Integration Patterns for Heimdall

## Local Whisper Integration Standards
```python
# Use local Whisper for speech recognition
import whisper
import asyncio

class LocalWhisperClient:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)
    
    async def transcribe_audio(self, audio_file_path: str) -> str:
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self.model.transcribe(audio_file_path)
            )
            return result["text"].strip()
        except Exception as e:
            logger.error(f"Local Whisper error: {e}")
            raise APIError("Speech recognition failed")
```

## Local TTS Patterns
```python
# Use pyttsx3 for text-to-speech
import pyttsx3
import asyncio

class LocalTTSClient:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.cache = {}
    
    async def speak_text(self, text: str) -> bool:
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._speak_sync(text)
            )
            return True
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def _speak_sync(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
```

## Local Storage Patterns
```python
# Use SQLite for local data storage
import aiosqlite
import json
from datetime import datetime

class LocalStorageClient:
    def __init__(self, db_path="./data/heimdall.db"):
        self.db_path = db_path
    
    async def save_screenshot_metadata(self, filepath: str, analysis_data: dict) -> int:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO screenshots (timestamp, filepath, analysis_data)
                    VALUES (?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    filepath,
                    json.dumps(analysis_data)
                ))
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Local storage error: {e}")
            raise StorageError("Failed to save screenshot metadata")
```

## Error Handling Standards
- Always provide user-friendly error messages
- Log technical details for debugging
- Implement graceful degradation
- Use circuit breaker pattern for external APIs
- Provide offline fallbacks where possible

## Rate Limiting Patterns
```python
from asyncio import Semaphore
import asyncio

class RateLimitedClient:
    def __init__(self, max_concurrent=5, requests_per_minute=60):
        self.semaphore = Semaphore(max_concurrent)
        self.rate_limiter = AsyncRateLimiter(requests_per_minute)
    
    async def make_request(self, *args, **kwargs):
        async with self.semaphore:
            await self.rate_limiter.acquire()
            return await self._actual_request(*args, **kwargs)
```