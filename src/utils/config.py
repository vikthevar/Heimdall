"""
Configuration management for Heimdall - Free API Version.
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


class LocalAIConfig(BaseSettings):
    """Local AI configuration (Ollama + Whisper)."""
    ollama_host: str = Field('http://localhost:11434', env='OLLAMA_HOST')
    ollama_model: str = Field('llama3.2:3b', env='OLLAMA_MODEL')
    whisper_model: str = Field('base', env='WHISPER_MODEL')


class LocalTTSConfig(BaseSettings):
    """Local TTS configuration (pyttsx3)."""
    engine: str = Field('pyttsx3', env='TTS_ENGINE')
    voice_index: int = Field(0, env='TTS_VOICE_INDEX')
    rate: int = Field(200, env='TTS_RATE')
    volume: float = Field(0.9, env='TTS_VOLUME')


class LocalStorageConfig(BaseSettings):
    """Local storage configuration (SQLite + filesystem)."""
    database_path: str = Field('./data/heimdall.db', env='DATABASE_PATH')
    screenshots_path: str = Field('./data/screenshots', env='SCREENSHOTS_PATH')
    logs_path: str = Field('./data/logs', env='LOGS_PATH')


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
    """Central configuration manager for Heimdall - Free API Version."""
    
    def __init__(self):
        self.local_ai = LocalAIConfig()
        self.local_tts = LocalTTSConfig()
        self.local_storage = LocalStorageConfig()
        self.audio = AudioConfig()
        self.screen_analysis = ScreenAnalysisConfig()
        self.performance = PerformanceConfig()
        self.privacy = PrivacyConfig()
        self.app = AppConfig()
    
    def validate_setup(self) -> list[str]:
        """Validate that local services are accessible."""
        issues = []
        
        # Check if Ollama is accessible
        try:
            import requests
            response = requests.get(f"{self.local_ai.ollama_host}/api/tags", timeout=5)
            if response.status_code != 200:
                issues.append("Ollama server not accessible - run 'ollama serve'")
        except Exception:
            issues.append("Ollama not installed or not running - visit https://ollama.ai/")
        
        # Check if required directories exist
        for path in [self.local_storage.screenshots_path, self.local_storage.logs_path]:
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                except Exception:
                    issues.append(f"Cannot create directory: {path}")
        
        return issues
    
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
    """Validate environment configuration and check local services."""
    issues = config.validate_setup()
    
    if issues:
        print("⚠️  Setup issues found:")
        for issue in issues:
            print(f"   - {issue}")
        
        if not config.app.test_mode:
            print("\n💡 Run 'python test_setup.py' to diagnose issues")
            print("💡 Run 'python setup.py' to fix setup problems")