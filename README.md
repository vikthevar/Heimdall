# Heimdall - AI Voice Assistant for Visually Impaired Users

<div align="center">
  <img src="assets/heimdall-logo.png" alt="Heimdall Logo" width="200"/>
  <p><em>Your AI companion for computer navigation and control</em></p>
</div>

## 🎯 Overview

Heimdall is an intelligent voice assistant designed to help visually impaired and non-technical users navigate and control their computer screens through natural voice commands. The system captures screenshots, analyzes screen content using OCR and computer vision, and executes user requests through voice-controlled automation.

## ✨ Features

- **Voice Command Recognition**: Natural language processing for screen navigation
- **Screen Analysis**: OCR text extraction and UI element detection
- **Intelligent Automation**: Mouse and keyboard control based on voice commands
- **Voice Feedback**: Clear, friendly audio responses
- **Cloud Storage**: Secure AWS integration for data and preferences
- **Accessibility Focused**: Designed specifically for visually impaired users

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  Intent Parser  │───▶│ Screen Controller│
│   (Whisper)     │    │   (GPT-4o)      │    │  (PyAutoGUI)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Voice Output    │    │ Screen Analyzer │    │   AWS Storage   │
│ (ElevenLabs)    │    │ (OCR + YOLOv8)  │    │ (S3 + DynamoDB) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- macOS, Windows, or Linux
- Microphone and speakers
- AWS account (for cloud features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kushallg/Heimdall.git
   cd Heimdall
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies**
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download and install Tesseract from GitHub releases
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys:
   # - OPENAI_API_KEY: Your OpenAI API key
   # - ELEVENLABS_API_KEY: Your ElevenLabs API key  
   # - AWS_ACCESS_KEY_ID: Your AWS access key
   # - AWS_SECRET_ACCESS_KEY: Your AWS secret key
   ```

6. **Run Heimdall**
   ```bash
   python main.py
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

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_key

# ElevenLabs API
ELEVENLABS_API_KEY=your_elevenlabs_key

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=heimdall-screenshots
DYNAMODB_TABLE_NAME=heimdall-logs

# Application Settings
SCREENSHOT_INTERVAL=30
VOICE_MODEL=eleven_monolingual_v1
```

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

- All audio and image data is encrypted before storage
- API calls are rate-limited and anonymized
- User preferences are stored locally by default
- Comprehensive logging for transparency and debugging

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/heimdall/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/heimdall/discussions)

## 🙏 Acknowledgments

- OpenAI for Whisper and GPT models
- ElevenLabs for voice synthesis
- AWS for cloud infrastructure
- The open-source community for OCR and computer vision tools

---

<div align="center">
  <p>Made with ❤️ for accessibility and inclusion</p>
</div> 