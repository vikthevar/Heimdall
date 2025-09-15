# Heimdall Project Structure

## 📁 Directory Layout

```
heimdall/
├── 📄 main.py                    # Command-line application entry point
├── 📄 heimdall_working.py        # Modern desktop GUI (MAIN ENTRY POINT)
├── 📄 main_simple.py             # Simple Tkinter fallback GUI
├── 📄 setup.py                   # Automated setup script
├── 📄 test_setup.py              # Setup verification script
├── 📄 create_icons.py            # Icon generation script
├── 📄 install_gui.py             # GUI installation helper
├── 📄 requirements.txt           # Python dependencies (all free)
├── 📄 requirements-minimal.txt   # Minimal dependencies
├── 📄 .env.example               # Environment configuration template
├── 📄 README.md                  # Project documentation
├── 📄 USAGE.md                   # Usage guide and troubleshooting
├── 📄 TROUBLESHOOTING.md         # Detailed troubleshooting guide
├── 📄 PROJECT_STRUCTURE.md       # This file
├── 📄 SECURITY.md                # Security guidelines
├── 📄 .gitignore                 # Git ignore rules
│
├── 📁 src/                       # Source code
│   ├── 📁 core/                  # Core AI functionality
│   │   ├── 📄 __init__.py
│   │   ├── 📄 voice_handler.py       # Local Whisper speech recognition
│   │   ├── 📄 voice_output.py        # pyttsx3 text-to-speech
│   │   ├── 📄 intent_parser.py       # Ollama LLM for command parsing
│   │   ├── 📄 screenshot_capturer.py # Screen capture functionality
│   │   ├── 📄 screen_analyzer.py     # Tesseract OCR + OpenCV analysis
│   │   └── 📄 screen_controller.py   # PyAutoGUI automation
│   │
│   ├── 📁 ui/                    # Desktop GUI Components
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main_window.py         # PyQt6 main window (legacy)
│   │   ├── 📄 components.py          # Reusable UI components
│   │   ├── 📄 styles.py              # UI themes and styling
│   │   ├── 📄 gui_main.py            # GUI application controller
│   │   └── 📄 tkinter_gui.py         # Tkinter fallback GUI
│   │
│   ├── 📁 storage/               # Local storage (no cloud)
│   │   ├── 📄 __init__.py
│   │   └── 📄 database.py            # SQLite database operations
│   │
│   └── 📁 utils/                 # Utilities
│       ├── 📄 __init__.py
│       └── 📄 config.py              # Configuration management
│
├── 📁 assets/                    # UI assets and icons
│   ├── 📄 README.md              # Asset documentation
│   ├── 📄 heimdall_icon.png      # Main application icon
│   ├── 📄 avatar_ai.png          # AI assistant avatar
│   └── 📄 *.png                  # Various UI icons
│
├── 📁 data/                      # Local data (created at runtime)
│   ├── 📁 screenshots/           # Captured screenshots
│   ├── 📁 logs/                  # Application logs
│   └── 📄 heimdall.db            # SQLite database
│
└── 📁 .kiro/                     # Kiro IDE configuration
    ├── 📁 hooks/                 # IDE hooks
    └── 📁 steering/              # IDE steering rules
```

## 🔧 Core Components

### Voice Processing
- **voice_handler.py**: Local Whisper for speech-to-text conversion
- **voice_output.py**: System TTS using pyttsx3 for voice feedback

### AI & Intelligence  
- **intent_parser.py**: Local Ollama LLM for understanding voice commands
- **screen_analyzer.py**: Tesseract OCR + OpenCV for screen content analysis

### Screen Interaction
- **screenshot_capturer.py**: PIL-based screen capture
- **screen_controller.py**: PyAutoGUI for mouse/keyboard automation

### Data Management
- **database.py**: SQLite for local command history and preferences
- **config.py**: Environment configuration management

## 🆓 Free Technologies Used

| Component | Technology | Purpose | Cost |
|-----------|------------|---------|------|
| Speech Recognition | Local Whisper | Voice input | FREE |
| Language Model | Ollama + Llama 3.2 | Command understanding | FREE |
| Text-to-Speech | pyttsx3 | Voice output | FREE |
| OCR | Tesseract | Screen text extraction | FREE |
| Computer Vision | OpenCV | UI element detection | FREE |
| Database | SQLite | Local data storage | FREE |
| Automation | PyAutoGUI | Screen control | FREE |

## 📊 Data Flow

```
Voice Input → Whisper → Text Command
                           ↓
Screen Capture → OCR/CV → Screen Context
                           ↓
Text + Context → Ollama → Parsed Intent
                           ↓
Parsed Intent → PyAutoGUI → Screen Action
                           ↓
Action Result → pyttsx3 → Voice Feedback
                           ↓
All Data → SQLite → Local Storage
```

## 🔒 Privacy & Security

- **100% Local**: No data leaves your machine
- **No API Keys**: No external service dependencies
- **Open Source**: Full code transparency
- **Local Storage**: SQLite database in `./data/`
- **No Telemetry**: No usage tracking

## 🚀 Getting Started

1. **Setup**: `python setup.py`
2. **Test**: `python test_setup.py`  
3. **Run**: `python main.py`

## 📝 Configuration Files

- **`.env`**: Runtime configuration (created from `.env.example`)
- **`requirements.txt`**: Python package dependencies
- **`.gitignore`**: Files to exclude from version control

## 🗂️ Runtime Data

The `data/` directory is created automatically and contains:
- **Screenshots**: Captured screen images for analysis
- **Logs**: Application logs with rotation
- **Database**: SQLite file with command history and preferences

This directory is excluded from git to maintain privacy.