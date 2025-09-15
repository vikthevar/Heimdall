#!/usr/bin/env python3
"""
Heimdall Minimal Working - Guaranteed to show chat interface
Simple, robust GUI with screen capture functionality
"""
import sys
import os
import asyncio
import threading
from datetime import datetime

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                               QLabel, QFrame, QCheckBox)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Import screen capture functionality
try:
    import pyautogui
    import pytesseract
    from PIL import ImageGrab
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Screen capture not available: {e}")
    SCREEN_CAPTURE_AVAILABLE = False

class ScreenCaptureWorker(QThread):
    """Simple screen capture worker"""
    capture_complete = pyqtSignal(str, str)  # full_text, truncated_text
    capture_error = pyqtSignal(str)
    
    def run(self):
        """Capture screen and perform OCR"""
        try:
            if not SCREEN_CAPTURE_AVAILABLE:
                self.capture_error.emit("Screen capture not available. Install: pip install pyautogui pytesseract pillow")
                return
            
            # Take screenshot
            try:
                screenshot = pyautogui.screenshot()
            except:
                screenshot = ImageGrab.grab()
            
            # Perform OCR
            try:
                full_text = pytesseract.image_to_string(screenshot)
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                cleaned_text = '\n'.join(lines)
                
                if not cleaned_text:
                    self.capture_error.emit("No text found on screen")
                    return
                
                truncated = cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text
                self.capture_complete.emit(cleaned_text, truncated)
                
            except Exception as e:
                if "tesseract" in str(e).lower():
                    self.capture_error.emit("Tesseract not found. Install: brew install tesseract (macOS)")
                else:
                    self.capture_error.emit(f"OCR failed: {str(e)}")
                    
        except Exception as e:
            self.capture_error.emit(f"Screen capture failed: {str(e)}")

class HeimdallMinimalWindow(QMainWindow):
    """Minimal working Heimdall window"""
    
    def __init__(self):
        super().__init__()
        self.screen_worker = None
        self.setup_ui()
        print("✅ GUI setup complete")
    
    def setup_ui(self):
        """Setup the user interface - guaranteed to work"""
        self.setWindowTitle("Heimdall AI Assistant - Minimal Working")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Simple header
        header = QLabel("👁 Heimdall AI Assistant")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #d4af37; padding: 20px; background: #1a1a1a; border-radius: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Status and controls
        controls = QFrame()
        controls_layout = QHBoxLayout(controls)
        
        self.status_label = QLabel("🟢 Ready")
        self.status_label.setStyleSheet("color: white; padding: 10px; background: #2a2a2a; border-radius: 5px;")
        
        self.auto_analyze_cb = QCheckBox("Auto-analyze OCR")
        self.auto_analyze_cb.setChecked(True)
        self.auto_analyze_cb.setStyleSheet("color: white; padding: 5px;")
        
        self.read_screen_btn = QPushButton("📖 Read Screen")
        self.read_screen_btn.setStyleSheet("""
            QPushButton {
                background: #4a4a4a; color: white; border: none; border-radius: 8px;
                padding: 10px 20px; font-weight: bold;
            }
            QPushButton:hover { background: #5a5a5a; }
            QPushButton:disabled { background: #2a2a2a; color: #666; }
        """)
        self.read_screen_btn.clicked.connect(self.read_screen)
        
        controls_layout.addWidget(self.status_label)
        controls_layout.addWidget(self.auto_analyze_cb)
        controls_layout.addStretch()
        controls_layout.addWidget(self.read_screen_btn)
        layout.addWidget(controls)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background: #0a0a0a; color: white; border: 2px solid #333;
                border-radius: 10px; padding: 15px; font-size: 14px;
            }
        """)
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)
        
        # Input area
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: #2a2a2a; color: white; border: 1px solid #444;
                border-radius: 15px; padding: 12px; font-size: 14px;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: #8b5cf6; color: white; border: none; border-radius: 15px;
                padding: 12px 25px; font-weight: bold;
            }
            QPushButton:hover { background: #7c3aed; }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        layout.addWidget(input_frame)
        
        # Apply dark theme
        self.setStyleSheet("QMainWindow { background: #0a0a0a; }")
        
        # Add welcome messages
        self.add_message("Welcome to Heimdall AI Assistant! 👁", False)
        self.add_message("", False)
        self.add_message("🎯 **Features:**", False)
        self.add_message("• Click '📖 Read Screen' to capture and analyze your screen", False)
        self.add_message("• Type messages in the input field below", False)
        self.add_message("• Toggle 'Auto-analyze OCR' to get AI interpretation of screen content", False)
        self.add_message("", False)
        
        if SCREEN_CAPTURE_AVAILABLE:
            self.add_message("✅ Screen capture ready! Tesseract OCR available.", False)
        else:
            self.add_message("⚠️ Screen capture unavailable. Install: pip install pyautogui pytesseract", False)
        
        self.add_message("", False)
        self.add_message("Ready! Try clicking 'Read Screen' or type a message.", False)
        
        print("✅ UI elements created successfully")
    
    def add_message(self, message, is_user=False):
        """Add message to chat area"""
        if is_user:
            formatted = f'<div style="margin: 10px 0; padding: 10px; background: #8b5cf6; border-radius: 10px;"><b>🧑 You:</b> {message}</div>'
        else:
            formatted = f'<div style="margin: 10px 0; padding: 10px; background: #2a2a2a; border-radius: 10px;"><b>🤖 Heimdall:</b> {message}</div>'
        
        self.chat_area.append(formatted)
        
        # Auto-scroll
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Send user message"""
        text = self.input_field.text().strip()
        if not text:
            return
        
        # Add user message
        self.add_message(text, True)
        
        # Simple AI response
        if "hello" in text.lower() or "hi" in text.lower():
            response = "Hello! I'm Heimdall, your AI assistant. Try clicking 'Read Screen' to see what I can do!"
        elif "help" in text.lower():
            response = """I can help you with:
• Screen reading and OCR analysis
• Basic chat and conversation
• Screen capture and text extraction

Click the 'Read Screen' button to capture and analyze your screen content!"""
        elif "read" in text.lower() and "screen" in text.lower():
            response = "I'll read your screen! Click the 'Read Screen' button above for real OCR analysis."
        else:
            response = f"I understand you said: '{text}'. This is a simple demo response. Click 'Read Screen' for real functionality!"
        
        self.add_message(response, False)
        self.input_field.clear()
    
    def read_screen(self):
        """Capture and read screen content"""
        # Disable button during capture
        self.read_screen_btn.setEnabled(False)
        self.read_screen_btn.setText("Capturing...")
        self.status_label.setText("📸 Capturing screen...")
        
        # Add user action message
        self.add_message("📖 Read my screen", True)
        self.add_message("🤔 Capturing and analyzing screen...", False)
        
        # Start screen capture worker
        self.screen_worker = ScreenCaptureWorker()
        self.screen_worker.capture_complete.connect(self.handle_screen_capture_success)
        self.screen_worker.capture_error.connect(self.handle_screen_capture_error)
        self.screen_worker.start()
    
    def handle_screen_capture_success(self, full_text, truncated_text):
        """Handle successful screen capture"""
        # Re-enable button
        self.read_screen_btn.setEnabled(True)
        self.read_screen_btn.setText("📖 Read Screen")
        self.status_label.setText("🟢 Ready")
        
        # Show OCR results
        char_count = len(full_text)
        word_count = len(full_text.split())
        
        result_msg = f"""✅ Screen captured successfully!

📊 **Statistics:**
• {word_count} words found
• {char_count} characters extracted

📖 **Content Preview:**
{truncated_text}"""
        
        if len(full_text) > 500:
            result_msg += f"\n\n📄 *Showing first 500 characters. Full text has {char_count} characters.*"
        
        self.add_message(result_msg, False)
        
        # Auto-analyze if enabled
        if self.auto_analyze_cb.isChecked():
            analysis_msg = f"""🧠 **AI Analysis:**
I can see your screen contains text content. The main elements include:
• Text passages and readable content
• UI elements and interface components
• {word_count} words of extractable text

This is a demo analysis. In the full version, I would provide detailed interpretation of the screen content and suggest possible actions."""
            
            self.add_message(analysis_msg, False)
    
    def handle_screen_capture_error(self, error_msg):
        """Handle screen capture error"""
        # Re-enable button
        self.read_screen_btn.setEnabled(True)
        self.read_screen_btn.setText("📖 Read Screen")
        self.status_label.setText("❌ Error")
        
        # Show error message with troubleshooting
        error_response = f"""❌ Screen capture failed: {error_msg}

🔧 **Troubleshooting:**
• **macOS**: brew install tesseract
• **Ubuntu**: sudo apt install tesseract-ocr
• **Windows**: Download from GitHub releases
• **Python packages**: pip install pyautogui pytesseract pillow

📋 **Common Issues:**
• Tesseract binary not in PATH
• Missing Python packages
• Screen permissions (macOS Security & Privacy)"""
        
        self.add_message(error_response, False)

def main():
    """Main entry point"""
    if not PYQT_AVAILABLE:
        print("❌ PyQt6 not available. Install with: pip install PyQt6")
        return 1
    
    print("🚀 Starting Heimdall Minimal Working GUI...")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Heimdall AI Assistant - Minimal")
    
    # Create and show window
    try:
        window = HeimdallMinimalWindow()
        window.show()
        
        print("✅ Heimdall Minimal GUI started successfully!")
        print("🎯 Features available:")
        print("  • Chat interface")
        print("  • Screen capture with OCR")
        print("  • Auto-analysis toggle")
        print("  • Error handling with troubleshooting")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        print(f"❌ Failed to start GUI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())