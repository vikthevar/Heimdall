---
inclusion: always
---

# API Integration Patterns for Heimdall

## OpenAI Integration Standards
```python
# Always use async clients for better performance
from openai import AsyncOpenAI

class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        try:
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_data,
                response_format="text"
            )
            return response
        except Exception as e:
            logger.error(f"Whisper API error: {e}")
            raise APIError("Speech recognition failed")
```

## ElevenLabs TTS Patterns
```python
# Implement voice caching for repeated phrases
class VoiceCache:
    def __init__(self):
        self.cache = {}
    
    async def get_or_generate_audio(self, text: str) -> bytes:
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        audio = await self.elevenlabs_client.generate(text)
        self.cache[cache_key] = audio
        return audio
```

## AWS Integration Patterns
```python
# Use boto3 with proper error handling and retries
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class AWSClient:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
    
    async def upload_screenshot(self, image_data: bytes, user_id: str) -> str:
        try:
            key = f"screenshots/{user_id}/{datetime.now().isoformat()}.png"
            self.s3.put_object(
                Bucket=os.getenv('S3_BUCKET_NAME'),
                Key=key,
                Body=image_data,
                ServerSideEncryption='AES256'
            )
            return key
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise StorageError("Failed to save screenshot")
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