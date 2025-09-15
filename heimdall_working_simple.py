#!/usr/bin/env python3
"""
Heimdall Working Simple - Minimal AI Integration
Direct connection between GUI and basic AI functionality
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

# Import the real AI Brain
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ai.heimdall_brain import heimdall_brain
    REAL_AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Real AI not available: {e}")
    REAL_AI_AVAILABLE = False

# Import screen capture functionality
try:
    from src.core.screen_analyzer import capture_fullscreen_and_ocr
    import pyautogui
    import pytesseract
    from PIL import ImageGrab
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Screen capture not available: {e}")
    SCREEN_CAPTURE_AVAILABLE = False

class ScreenCaptureWorker(QThread):
    """Background thread for screen capture and OCR"""
    capture_complete = pyqtSignal(str, str)  # Emits (full_text, truncated_text)
    capture_error = pyqtSignal(str)  # Emits error message
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.auto_analyze = True  # Whether to auto-analyze with AI after OCR
        
    def set_auto_analyze(self, enabled):
        """Set whether to auto-analyze OCR results with AI"""
        self.auto_analyze = enabled
    
    def run(self):
        """Capture screen and perform OCR"""
        try:
            self.status_changed.emit("Capturing screen...")
            
            if not SCREEN_CAPTURE_AVAILABLE:
                self.capture_error.emit("Screen capture components not available. Install with: pip install pyautogui pytesseract pillow")
                return
            
            # Take screenshot using PyAutoGUI
            try:
                screenshot = pyautogui.screenshot()
            except Exception as e:
                # Fallback to PIL ImageGrab
                try:
                    screenshot = ImageGrab.grab()
                except Exception as e2:
                    self.capture_error.emit(f"Failed to capture screen: {str(e)} / {str(e2)}")
                    return
            
            self.status_changed.emit("Analyzing screen content...")
            
            # Perform OCR using pytesseract
            try:
                # Convert to RGB if needed
                if screenshot.mode != 'RGB':
                    screenshot = screenshot.convert('RGB')
                
                # Extract text using Tesseract
                full_text = pytesseract.image_to_string(screenshot, config='--psm 6')
                
                # Clean up the text
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                cleaned_text = '\n'.join(lines)
                
                if not cleaned_text:
                    self.capture_error.emit("No readable text found on screen. The screen may contain mostly images or graphics.")
                    return
                
                # Create truncated version (first 500 characters)
                truncated_text = cleaned_text[:500]
                if len(cleaned_text) > 500:
                    truncated_text += "..."
                
                self.capture_complete.emit(cleaned_text, truncated_text)
                
            except pytesseract.TesseractNotFoundError:
                self.capture_error.emit("Tesseract OCR not found. Install with:\n• macOS: brew install tesseract\n• Ubuntu: sudo apt install tesseract-ocr\n• Windows: Download from GitHub releases")
            except Exception as e:
                self.capture_error.emit(f"OCR processing failed: {str(e)}")
                
        except Exception as e:
            self.capture_error.emit(f"Screen capture failed: {str(e)}")
        finally:
            self.status_changed.emit("Ready")

class AIWorker(QThread):
    """Background thread for real AI processing"""
    result_ready = pyqtSignal(dict)  # Emits full result dict
    error_occurred = pyqtSignal(str)  # Emits error message
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.message_queue = []
        self.running = True
        self.current_task = None
        self.simulate_actions = True  # Default to simulation mode
        
    def add_message(self, message, simulate=True):
        """Add message to processing queue"""
        self.message_queue.append((message, simulate))
    
    def cancel_current_task(self):
        """Cancel current processing task (if feasible)"""
        # TODO: Implement task cancellation for long-running operations
        # This could involve setting a cancellation flag that the AI brain checks
        self.current_task = None
        self.status_changed.emit("Cancelled")
    
    def run(self):
        """Main thread loop with real AI integration"""
        # Initialize AI in this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Initialize Heimdall Brain
            self.status_changed.emit("Initializing AI...")
            
            if REAL_AI_AVAILABLE:
                success = loop.run_until_complete(heimdall_brain.initialize())
                if success:
                    self.status_changed.emit("Ready")
                else:
                    self.status_changed.emit("AI initialization failed")
                    self.error_occurred.emit("Failed to initialize AI brain")
                    return
            else:
                self.status_changed.emit("Mock AI Mode")
            
            # Process messages
            while self.running:
                if self.message_queue:
                    message, simulate = self.message_queue.pop(0)
                    self.current_task = message
                    self.status_changed.emit("Thinking...")
                    
                    try:
                        if REAL_AI_AVAILABLE:
                            # Process with real AI brain
                            result = loop.run_until_complete(
                                heimdall_brain.process_message(message, simulate_actions=simulate)
                            )
                        else:
                            # Fallback to mock response
                            loop.run_until_complete(asyncio.sleep(1))  # Simulate processing time
                            result = {
                                'reply': f"🤖 Mock AI Response: I understand '{message}'. Real AI not available.",
                                'intent': {'type': 'mock', 'action': 'mock_response'},
                                'executed': False,
                                'execution_result': None
                            }
                        
                        self.result_ready.emit(result)
                        self.status_changed.emit("Ready")
                        
                    except Exception as e:
                        error_msg = f"Error processing message: {str(e)}"
                        print(f"❌ AI Worker Error: {error_msg}")  # Debug logging
                        self.error_occurred.emit(error_msg)
                        self.status_changed.emit("Error")
                    
                    finally:
                        self.current_task = None
                
                # Small delay to prevent busy waiting
                loop.run_until_complete(asyncio.sleep(0.1))
                
        except Exception as e:
            error_msg = f"AI Worker thread error: {str(e)}"
            print(f"❌ Critical AI Worker Error: {error_msg}")  # Debug logging
            self.error_occurred.emit(error_msg)
            self.status_changed.emit("Critical Error")
        finally:
            loop.close()
    
    def stop(self):
        """Stop the worker thread"""
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
        self.setWindowTitle("Heimdall AI Assistant - Working Demo")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("👁 Heimdall AI Assistant")
        header.setStyleSheet("""
            QLabel {
                color: #d4af37; 
                font-size: 28px; 
                font-weight: bold; 
                padding: 25px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a1a, stop:1 #2a2a2a);
                border-radius: 15px;
                margin-bottom: 15px;
                border: 2px solid #333;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Status and controls
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        
        self.status_label = QLabel("🔄 Starting up...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                padding: 8px 15px;
                background: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        
        # Auto-analyze toggle
        self.auto_analyze_checkbox = QCheckBox("Auto-analyze OCR")
        self.auto_analyze_checkbox.setChecked(True)
        self.auto_analyze_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:checked {
                background: #d4af37;
                border: 2px solid #b8860b;
            }
            QCheckBox::indicator:unchecked {
                background: #3a3a3a;
                border: 2px solid #555;
            }
        """)
        self.auto_analyze_checkbox.toggled.connect(self.toggle_auto_analyze)
        
        # Quick action buttons
        self.read_btn = QPushButton("📖 Read Screen")
        self.voice_btn = QPushButton("🎤 Voice")
        self.help_btn = QPushButton("🆘 Help")
        self.debug_btn = QPushButton("🐛 Debug")
        self.cancel_btn = QPushButton("🚫 Cancel")
        
        for btn in [self.read_btn, self.voice_btn, self.help_btn, self.debug_btn, self.cancel_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #3a3a3a;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 8px;
                    padding: 8px 15px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #4a4a4a;
                    border-color: #d4af37;
                }
                QPushButton:pressed {
                    background: #2a2a2a;
                }
            """)
        
        # Special styling for cancel button
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #8B0000;
                color: white;
                border: 1px solid #A52A2A;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #A52A2A;
                border-color: #FF6B6B;
            }
            QPushButton:pressed {
                background: #660000;
            }
        """)
        
        self.read_btn.clicked.connect(self.capture_and_read_screen)
        self.voice_btn.clicked.connect(lambda: self.send_quick_message("Voice commands help"))
        self.help_btn.clicked.connect(lambda: self.send_quick_message("Help"))
        self.debug_btn.clicked.connect(self.toggle_debug_panel)
        self.cancel_btn.clicked.connect(self.cancel_current_processing)
    
    def toggle_auto_analyze(self, checked):
        """Toggle auto-analysis of OCR results"""
        self.auto_analyze_ocr = checked
        if hasattr(self, 'screen_worker'):
            self.screen_worker.set_auto_analyze(checked)
        
        status = "enabled" if checked else "disabled"
        self.log_to_debug(f"INFO: Auto-analyze OCR {status}")
        
        controls_layout.addWidget(self.status_label)
        controls_layout.addWidget(self.auto_analyze_checkbox)
        controls_layout.addStretch()
        controls_layout.addWidget(self.read_btn)
        controls_layout.addWidget(self.voice_btn)
        controls_layout.addWidget(self.help_btn)
        controls_layout.addWidget(self.debug_btn)
        controls_layout.addWidget(self.cancel_btn)
        layout.addWidget(controls_frame)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a1a);
                color: white;
                border: 2px solid #333;
                border-radius: 15px;
                padding: 20px;
                font-size: 14px;
                font-family: 'SF Pro Display', 'Segoe UI', Arial;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #d4af37;
                border-radius: 6px;
                min-height: 20px;
            }
        """)
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)
        
        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: #2a2a2a;
                border-radius: 15px;
                border: 2px solid #333;
                padding: 5px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message... (e.g., 'Read my screen', 'Click the blue button', 'Help')")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                color: white;
                border: none;
                padding: 15px 20px;
                font-size: 14px;
                border-radius: 10px;
            }
            QLineEdit:focus {
                background: #3a3a3a;
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
                border-radius: 12px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
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
        
        # Debug panel (initially hidden)
        self.debug_panel = QTextEdit()
        self.debug_panel.setMaximumHeight(150)
        self.debug_panel.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a;
                color: #888;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
                font-size: 11px;
                font-family: 'Courier New', monospace;
            }
        """)
        self.debug_panel.setPlaceholderText("Debug logs will appear here...")
        self.debug_panel.hide()  # Hidden by default
        layout.addWidget(self.debug_panel)
        
        # Welcome message
        ai_status = "Real AI" if REAL_AI_AVAILABLE else "Mock AI (components missing)"
        screen_status = "Available" if SCREEN_CAPTURE_AVAILABLE else "Missing components"
        
        self.add_message(f"Welcome to Heimdall AI Assistant! 👁 ({ai_status})", False)
        self.add_message("I'm your intelligent screen control and automation assistant.", False)
        self.add_message("", False)
        self.add_message("🎯 **Quick Start:**", False)
        self.add_message("• Click '📖 Read Screen' for real OCR analysis", False)
        self.add_message("• Type 'Help' for full command list", False)
        self.add_message("• Use 'Click the blue button' for UI control", False)
        self.add_message("• Toggle 'Auto-analyze OCR' for AI interpretation", False)
        self.add_message("", False)
        
        if REAL_AI_AVAILABLE:
            self.add_message("✅ Real AI backend connected! Full functionality available.", False)
        else:
            self.add_message("⚠️ Running in mock mode. Install missing components for full AI.", False)
        
        if SCREEN_CAPTURE_AVAILABLE:
            self.add_message("✅ Screen capture ready! OCR with Tesseract available.", False)
        else:
            self.add_message("⚠️ Screen capture unavailable. Install with: pip install pyautogui pytesseract", False)
            self.add_message("   For Tesseract: brew install tesseract (macOS)", False)
        
        self.add_message("", False)
        self.add_message("Ready to assist! Click 'Read Screen' or type a command.", False)
    
    def setup_ai(self):
        """Setup AI worker thread with real AI integration"""
        self.ai_worker = AIWorker()
        self.ai_worker.result_ready.connect(self.handle_ai_result)
        self.ai_worker.error_occurred.connect(self.handle_ai_error)
        self.ai_worker.status_changed.connect(self.handle_status_change)
        self.ai_worker.start()
        
        # Setup screen capture worker
        self.screen_worker = ScreenCaptureWorker()
        self.screen_worker.capture_complete.connect(self.handle_screen_capture_complete)
        self.screen_worker.capture_error.connect(self.handle_screen_capture_error)
        self.screen_worker.status_changed.connect(self.handle_status_change)
        
        # Track message placeholders for replacement
        self.pending_messages = {}  # message_id -> placeholder_info
        self.auto_analyze_ocr = True  # Setting for auto-analyzing OCR results
    
    def send_message(self):
        """Send user message"""
        text = self.input_field.text().strip()
        if not text:
            return
        
        self.send_quick_message(text)
        self.input_field.clear()
    
    def send_quick_message(self, text):
        """Send a quick message (from buttons or input)"""
        # Add user message to chat
        self.add_message(text, True)
        
        # Add "Thinking..." placeholder for assistant response
        placeholder_id = self.add_thinking_placeholder()
        
        # Disable send button while processing
        self.send_btn.setEnabled(False)
        self.send_btn.setText("Processing...")
        
        # Send to AI worker
        if self.ai_worker:
            simulate = True  # Default to simulation mode for safety
            self.ai_worker.add_message(text, simulate)
            
            # Store placeholder info for later replacement
            self.pending_messages[text] = {
                'placeholder_id': placeholder_id,
                'timestamp': datetime.now()
            }
    
    def add_thinking_placeholder(self):
        """Add a thinking placeholder that can be replaced later"""
        placeholder_text = "🤔 Thinking..."
        placeholder_id = id(placeholder_text)  # Simple ID generation
        
        formatted = f'''
        <div id="msg_{placeholder_id}" style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #1a1a1a, #2a2a2a); border-radius: 15px; border-left: 4px solid #d4af37;">
            <b style="color: #d4af37; font-size: 16px;">🤖 Heimdall:</b><br>
            <span style="color: #888; font-size: 14px; line-height: 1.6; font-style: italic;">{placeholder_text}</span>
        </div>
        '''
        
        self.chat_area.append(formatted)
        self.auto_scroll()
        
        return placeholder_id
    
    def replace_placeholder_with_result(self, placeholder_id, result):
        """Replace thinking placeholder with actual AI result"""
        reply = result.get('reply', 'No response')
        intent = result.get('intent', {})
        executed = result.get('executed', False)
        execution_result = result.get('execution_result')
        
        # Format the main response
        response_html = f'<span style="color: white; font-size: 14px; line-height: 1.6;">{reply.replace(chr(10), "<br>")}</span>'
        
        # Add execution plan if available
        if intent.get('type') == 'automation':
            if executed and execution_result:
                response_html += f'<br><br><span style="color: #90EE90; font-size: 12px;">✅ <b>Executed:</b> {execution_result}</span>'
            elif not executed:
                response_html += f'<br><br><span style="color: #FFD700; font-size: 12px;">⚠️ <b>Simulation Mode:</b> Action planned but not executed</span>'
        
        # Add intent information for debugging (if not basic chat)
        if intent.get('type') not in ['chat', 'greeting', 'help']:
            intent_info = f"Intent: {intent.get('type', 'unknown')}"
            if intent.get('action'):
                intent_info += f" → {intent.get('action')}"
            if intent.get('confidence'):
                intent_info += f" (confidence: {intent.get('confidence'):.1f})"
            response_html += f'<br><br><span style="color: #888; font-size: 11px;">🧠 {intent_info}</span>'
        
        # Replace the placeholder content
        # Note: This is a simplified replacement - in a real implementation,
        # you might want to use a more sophisticated method to update specific messages
        formatted = f'''
        <div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #1a1a1a, #2a2a2a); border-radius: 15px; border-left: 4px solid #d4af37;">
            <b style="color: #d4af37; font-size: 16px;">🤖 Heimdall:</b><br>
            {response_html}
        </div>
        '''
        
        self.chat_area.append(formatted)
        self.auto_scroll()
    
    def replace_placeholder_with_error(self, placeholder_id, error_msg):
        """Replace thinking placeholder with error message"""
        error_html = f'<span style="color: #FF6B6B; font-size: 14px;">❌ Error processing — check logs<br><small>{error_msg}</small></span>'
        
        formatted = f'''
        <div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #2a1a1a, #3a1a1a); border-radius: 15px; border-left: 4px solid #FF6B6B;">
            <b style="color: #FF6B6B; font-size: 16px;">🤖 Heimdall:</b><br>
            {error_html}
        </div>
        '''
        
        self.chat_area.append(formatted)
        self.auto_scroll()
        
        # Log to debug panel
        self.log_to_debug(f"ERROR: {error_msg}")
    
    def auto_scroll(self):
        """Auto-scroll chat area to bottom"""
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def log_to_debug(self, message):
        """Log message to debug panel"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        debug_msg = f"[{timestamp}] {message}"
        
        # Safety check - debug panel might not be initialized yet
        if hasattr(self, 'debug_panel'):
            self.debug_panel.append(debug_msg)
            
            # Show debug panel if there are errors
            if "ERROR" in message:
                self.debug_panel.show()
        else:
            # Fallback to console logging during initialization
            print(debug_msg)
    
    def toggle_debug_panel(self):
        """Toggle debug panel visibility"""
        if self.debug_panel.isVisible():
            self.debug_panel.hide()
        else:
            self.debug_panel.show()
    
    def add_message(self, message, is_user=False):
        """Add message to chat area"""
        if is_user:
            formatted = f'''
            <div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #8b5cf6, #6366f1); border-radius: 15px; border-left: 4px solid #a855f7;">
                <b style="color: white; font-size: 16px;">🧑 You:</b><br>
                <span style="color: white; font-size: 14px; line-height: 1.4;">{message}</span>
            </div>
            '''
        else:
            formatted = f'''
            <div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #1a1a1a, #2a2a2a); border-radius: 15px; border-left: 4px solid #d4af37;">
                <b style="color: #d4af37; font-size: 16px;">🤖 Heimdall:</b><br>
                <span style="color: white; font-size: 14px; line-height: 1.6;">{message.replace(chr(10), '<br>')}</span>
            </div>
            '''
        
        self.chat_area.append(formatted)
        
        # Auto-scroll to bottom
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def handle_ai_result(self, result):
        """Handle successful AI result"""
        # Find the most recent pending message to replace its placeholder
        if self.pending_messages:
            # Get the most recent message (simple approach)
            latest_msg = max(self.pending_messages.items(), key=lambda x: x[1]['timestamp'])
            message_text, msg_info = latest_msg
            
            # Replace placeholder with result
            self.replace_placeholder_with_result(msg_info['placeholder_id'], result)
            
            # Remove from pending
            del self.pending_messages[message_text]
        
        # Re-enable send button
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")
        
        # Log successful processing
        intent_type = result.get('intent', {}).get('type', 'unknown')
        self.log_to_debug(f"SUCCESS: Processed {intent_type} intent")
        
        # TODO: Hook for streaming partial results
        # This is where you would handle partial/streaming responses:
        # - Connect to a 'partial_result' signal from the AI worker
        # - Update the placeholder incrementally as tokens arrive
        # - Show typing indicators or progress bars for long operations
        # Example:
        # def handle_partial_result(self, partial_text, placeholder_id):
        #     self.update_placeholder_partial(placeholder_id, partial_text)
    
    def handle_ai_error(self, error_msg):
        """Handle AI processing error"""
        # Find the most recent pending message to replace its placeholder
        if self.pending_messages:
            latest_msg = max(self.pending_messages.items(), key=lambda x: x[1]['timestamp'])
            message_text, msg_info = latest_msg
            
            # Replace placeholder with error
            self.replace_placeholder_with_error(msg_info['placeholder_id'], error_msg)
            
            # Remove from pending
            del self.pending_messages[message_text]
        
        # Re-enable send button
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")
        
        # Log error
        self.log_to_debug(f"ERROR: {error_msg}")
    
    def handle_status_change(self, status):
        """Handle AI worker status change"""
        status_icons = {
            "Initializing AI...": "🔄",
            "Ready": "🟢",
            "Thinking...": "🧠",
            "Processing...": "⚡",
            "Mock AI Mode": "🎭",
            "Error": "❌",
            "Critical Error": "💥",
            "Cancelled": "🚫"
        }
        
        icon = status_icons.get(status, "🔵")
        self.status_label.setText(f"{icon} {status}")
        
        # Log status changes
        self.log_to_debug(f"STATUS: {status}")
        
        # Update UI based on status (with safety checks)
        if status in ["Thinking...", "Processing..."]:
            # Keep send button disabled during processing
            pass
        elif status in ["Ready", "Mock AI Mode"]:
            # Re-enable send button when ready
            if hasattr(self, 'send_btn') and not self.pending_messages:  # Only if no pending messages
                self.send_btn.setEnabled(True)
                self.send_btn.setText("Send")
        elif status in ["Error", "Critical Error"]:
            # Re-enable send button on error
            if hasattr(self, 'send_btn'):
                self.send_btn.setEnabled(True)
                self.send_btn.setText("Send")
    
    def cancel_current_processing(self):
        """Cancel current AI processing (if feasible)"""
        if self.ai_worker and self.pending_messages:
            self.ai_worker.cancel_current_task()
            
            # Clear pending messages
            for message_text, msg_info in self.pending_messages.items():
                self.replace_placeholder_with_error(
                    msg_info['placeholder_id'], 
                    "Processing cancelled by user"
                )
            
            self.pending_messages.clear()
            
            # Re-enable send button
            self.send_btn.setEnabled(True)
            self.send_btn.setText("Send")
            
            self.log_to_debug("INFO: Processing cancelled by user")
    
    def capture_and_read_screen(self):
        """Capture screen and perform OCR"""
        # Disable read button during capture
        self.read_btn.setEnabled(False)
        self.read_btn.setText("Capturing...")
        
        # Add user action message
        self.add_message("📖 Read my screen", True)
        
        # Add processing placeholder
        placeholder_id = self.add_thinking_placeholder()
        
        # Store placeholder for screen capture
        self.pending_messages["screen_capture"] = {
            'placeholder_id': placeholder_id,
            'timestamp': datetime.now()
        }
        
        # Start screen capture in background thread
        if hasattr(self, 'screen_worker'):
            self.screen_worker.set_auto_analyze(self.auto_analyze_ocr)
            self.screen_worker.start()
        else:
            self.handle_screen_capture_error("Screen capture worker not initialized")
    
    def handle_screen_capture_complete(self, full_text, truncated_text):
        """Handle successful screen capture and OCR"""
        # Re-enable read button
        self.read_btn.setEnabled(True)
        self.read_btn.setText("📖 Read Screen")
        
        # Create expandable OCR result
        ocr_result = self.create_expandable_ocr_result(full_text, truncated_text)
        
        # Replace placeholder with OCR result
        if "screen_capture" in self.pending_messages:
            msg_info = self.pending_messages["screen_capture"]
            self.replace_placeholder_with_ocr_result(msg_info['placeholder_id'], ocr_result, full_text, truncated_text)
            del self.pending_messages["screen_capture"]
        
        # Auto-analyze with AI if enabled
        if self.auto_analyze_ocr and full_text.strip():
            snippet = truncated_text if len(full_text) > 500 else full_text
            analysis_prompt = f"Read screen: {snippet}"
            
            # Add a small delay to let user see the OCR result first
            QTimer.singleShot(1000, lambda: self.send_quick_message(analysis_prompt))
        
        self.log_to_debug(f"SUCCESS: Screen capture completed, {len(full_text)} characters extracted")
    
    def handle_screen_capture_error(self, error_msg):
        """Handle screen capture error"""
        # Re-enable read button
        self.read_btn.setEnabled(True)
        self.read_btn.setText("📖 Read Screen")
        
        # Replace placeholder with error
        if "screen_capture" in self.pending_messages:
            msg_info = self.pending_messages["screen_capture"]
            self.replace_placeholder_with_error(msg_info['placeholder_id'], error_msg)
            del self.pending_messages["screen_capture"]
        
        self.log_to_debug(f"ERROR: Screen capture failed - {error_msg}")
    
    def create_expandable_ocr_result(self, full_text, truncated_text):
        """Create an expandable OCR result with show more/less functionality"""
        char_count = len(full_text)
        word_count = len(full_text.split())
        
        result = {
            'type': 'ocr_result',
            'full_text': full_text,
            'truncated_text': truncated_text,
            'char_count': char_count,
            'word_count': word_count,
            'is_truncated': len(full_text) > 500
        }
        
        return result
    
    def replace_placeholder_with_ocr_result(self, placeholder_id, ocr_result, full_text, truncated_text):
        """Replace thinking placeholder with OCR result"""
        char_count = ocr_result['char_count']
        word_count = ocr_result['word_count']
        is_truncated = ocr_result['is_truncated']
        
        # Create the main OCR display
        ocr_html = f'''
        <div style="background: #2a2a2a; border-radius: 8px; padding: 15px; margin: 10px 0;">
            <div style="color: #d4af37; font-weight: bold; margin-bottom: 10px;">
                📖 Screen Content ({word_count} words, {char_count} characters)
            </div>
            <div style="color: white; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4; white-space: pre-wrap; background: #1a1a1a; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto;">
{truncated_text.replace('<', '&lt;').replace('>', '&gt;')}
            </div>
        '''
        
        if is_truncated:
            ocr_html += f'''
            <div style="margin-top: 10px;">
                <button onclick="this.style.display='none'; this.nextElementSibling.style.display='block';" 
                        style="background: #d4af37; color: black; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 11px;">
                    📄 Show Full Text
                </button>
                <div style="display: none;">
                    <div style="color: white; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4; white-space: pre-wrap; background: #1a1a1a; padding: 10px; border-radius: 5px; margin-top: 5px; max-height: 400px; overflow-y: auto;">
{full_text.replace('<', '&lt;').replace('>', '&gt;')}
                    </div>
                    <button onclick="this.parentElement.style.display='none'; this.parentElement.previousElementSibling.style.display='inline-block';" 
                            style="background: #666; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 11px; margin-top: 5px;">
                        📄 Show Less
                    </button>
                </div>
            </div>
            '''
        
        ocr_html += '</div>'
        
        # Add analysis info
        analysis_info = ""
        if self.auto_analyze_ocr:
            analysis_info = '<br><span style="color: #888; font-size: 11px;">🧠 Auto-analyzing with AI...</span>'
        
        # Complete formatted response
        formatted = f'''
        <div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #1a1a1a, #2a2a2a); border-radius: 15px; border-left: 4px solid #d4af37;">
            <b style="color: #d4af37; font-size: 16px;">🤖 Heimdall:</b><br>
            <span style="color: white; font-size: 14px; line-height: 1.6;">
                ✅ Screen captured and analyzed successfully!
                {ocr_html}
                {analysis_info}
            </span>
        </div>
        '''
        
        self.chat_area.append(formatted)
        self.auto_scroll()
    
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
    
    print("✅ Heimdall AI Assistant started!")
    print("🎯 Try typing: 'Help', 'Read my screen', or 'Click the blue button'")
    print("🚀 This is a working demo showing AI integration!")
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())