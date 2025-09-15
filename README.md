# Heimdall - FREE AI Voice Assistant for Screen Control

<div align="center">
  <p><em>🆓 100% Free AI companion for computer navigation and control</em></p>
  <p><strong>No API keys required • No cloud dependencies • Complete privacy</strong></p>
</div>

## 🎯 Overview

Heimdall is an intelligent voice assistant that uses **completely free APIs and local processing** to help users navigate and control their computer screens through natural voice commands. Everything runs locally on your machine for maximum privacy and zero ongoing costs.

## ✨ Features

- **🆓 100% Free**: No API keys, subscriptions, or cloud services required
- **🔒 Privacy First**: All processing happens locally on your machine
- **🎤 Voice Recognition**: Local Whisper for speech-to-text
- **🧠 AI Intelligence**: Local Ollama LLM for command understanding
- **🔊 Text-to-Speech**: Built-in system TTS for voice feedback
- **👁️ Screen Analysis**: Free OCR and computer vision
- **🖱️ Smart Automation**: Mouse and keyboard control
- **♿ Accessibility Focused**: Designed for visually impaired users

## 🏗️ Free Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  Intent Parser  │───▶│ Screen Controller│
│ (Local Whisper) │    │ (Local Ollama)  │    │  (PyAutoGUI)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Voice Output    │    │ Screen Analyzer │    │ Local Storage   │
│   (pyttsx3)     │    │ (Tesseract OCR) │    │   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start (100% Free Setup)

### Prerequisites

- Python 3.9 or higher
- macOS, Windows, or Linux
- Microphone and speakers
- **No API keys or cloud accounts needed!**

### Automated Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/kushallg/Heimdall.git
   cd Heimdall
   ```

2. **Run the setup script**

   ```bash
   python setup.py
   ```

   This will automatically:

   - Install system dependencies (Tesseract OCR)
   - Create Python virtual environment
   - Install all Python packages
   - Set up Ollama (local LLM)
   - Create necessary directories and config files

3. **Start Ollama and download the model**

   ```bash
   # Start Ollama server (in a separate terminal)
   ollama serve

   # Download the free Llama model (3B parameters)
   ollama pull llama3.2:3b
   ```

4. **Create UI icons (optional)**
   ```bash
   python create_icons.py
   ```

5. **Run Heimdall**
   ```bash
   # 🎨 Modern Desktop GUI (RECOMMENDED)
   python heimdall_working.py
   
   # 💻 Command-line version
   python main.py
   
   # 🔧 Simple compatibility version
   python main_simple.py
   ```

## 📊 **Project Status**
- ✅ **Modern GUI**: Beautiful dark theme with gold/purple accents
- ✅ **Free APIs**: 100% local processing, no API costs
- ✅ **Cross-Platform**: Works on Windows, macOS, Linux
- ✅ **Privacy-First**: All data stays on your machine
- 🔧 **Integration Needed**: Connect GUI to AI backend (see PROJECT_SUMMARY.md)
   ```bash
   python main.py
   ```

### Manual Installation (if automated setup fails)

1. **Install system dependencies**

   ```bash
   # macOS
   brew install tesseract ollama

   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr portaudio19-dev
   curl -fsSL https://ollama.ai/install.sh | sh

   # Windows
   # Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
   # Download Ollama: https://ollama.ai/download/windows
   ```

2. **Create virtual environment and install Python packages**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up local AI model**
   ```bash
   ollama serve  # Start Ollama
   ollama pull llama3.2:3b  # Download free model
   ```

## 🎮 Usage Examples

### Basic Commands

- **"Read what's on my screen"** - Extracts and reads all visible text
- **"Click the blue button"** - Finds and clicks UI elements
- **"Scroll down"** - Performs scroll actions
- **"What's in the top right corner?"** - Analyzes specific screen regions
- **"Open the file menu"** - Navigates application menus

### Advanced Features

- **Context-aware navigation**: "Go back to the previous page"
- **Form filling**: "Type 'hello world' in the text box"
- **File operations**: "Save this document"
- **Application control**: "Close the browser window"

## ⚙️ Configuration (All Free!)

### Environment Variables

The `.env` file is automatically created with free settings:

```env
# Local AI Configuration (FREE)
OLLAMA_MODEL=llama3.2:3b
OLLAMA_HOST=http://localhost:11434
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large

# Local TTS Configuration (FREE)
TTS_ENGINE=pyttsx3
TTS_VOICE_INDEX=0  # System voice to use
TTS_RATE=200  # Words per minute
TTS_VOLUME=0.9

# Local Storage (FREE)
DATABASE_PATH=./data/heimdall.db
SCREENSHOTS_PATH=./data/screenshots
LOGS_PATH=./data/logs
```

### Free Components Used

- **Speech Recognition**: OpenAI Whisper (runs locally)
- **Language Model**: Llama 3.2 via Ollama (runs locally)
- **Text-to-Speech**: pyttsx3 (uses system TTS)
- **OCR**: Tesseract (completely free)
- **Database**: SQLite (built into Python)
- **Storage**: Local filesystem

## 🛠️ Development

### Project Structure

```
heimdall/
├── src/
│   ├── core/
│   │   ├── screenshot_capturer.py
│   │   ├── voice_handler.py
│   │   ├── screen_analyzer.py
│   │   ├── intent_parser.py
│   │   ├── screen_controller.py
│   │   └── voice_output.py
│   ├── aws/
│   │   ├── s3_client.py
│   │   └── dynamodb_client.py
│   ├── models/
│   │   ├── screen_element.py
│   │   └── user_command.py
│   └── utils/
│       ├── config.py
│       └── logger.py
├── tests/
├── assets/
├── docs/
├── main.py
├── requirements.txt
└── README.md
```

### Running Tests

```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🔐 Privacy & Security

- **100% Local Processing**: No data ever leaves your machine
- **No Cloud Dependencies**: Everything runs offline
- **No API Keys Required**: No risk of key exposure or billing
- **Local Storage Only**: SQLite database and local files
- **Open Source**: Full transparency of all code
- **No Telemetry**: No usage tracking or analytics

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/heimdall/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/heimdall/discussions)

## 🙏 Acknowledgments

- **OpenAI** for the free Whisper model
- **Meta** for the free Llama models
- **Ollama** for making local LLMs accessible
- **Tesseract** team for free OCR
- **pyttsx3** developers for free TTS
- The entire **open-source community** for making this possible

## 💰 Cost Comparison

| Service        | Paid Alternative   | Heimdall (Free) | Monthly Savings    |
| -------------- | ------------------ | --------------- | ------------------ |
| Speech-to-Text | OpenAI Whisper API | Local Whisper   | $10-50+            |
| Language Model | GPT-4 API          | Local Llama     | $20-200+           |
| Text-to-Speech | ElevenLabs         | System TTS      | $5-25+             |
| Cloud Storage  | AWS S3/DynamoDB    | Local SQLite    | $5-20+             |
| **Total**      |                    |                 | **$40-295+/month** |

---

<div align="center">
  <p>Made with ❤️ for accessibility and inclusion</p>
</div>
