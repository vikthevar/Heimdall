# Heimdall - AI Voice Assistant for Visually Impaired Users

## 🎯 System Goal
An AI voice assistant that helps visually impaired and non-technical users navigate and control their computer screen through voice commands and intelligent screen analysis.

## 🗂️ System Architecture

### Core Components:
1. **Screenshot Capturer** - Python-based screen capture every 30s or on-demand
2. **Voice Input Handler** - OpenAI Whisper for speech-to-text
3. **Screen Analyzer** - OCR + Computer Vision (Tesseract + YOLOv8)
4. **Intent Parser** - GPT-4o for natural language understanding
5. **Screen Controller** - PyAutoGUI for mouse/keyboard automation
6. **Voice Output Generator** - ElevenLabs/AWS Polly for TTS
7. **AWS Integration** - S3 + DynamoDB for storage and logging

### Development Phases:
- Phase 1: Screenshot capture + OCR pipeline
- Phase 2: Voice input/output integration
- Phase 3: Intent parsing and action planning
- Phase 4: Screen control automation
- Phase 5: AWS cloud integration

## 🛠️ Technical Stack
- **Backend**: Python 3.9+
- **AI/ML**: OpenAI Whisper, GPT-4o, YOLOv8, Tesseract OCR
- **Automation**: PyAutoGUI, pyautogui
- **Cloud**: AWS S3, DynamoDB
- **TTS**: ElevenLabs API
- **Audio**: pyaudio, speech_recognition

## 🔐 Security & Privacy
- Encrypted data storage in S3
- Rate-limited LLM calls
- Anonymized user data
- Comprehensive logging for transparency
