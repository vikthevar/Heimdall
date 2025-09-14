# Heimdall Usage Guide - Free Voice Assistant

## 🚀 Getting Started

### 1. First Time Setup
```bash
# Clone and setup
git clone https://github.com/kushallg/Heimdall.git
cd Heimdall
python setup.py

# Start Ollama (in separate terminal)
ollama serve

# Download the AI model
ollama pull llama3.2:3b

# Test everything works
python test_setup.py

# Start Heimdall
python main.py
```

### 2. Daily Usage
```bash
# Start Ollama (if not running)
ollama serve

# Start Heimdall
python main.py
```

## 🎤 Voice Commands

### Basic Navigation
- **"Read what's on my screen"** - Reads all visible text
- **"What's in the top right corner?"** - Analyzes specific regions
- **"Scroll down"** / **"Scroll up"** - Scrolls the page
- **"Go back"** / **"Go forward"** - Browser navigation

### Clicking and Interaction
- **"Click the blue button"** - Finds and clicks UI elements
- **"Click on submit"** - Clicks buttons by text
- **"Press enter"** - Keyboard shortcuts
- **"Double click on file"** - Double-click actions

### Text Input
- **"Type hello world"** - Types specified text
- **"Press ctrl+c"** - Key combinations
- **"Clear the text field"** - Text manipulation

### System Control
- **"Stop Heimdall"** - Exits the application
- **"Take a screenshot"** - Captures current screen

## 🔧 Configuration

### Voice Settings
Edit `.env` file to customize:
```env
# Change TTS voice (0, 1, 2, etc.)
TTS_VOICE_INDEX=1

# Adjust speaking speed (words per minute)
TTS_RATE=180

# Change volume (0.0 to 1.0)
TTS_VOLUME=0.8

# Use different Whisper model for better accuracy
WHISPER_MODEL=small  # Options: tiny, base, small, medium, large
```

### AI Model Settings
```env
# Use different Ollama model
OLLAMA_MODEL=llama3.2:1b  # Faster, less accurate
OLLAMA_MODEL=llama3.2:3b  # Balanced (recommended)
OLLAMA_MODEL=llama3.2:7b  # Slower, more accurate
```

## 🛠️ Troubleshooting

### Common Issues

#### "Ollama not responding"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Pull model if missing
ollama pull llama3.2:3b
```

#### "No audio input detected"
```bash
# Test microphone
python -c "import sounddevice as sd; print(sd.query_devices())"

# Check system audio permissions
# macOS: System Preferences > Security & Privacy > Microphone
# Windows: Settings > Privacy > Microphone
```

#### "Tesseract not found"
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows: Download from GitHub and add to PATH
```

#### "TTS not working"
```bash
# Test TTS
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"

# List available voices
python -c "import pyttsx3; engine = pyttsx3.init(); voices = engine.getProperty('voices'); [print(f'{i}: {v.name}') for i, v in enumerate(voices)]"
```

### Performance Optimization

#### For Slower Computers
```env
# Use smaller models
WHISPER_MODEL=tiny
OLLAMA_MODEL=llama3.2:1b

# Reduce screenshot frequency
SCREENSHOT_INTERVAL=60
```

#### For Better Accuracy
```env
# Use larger models (requires more RAM)
WHISPER_MODEL=small
OLLAMA_MODEL=llama3.2:3b

# Increase OCR confidence
OCR_CONFIDENCE_THRESHOLD=0.8
```

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 2+ cores, 2.0+ GHz
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **OS**: macOS 10.14+, Windows 10+, Ubuntu 18.04+

### Recommended Requirements
- **CPU**: 4+ cores, 3.0+ GHz
- **RAM**: 8GB+ (for larger AI models)
- **Storage**: 5GB+ free space
- **GPU**: Optional, but helps with larger models

## 🔒 Privacy Features

### Data Storage
- All data stored locally in `./data/` directory
- No cloud uploads or external API calls
- SQLite database for command history
- Screenshots saved locally only

### Data Management
```bash
# View stored data
ls -la data/

# Clear command history
rm data/heimdall.db

# Clear screenshots
rm -rf data/screenshots/*

# Clear logs
rm -rf data/logs/*
```

## 🎯 Tips for Best Results

### Voice Commands
- Speak clearly and at normal pace
- Use specific descriptions: "blue submit button" vs "button"
- Wait for Heimdall to respond before next command
- Use consistent terminology

### Screen Analysis
- Ensure good screen contrast for better OCR
- Avoid cluttered screens when possible
- Use descriptive text on buttons/links
- Keep important elements visible

### Performance
- Close unnecessary applications to free RAM
- Use smaller AI models on slower computers
- Regular cleanup of old screenshots and logs
- Keep Ollama running for faster responses

## 🆘 Getting Help

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

### Log Files
- Application logs: `./data/logs/heimdall.log`
- Error details and performance metrics included

### Community Support
- GitHub Issues: Report bugs and feature requests
- Discussions: Share tips and get help
- Wiki: Additional documentation and guides

## 🔄 Updates

### Updating Heimdall
```bash
git pull origin main
pip install -r requirements.txt
```

### Updating AI Models
```bash
# Update Ollama models
ollama pull llama3.2:3b

# Update Whisper (automatic with pip)
pip install --upgrade openai-whisper
```