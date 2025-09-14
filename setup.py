#!/usr/bin/env python3
"""
Setup script for Heimdall - Free AI Voice Assistant
"""
import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system().lower()
    
    print("📦 Installing system dependencies...")
    
    if system == "darwin":  # macOS
        print("Installing Tesseract OCR via Homebrew...")
        try:
            subprocess.run(["brew", "install", "tesseract"], check=True)
            print("✅ Tesseract installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Tesseract. Please install Homebrew first:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return False
    
    elif system == "linux":
        print("Installing Tesseract OCR via apt...")
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "tesseract-ocr", "portaudio19-dev"], check=True)
            print("✅ Tesseract and PortAudio installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install system dependencies")
            return False
    
    elif system == "windows":
        print("⚠️  Windows users need to manually install:")
        print("   1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   2. Add Tesseract to PATH")
        print("   3. Install Visual C++ Build Tools if needed")
    
    return True


def install_ollama():
    """Install and setup Ollama"""
    print("🤖 Setting up Ollama (Free Local LLM)...")
    
    system = platform.system().lower()
    
    if system == "darwin":
        print("Download Ollama from: https://ollama.ai/download/mac")
    elif system == "linux":
        print("Installing Ollama...")
        try:
            subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh"], 
                         stdout=subprocess.PIPE, check=True)
            print("✅ Ollama installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Ollama automatically")
            print("Please install manually: curl -fsSL https://ollama.ai/install.sh | sh")
    elif system == "windows":
        print("Download Ollama from: https://ollama.ai/download/windows")
    
    print("\n📋 After installing Ollama:")
    print("   1. Start Ollama: ollama serve")
    print("   2. Pull the model: ollama pull llama3.2:3b")


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "data",
        "data/screenshots", 
        "data/logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")


def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists(".env"):
        print("📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("""# Heimdall Environment Configuration - FREE APIS ONLY

# Local AI Configuration (FREE)
OLLAMA_MODEL=llama3.2:3b
OLLAMA_HOST=http://localhost:11434
WHISPER_MODEL=base

# Local TTS Configuration (FREE)
TTS_ENGINE=pyttsx3
TTS_VOICE_INDEX=0
TTS_RATE=200
TTS_VOLUME=0.9

# Local Storage Configuration (FREE)
DATABASE_PATH=./data/heimdall.db
SCREENSHOTS_PATH=./data/screenshots
LOGS_PATH=./data/logs

# Application Settings
SCREENSHOT_INTERVAL=30
LOG_LEVEL=INFO
DEBUG_MODE=false

# Audio Configuration
AUDIO_SAMPLE_RATE=16000
AUDIO_CHUNK_SIZE=1024

# Screen Analysis Settings
OCR_CONFIDENCE_THRESHOLD=0.7
UI_DETECTION_CONFIDENCE=0.8

# Performance Settings
MAX_CONCURRENT_REQUESTS=5
API_TIMEOUT_SECONDS=30
""")
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")


def install_python_dependencies():
    """Install Python dependencies"""
    print("🐍 Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False


def test_installation():
    """Test if everything is working"""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        import whisper
        import pyttsx3
        import pytesseract
        import pyautogui
        print("✅ All Python modules imported successfully")
        
        # Test Tesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is working")
        
        # Test TTS
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"✅ TTS engine initialized with {len(voices)} voices")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🏠 Heimdall Setup - Free AI Voice Assistant")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install system dependencies
    if not install_system_dependencies():
        print("❌ Setup failed at system dependencies")
        return
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Setup failed at Python dependencies")
        return
    
    # Install Ollama
    install_ollama()
    
    # Test installation
    if test_installation():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Install and start Ollama if not done already")
        print("   2. Run: ollama pull llama3.2:3b")
        print("   3. Start Heimdall: python main.py")
        print("\n💡 All APIs used are completely FREE!")
    else:
        print("\n❌ Setup completed with errors. Check the messages above.")


if __name__ == "__main__":
    main()