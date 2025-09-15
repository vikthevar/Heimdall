#!/usr/bin/env python3
"""
Heimdall Simple GUI - Working AI Integration
Connects GUI directly to AI backend
"""
import sys
import os
import asyncio
import threading
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                               QLabel, QFrame)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Import AI Brain
from ai.heimdall_brain import heimdall_brain

class AIWorker(QThread):
    """Background thread for AI processing"""
    response_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.message_queue = []
        self.running = True
        
    def add_message(self, message):
        """Add message to processing queue"""
        self.message_queue.append(message)
    
    def run(self):
        """Main thread loop"""
        # Initialize AI in this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Initialize Heimdall Brain
            self.status_changed.emit("Initializing AI...")
            success = loop.run_until_complete(heimdall_brain.initialize())
            
            if success:
                self.status_changed.emit("Ready")
            else:
                self.status_changed.emit("AI initialization failed")
                return
            
            # Process messages
            while self.running:
                if self.message_queue:
                    message = self.message_queue.pop(0)
                    self.status_changed.emit("Processing...")
                    
                    # Process with AI
                    response = loop.run_until_complete(
                        heimdall_brain.process_message(message)
                    )
                    
                    self.response_ready.emit(response)
                    self.status_changed.emit("Ready")
                
                # Small delay
                loop.run_until_complete(asyncio.sleep(0.1))
                
        except Exception as e:
            self.response_ready.emit(f"❌ Error: {str(e)}")
            self.status_changed.emit("Error")
        finally:
            loop.close()
    
    def stop(self):
        """Stop the worker"""
        self.running = False

class HeimdallWindow(QMainWindow):
    """Simple Heimdall GUI Window"""
    
    def __init__(self):
        super().__init__()
        self.ai_worker = None
        self.setup_ui()
        self.setup_ai()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Heimdall AI Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("👁 Heimdall AI Assistant")
        header.setStyleSheet("""
            QLabel {
                color: #d4af37; 
                font-size: 24px; 
                font-weight: bold; 
                padding: 20px;
                background: #1a1a1a;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Status
        self.status_label = QLabel("🔄 Starting up...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 12px;
                padding: 5px;
                background: #2a2a2a;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background: #0a0a0a;
                color: white;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                font-family: 'SF Pro Display', 'Segoe UI', Arial;
            }
        """)
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)
        
        # Input area
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message... (e.g., 'Read my screen', 'Click the blue button')")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: #2a2a2a;
                color: white;
                border: 2px solid #444;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #d4af37;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #d4af37);
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #b8860b);
            }
            QPushButton:pressed {
                background: #666;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        layout.addWidget(input_frame)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a1a);
            }
        """)
        
        # Welcome message
        self.add_message("Welcome to Heimdall! 👁", False)
        self.add_message("I'm your AI assistant. I can help you with:", False)
        self.add_message("• Reading screen content", False)
        self.add_message("• Clicking buttons and links", False)
        self.add_message("• Voice commands", False)
        self.add_message("• Screen navigation", False)
        self.add_message("", False)
        self.add_message("Try typing: 'Read what's on my screen' or 'Help'", False)
    
    def setup_ai(self):
        """Setup AI worker thread"""
        self.ai_worker = AIWorker()
        self.ai_worker.response_ready.connect(self.handle_ai_response)
        self.ai_worker.status_changed.connect(self.handle_status_change)
        self.ai_worker.start()
    
    def send_message(self):
        """Send user message"""
        text = self.input_field.text().strip()
        if not text:
            return
        
        # Add user message to chat
        self.add_message(text, True)
        
        # Send to AI
        if self.ai_worker:
            self.ai_worker.add_message(text)
        
        # Clear input
        self.input_field.clear()
    
    def add_message(self, message, is_user=False):
        """Add message to chat area"""
        if is_user:
            formatted = f'<div style="color: #8b5cf6; margin: 10px 0;"><b>🧑 You:</b> {message}</div>'
        else:
            formatted = f'<div style="color: #d4af37; margin: 10px 0;"><b>🤖 Heimdall:</b> {message}</div>'
        
        self.chat_area.append(formatted)
        
        # Auto-scroll to bottom
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def handle_ai_response(self, response):
        """Handle AI response"""
        self.add_message(response, False)
    
    def handle_status_change(self, status):
        """Handle status change"""
        status_icons = {
            "Initializing AI...": "🔄",
            "Ready": "🟢",
            "Processing...": "⚡",
            "Error": "❌"
        }
        
        icon = status_icons.get(status, "🔵")
        self.status_label.setText(f"{icon} {status}")
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.ai_worker:
            self.ai_worker.stop()
            self.ai_worker.wait()
        event.accept()

def main():
    """Main entry point"""
    if not PYQT_AVAILABLE:
        print("❌ PyQt6 not available. Install with: pip install PyQt6")
        return 1
    
    # Ensure directories exist
    os.makedirs("./data/logs", exist_ok=True)
    os.makedirs("./data/screenshots", exist_ok=True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Heimdall AI Assistant")
    
    # Create and show window
    window = HeimdallWindow()
    window.show()
    
    print("✅ Heimdall GUI started!")
    print("🎯 Try typing: 'Read my screen' or 'Help'")
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())