# Heimdall Troubleshooting Guide

## 🚨 Common Installation Issues

### Problem: Cannot install PyQt6/PyQt5

**Symptoms:**
- `pip install PyQt6` fails
- "No module named 'PyQt6'" error
- GUI won't start

**Solutions:**

#### Option 1: Use Simple GUI (Recommended)
```bash
# Run the simple, compatible version
python main_simple.py
```

#### Option 2: Auto-install GUI Framework
```bash
# Let the installer detect the best option
python install_gui.py
python heimdall_gui.py
```

#### Option 3: Manual PyQt Installation

**For macOS:**
```bash
# Using Homebrew
brew install pyqt@5
pip install PyQt5

# Or try PyQt6
pip install PyQt6
```

**For Ubuntu/Debian:**
```bash
# Install system dependencies first
sudo apt-get update
sudo apt-get install python3-pyqt5 python3-pyqt5-dev
pip install PyQt5

# Or for PyQt6
sudo apt-get install python3-pyqt6
pip install PyQt6
```

**For Windows:**
```bash
# Usually works directly
pip install PyQt5
# or
pip install PyQt6

# If it fails, try:
pip install --upgrade pip
pip install PyQt5 --no-cache-dir
```

### Problem: Audio dependencies fail to install

**Symptoms:**
- `pyaudio` installation fails
- "Microsoft Visual C++ 14.0 is required" (Windows)
- Audio-related import errors

**Solutions:**

#### Skip Audio Dependencies (GUI Only)
```bash
# Install minimal requirements without audio
pip install python-dotenv loguru Pillow requests aiosqlite
python main_simple.py
```

#### Fix Audio Dependencies

**For macOS:**
```bash
# Install portaudio first
brew install portaudio
pip install pyaudio
```

**For Ubuntu/Debian:**
```bash
# Install audio development libraries
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**For Windows:**
```bash
# Download pre-compiled wheel
pip install pipwin
pipwin install pyaudio

# Or download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

### Problem: Ollama not working

**Symptoms:**
- "Ollama server not responding"
- Connection refused errors
- Model not found

**Solutions:**

#### Install Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/download/windows
```

#### Start Ollama Service
```bash
# Start the server
ollama serve

# In another terminal, pull the model
ollama pull llama3.2:3b

# Test if it's working
curl http://localhost:11434/api/tags
```

#### Use Without Ollama
```bash
# Run in demo mode (no AI processing)
python main_simple.py
```

### Problem: Tesseract OCR not found

**Symptoms:**
- "Tesseract not found" error
- OCR functionality not working

**Solutions:**

**For macOS:**
```bash
brew install tesseract
```

**For Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**For Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH
3. Or set environment variable: `TESSDATA_PREFIX`

## 🔧 Runtime Issues

### Problem: GUI is slow or unresponsive

**Solutions:**
1. **Use lighter version:**
   ```bash
   python main_simple.py
   ```

2. **Reduce AI model size:**
   ```bash
   ollama pull llama3.2:1b  # Smaller, faster model
   ```

3. **Close other applications** to free up memory

### Problem: Voice recognition not working

**Solutions:**
1. **Check microphone permissions** (macOS/Windows)
2. **Test audio input:**
   ```python
   import sounddevice as sd
   print(sd.query_devices())
   ```
3. **Use text input instead** - the GUI works without voice

### Problem: Screen capture not working

**Solutions:**
1. **Grant screen recording permissions** (macOS)
2. **Run as administrator** (Windows)
3. **Check display scaling** - may affect coordinates

## 🚀 Quick Fixes

### Minimal Installation (Most Compatible)
```bash
# Install only essential packages
pip install python-dotenv loguru Pillow requests

# Run simple GUI
python main_simple.py
```

### Reset Everything
```bash
# Remove virtual environment
rm -rf venv/

# Create fresh environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install minimal requirements
pip install -r requirements-minimal.txt

# Run simple version
python main_simple.py
```

### Check What's Working
```bash
# Test basic functionality
python -c "import tkinter; print('Tkinter: OK')"
python -c "import PIL; print('Pillow: OK')"
python -c "import requests; print('Requests: OK')"

# Test optional components
python -c "import PyQt6; print('PyQt6: OK')" 2>/dev/null || echo "PyQt6: Not available"
python -c "import pyaudio; print('PyAudio: OK')" 2>/dev/null || echo "PyAudio: Not available"
```

## 📞 Getting Help

### Before Asking for Help
1. **Try the simple version:** `python main_simple.py`
2. **Check Python version:** `python --version` (need 3.8+)
3. **Update pip:** `pip install --upgrade pip`
4. **Check error messages** for specific package names

### Include This Information
- Operating system and version
- Python version
- Error messages (full traceback)
- Which installation method you tried
- Output of: `pip list | grep -E "(PyQt|tkinter|Pillow)"`

### Alternative Approaches
1. **Use command-line version:** `python main.py`
2. **Use web interface:** Install FastAPI version
3. **Use Docker:** Container with all dependencies
4. **Use cloud version:** Deploy to cloud platform

## 🎯 Success Indicators

You know it's working when:
- ✅ GUI window opens without errors
- ✅ You can type messages and get responses
- ✅ Status indicator shows "Ready"
- ✅ No error messages in terminal

Even if AI features don't work, the GUI should still open and show demo responses.