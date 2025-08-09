"""
Configuration management for Heimdall.
Loads environment variables and provides typed configuration access.
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseSettings, Field


# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class OpenAIConfig(BaseSettings):
    """OpenAI API configuration."""
    api_key: str = Field(..., env='OPENAI_API_KEY')
    model: str = Field('gpt-4o', env='OPENAI_MODEL')
    whisper_model: str = Field('whisper-1', env='WHISPER_MODEL')


class ElevenLabsConfig(BaseSettings):
    """ElevenLabs TTS configuration."""
    api_key: str = Field(..., env='ELEVENLABS_API_KEY')
    voice_id: Optional[str] = Field(None, env='ELEVENLABS_VOICE_ID')
    voice_model: str = Field('eleven_monolingual_v1', env='VOICE_MODEL')


class AWSConfig(BaseSettings):
    """AWS services configuration."""
    access_key_id: str = Field(..., env='AWS_ACCESS_KEY_ID')
    secret_access_key: str = Field(..., env='AWS_SECRET_ACCESS_KEY')
    region: str = Field('us-east-1', env='AWS_REGION')
    s3_bucket_name: str = Field('heimdall-screenshots', env='S3_BUCKET_NAME')
    dynamodb_table_name: str = Field('heimdall-logs', env='DYNAMODB_TABLE_NAME')


class AudioConfig(BaseSettings):
    """Audio processing configuration."""
    sample_rate: int = Field(16000, env='AUDIO_SAMPLE_RATE')
    chunk_size: int = Field(1024, env='AUDIO_CHUNK_SIZE')
    microphone_device_index: int = Field(0, env='MICROPHONE_DEVICE_INDEX')


class ScreenAnalysisConfig(BaseSettings):
    """Screen analysis configuration."""
    ocr_confidence_threshold: float = Field(0.7, env='OCR_CONFIDENCE_THRESHOLD')
    ui_detection_confidence: float = Field(0.8, env='UI_DETECTION_CONFIDENCE')
    screenshot_quality: int = Field(95, env='SCREENSHOT_QUALITY')


class PerformanceConfig(BaseSettings):
    """Performance and rate limiting configuration."""
    max_concurrent_requests: int = Field(5, env='MAX_CONCURRENT_REQUESTS')
    api_timeout_seconds: int = Field(30, env='API_TIMEOUT_SECONDS')
    cache_ttl_seconds: int = Field(300, env='CACHE_TTL_SECONDS')


class PrivacyConfig(BaseSettings):
    """Privacy and security configuration."""
    encrypt_screenshots: bool = Field(True, env='ENCRYPT_SCREENSHOTS')
    local_processing_only: bool = Field(False, env='LOCAL_PROCESSING_ONLY')
    anonymize_logs: bool = Field(True, env='ANONYMIZE_LOGS')


class AppConfig(BaseSettings):
    """Main application configuration."""
    screenshot_interval: int = Field(30, env='SCREENSHOT_INTERVAL')
    log_level: str = Field('INFO', env='LOG_LEVEL')
    debug_mode: bool = Field(False, env='DEBUG_MODE')
    enable_telemetry: bool = Field(False, env='ENABLE_TELEMETRY')
    mock_apis: bool = Field(False, env='MOCK_APIS')
    test_mode: bool = Field(False, env='TEST_MODE')


class HeimdallConfig:
    """Central configuration manager for Heimdall."""
    
    def __init__(self):
        self.openai = OpenAIConfig()
        self.elevenlabs = ElevenLabsConfig()
        self.aws = AWSConfig()
        self.audio = AudioConfig()
        self.screen_analysis = ScreenAnalysisConfig()
        self.performance = PerformanceConfig()
        self.privacy = PrivacyConfig()
        self.app = AppConfig()
    
    def validate_required_keys(self) -> list[str]:
        """Validate that all required API keys are present."""
        missing_keys = []
        
        if not self.openai.api_key:
            missing_keys.append('OPENAI_API_KEY')
        
        if not self.elevenlabs.api_key:
            missing_keys.append('ELEVENLABS_API_KEY')
        
        if not self.aws.access_key_id:
            missing_keys.append('AWS_ACCESS_KEY_ID')
        
        if not self.aws.secret_access_key:
            missing_keys.append('AWS_SECRET_ACCESS_KEY')
        
        return missing_keys
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return self.app.debug_mode or self.app.test_mode
    
    def get_log_config(self) -> dict:
        """Get logging configuration."""
        return {
            'level': self.app.log_level,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'anonymize': self.privacy.anonymize_logs
        }


# Global configuration instance
config = HeimdallConfig()


def get_config() -> HeimdallConfig:
    """Get the global configuration instance."""
    return config


def validate_environment() -> None:
    """Validate environment configuration and raise errors for missing keys."""
    missing_keys = config.validate_required_keys()
    
    if missing_keys and not config.app.mock_apis:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_keys)}. "
            f"Please check your .env file or set MOCK_APIS=true for development."
        )