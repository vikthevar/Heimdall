#!/usr/bin/env python3
"""
Heimdall Real AI - GUI with Real AI Integration
Connects GUI to the actual AI brain with all components
"""
import sys
import os
import asyncio
import threading
import json
from datetime import datetime

# Global configuration - will be loaded after imports
DEMO_SAFE_MODE = True  # Default, will be updated from settings

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                               QLabel, QFrame, QCheckBox, QMessageBox, QDialog)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Import the real AI Brain
from src.ai.heimdall_brain import heimdall_brain

# Import settings system
try:
    from src.core.settings_manager import settings_manager, get_setting, set_setting
    from src.ui.settings_dialog import show_settings_dialog
    SETTINGS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Settings system not available: {e}")
    SETTINGS_AVAILABLE = False
    def get_setting(key, default=None):
        return default
    def set_setting(key, value):
        return True
    def show_settings_dialog(parent=None):
        pass

# Import automation components
try:
    from src.core.screen_controller import execute_intent, render_plan
    AUTOMATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Automation not available: {e}")
    AUTOMATION_AVAILABLE = False
    def execute_intent(intent):
        return "❌ Automation components not available"
    def render_plan(intent):
        return "❌ Plan rendering not available"

# Import voice components
try:
    from src.core.voice_handler import record_and_transcribe
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Voice components not available: {e}")
    VOICE_AVAILABLE = False
    def record_and_transcribe():
        return "❌ Voice components not available"

# Import database for audit logging and conversation history
try:
    from src.storage.db import save_message, load_recent_messages
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    def save_message(*args, **kwargs):
        pass
    def load_recent_messages(limit=20):
        return []

class VoiceRecordingWorker(QThread):
    """Background thread for voice recording and transcription"""
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    transcription_ready = pyqtSignal(str)  # transcript text
    recording_error = pyqtSignal(str)  # error message
    recording_time_update = pyqtSignal(int)  # elapsed seconds
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.should_stop = False
        self.max_duration = 8  # Maximum recording duration in seconds
    
    def start_recording(self):
        """Start voice recording"""
        self.is_recording = True
        self.should_stop = False
        self.start()
    
    def stop_recording(self):
        """Stop voice recording"""
        self.should_stop = True
    
    def run(self):
        """Record audio and transcribe"""
        try:
            if not VOICE_AVAILABLE:
                self.recording_error.emit("Voice components not available. Install: pip install pyttsx3 sounddevice")
                return
            
            self.recording_started.emit()
            
            # Simulate recording with time updates
            elapsed = 0
            while self.is_recording and not self.should_stop and elapsed < self.max_duration:
                self.msleep(1000)  # Sleep for 1 second
                elapsed += 1
                self.recording_time_update.emit(elapsed)
            
            self.recording_stopped.emit()
            
            # Call the actual transcription function
            try:
                transcript = record_and_transcribe()
                
                if transcript and not transcript.startswith("❌"):
                    self.transcription_ready.emit(transcript)
                else:
                    self.recording_error.emit(transcript or "No speech detected")
                    
            except Exception as e:
                if "permission" in str(e).lower() or "access" in str(e).lower():
                    self.recording_error.emit("Mic access denied — please allow microphone or type command")
                else:
                    self.recording_error.emit(f"Transcription failed: {str(e)}")
                    
        except Exception as e:
            self.recording_error.emit(f"Recording failed: {str(e)}")
        finally:
            self.is_recording = False

class TTSWorker(QThread):
    """Background thread for text-to-speech"""
    tts_started = pyqtSignal()
    tts_finished = pyqtSignal()
    tts_error = pyqtSignal(str)
    
    def __init__(self, text):
        super().__init__()
        self.text = text
    
    def run(self):
        """Speak the text using TTS"""
        try:
            if not VOICE_AVAILABLE:
                self.tts_error.emit("TTS not available")
                return
            
            self.tts_started.emit()
            
            # Initialize TTS engine
            engine = pyttsx3.init()
            
            # Set properties (optional)
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
            
            # Speak the text
            engine.say(self.text)
            engine.runAndWait()
            
            self.tts_finished.emit()
            
        except Exception as e:
            self.tts_error.emit(f"TTS failed: {str(e)}")

class ExecutionWorker(QThread):
    """Background thread for executing automation actions"""
    execution_complete = pyqtSignal(dict, str)  # intent, result
    execution_error = pyqtSignal(dict, str)  # intent, error
    
    def __init__(self, intent):
        super().__init__()
        self.intent = intent
    
    def run(self):
        """Execute the automation intent"""
        try:
            if not AUTOMATION_AVAILABLE:
                self.execution_error.emit(self.intent, "Automation components not available")
                return
            
            # Log execution attempt
            self.log_execution_attempt()
            
            # Execute the intent
            result = execute_intent(self.intent)
            
            # Log execution result
            self.log_execution_result(result, success=True)
            
            self.execution_complete.emit(self.intent, result)
            
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.log_execution_result(error_msg, success=False)
            self.execution_error.emit(self.intent, error_msg)
    
    def log_execution_attempt(self):
        """Log execution attempt to database"""
        if DATABASE_AVAILABLE:
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'intent': self.intent,
                'action': 'execution_attempt',
                'user': 'user',  # In a real app, this would be the actual user
                'plan': render_plan(self.intent) if AUTOMATION_AVAILABLE else "N/A"
            }
            # Save to audit log (you might want a separate audit table)
            save_message(
                f"EXECUTION_ATTEMPT: {self.intent.get('action', 'unknown')}",
                json.dumps(log_data),
                self.intent
            )
    
    def log_execution_result(self, result, success):
        """Log execution result to database"""
        if DATABASE_AVAILABLE:
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'intent': self.intent,
                'action': 'execution_result',
                'success': success,
                'result': result
            }
            save_message(
                f"EXECUTION_RESULT: {'SUCCESS' if success else 'FAILED'}",
                json.dumps(log_data),
                self.intent
            )

class ConfirmationDialog(QDialog):
    """Confirmation dialog for automation execution"""
    
    def __init__(self, intent, plan, parent=None):
        super().__init__(parent)
        self.intent = intent
        self.plan = plan
        self.setup_ui()
    
    def setup_ui(self):
        """Setup confirmation dialog UI"""
        self.setWindowTitle("Confirm Automation Execution")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Warning header
        warning = QLabel("⚠️ CONFIRM REAL ACTIONS")
        warning.setStyleSheet("""
            QLabel {
                color: #FF6B6B;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                background: #2a1a1a;
                border-radius: 8px;
                border: 2px solid #FF6B6B;
            }
        """)
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning)
        
        # Confirmation text
        confirm_text = QLabel("This will move/click/keyboard on this machine. Proceed?")
        confirm_text.setStyleSheet("color: white; font-size: 14px; padding: 10px;")
        confirm_text.setWordWrap(True)
        layout.addWidget(confirm_text)
        
        # Plan display
        plan_label = QLabel("Execution Plan:")
        plan_label.setStyleSheet("color: #d4af37; font-weight: bold; padding: 5px;")
        layout.addWidget(plan_label)
        
        plan_display = QTextEdit()
        plan_display.setPlainText(self.plan)
        plan_display.setReadOnly(True)
        plan_display.setMaximumHeight(150)
        plan_display.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a;
                color: white;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }
        """)
        layout.addWidget(plan_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #666;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background: #777; }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        execute_btn = QPushButton("⚡ Execute")
        execute_btn.setStyleSheet("""
            QPushButton {
                background: #FF6B6B;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background: #FF5252; }
        """)
        execute_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(execute_btn)
        layout.addLayout(button_layout)
        
        # Apply dark theme
        self.setStyleSheet("QDialog { background: #0a0a0a; }")

class AIWorker(QThread):
    """Background thread for real AI processing"""
    response_ready = pyqtSignal(dict)  # Send full result dict
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.message_queue = []
        self.running = True
        self.simulate_actions = True  # Default to simulation mode
        
    def add_message(self, message, simulate=True):
        """Add message to processing queue"""
        self.message_queue.append((message, simulate))
    
    def set_simulation_mode(self, simulate):
        """Set whether to simulate or execute actions"""
        self.simulate_actions = simulate
    
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
                    message, simulate = self.message_queue.pop(0)
                    self.status_changed.emit("Processing...")
                    
                    # Process with real AI
                    result = loop.run_until_complete(
                        heimdall_brain.process_message(message, simulate_actions=simulate)
                    )
                    
                    # If it's an automation intent, add execution plan
                    if result.get('intent', {}).get('type') == 'automation':
                        intent = result['intent']
                        if AUTOMATION_AVAILABLE:
                            plan = render_plan(intent)
                            result['execution_plan'] = plan
                        else:
                            result['execution_plan'] = "❌ Automation components not available"
                    
                    self.response_ready.emit(result)
                    self.status_changed.emit("Ready")
                
                # Small delay
                loop.run_until_complete(asyncio.sleep(0.1))
                
        except Exception as e:
            error_result = {
                'reply': f"❌ Error: {str(e)}",
                'intent': {'type': 'error'},
                'executed': False,
                'execution_result': None
            }
            self.response_ready.emit(error_result)
            self.status_changed.emit("Error")
        finally:
            loop.close()
    
    def stop(self):
        """Stop the worker"""
        self.running = False

class HeimdallWindow(QMainWindow):
    """Heimdall GUI with Real AI Integration"""
    
    def __init__(self):
        super().__init__()
        self.ai_worker = None
        self.voice_worker = None
        self.tts_worker = None
        self.is_recording = False
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_ui)
        self.recording_start_time = None
        
        # Load settings
        self.load_settings_from_db()
        
        self.setup_ui()
        self.setup_ai()
    
    def load_settings_from_db(self):
        """Load settings from database"""
        global DEMO_SAFE_MODE
        
        if SETTINGS_AVAILABLE:
            # Load all settings into instance variables
            self.voice_output_enabled = get_setting('voice_output_enabled', True)
            self.voice_input_enabled = get_setting('voice_input_enabled', True)
            self.simulation_mode = get_setting('simulation_mode', True)
            self.auto_analyze_ocr = get_setting('auto_analyze_ocr', True)
            self.debug_mode = get_setting('debug_mode', False)
            self.max_recording_duration = get_setting('max_recording_duration', 8)
            self.auto_send_transcript = get_setting('auto_send_transcript', True)
            
            # Update global settings
            DEMO_SAFE_MODE = get_setting('demo_safe_mode', True)
        else:
            # Fallback defaults
            self.voice_output_enabled = True
            self.voice_input_enabled = True
            self.simulation_mode = True
            self.auto_analyze_ocr = True
            self.debug_mode = False
            self.max_recording_duration = 8
            self.auto_send_transcript = True
            
            # Update global with default
            DEMO_SAFE_MODE = True
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Heimdall AI Assistant - Real AI Integration")
        self.setGeometry(100, 100, 1000, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("👁 Heimdall AI Assistant - Real AI")
        header.setStyleSheet("""
            QLabel {
                color: #d4af37; 
                font-size: 32px; 
                font-weight: bold; 
                padding: 30px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a1a, stop:1 #2a2a2a);
                border-radius: 15px;
                margin-bottom: 15px;
                border: 2px solid #333;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Demo Safe Mode Banner
        if DEMO_SAFE_MODE:
            self.safe_mode_banner = QLabel("🔒 DEMO SAFE MODE - Automation execution disabled for safety")
            self.safe_mode_banner.setStyleSheet("""
                QLabel {
                    color: white;
                    background: #8B0000;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
            """)
            self.safe_mode_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.safe_mode_banner)
        
        # Controls and status
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        
        self.status_label = QLabel("🔄 Starting up...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                padding: 10px 15px;
                background: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        
        # Simulation mode toggle
        self.simulation_checkbox = QCheckBox("Simulation Mode")
        self.simulation_checkbox.setChecked(self.simulation_mode)
        self.simulation_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
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
        self.simulation_checkbox.toggled.connect(self.toggle_simulation_mode)
        
        # Voice output toggle
        self.voice_output_checkbox = QCheckBox("Voice Output")
        self.voice_output_checkbox.setChecked(self.voice_output_enabled)
        self.voice_output_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background: #4CAF50;
                border: 2px solid #45a049;
            }
            QCheckBox::indicator:unchecked {
                background: #3a3a3a;
                border: 2px solid #555;
            }
        """)
        self.voice_output_checkbox.toggled.connect(self.toggle_voice_output)
        
        # Quick action buttons
        self.read_btn = QPushButton("📖 Read Screen")
        self.click_btn = QPushButton("🖱️ Click Demo")
        self.voice_btn = QPushButton("🎤 Voice")
        self.voice_btn.setCheckable(True)  # Make it toggleable for recording state
        self.help_btn = QPushButton("🆘 Help")
        self.settings_btn = QPushButton("⚙️ Settings")
        self.export_btn = QPushButton("📤 Export")
        
        for btn in [self.read_btn, self.click_btn, self.voice_btn, self.help_btn, self.settings_btn, self.export_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #3a3a3a;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 8px;
                    padding: 10px 15px;
                    font-size: 12px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: #4a4a4a;
                    border-color: #d4af37;
                }
                QPushButton:pressed {
                    background: #2a2a2a;
                }
            """)
        
        self.read_btn.clicked.connect(lambda: self.send_quick_message("Read my screen"))
        self.click_btn.clicked.connect(lambda: self.send_quick_message("Click the submit button"))
        self.voice_btn.clicked.connect(self.toggle_voice_recording)
        self.help_btn.clicked.connect(self.show_help_and_stats)
        self.settings_btn.clicked.connect(self.show_settings)
        self.export_btn.clicked.connect(self.export_conversation)
        
        # Add safe mode toggle button
        self.safe_mode_btn = QPushButton("🔒 Safe Mode" if DEMO_SAFE_MODE else "🔓 Live Mode")
        self.safe_mode_btn.setStyleSheet(f"""
            QPushButton {{
                background: {'#8B0000' if DEMO_SAFE_MODE else '#4CAF50'};
                color: white;
                border: 1px solid {'#A52A2A' if DEMO_SAFE_MODE else '#45a049'};
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: {'#A52A2A' if DEMO_SAFE_MODE else '#45a049'};
            }}
        """)
        self.safe_mode_btn.clicked.connect(self.toggle_safe_mode)
        
        controls_layout.addWidget(self.status_label)
        controls_layout.addWidget(self.simulation_checkbox)
        controls_layout.addWidget(self.voice_output_checkbox)
        controls_layout.addStretch()
        controls_layout.addWidget(self.read_btn)
        controls_layout.addWidget(self.click_btn)
        controls_layout.addWidget(self.voice_btn)
        controls_layout.addWidget(self.help_btn)
        controls_layout.addWidget(self.settings_btn)
        controls_layout.addWidget(self.export_btn)
        controls_layout.addWidget(self.safe_mode_btn)
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
        self.input_field.setPlaceholderText("Type your message... (e.g., 'Read my screen', 'Click the blue button', 'Scroll down')")
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
        
        # Welcome message
        self.add_message("Welcome to Heimdall AI Assistant with Real AI! 👁", False)
        self.add_message("I'm connected to the full AI backend with real capabilities:", False)
        self.add_message("", False)
        self.add_message("🎯 **Real AI Features:**", False)
        self.add_message("• Natural language understanding with intent parsing", False)
        self.add_message("• Real screen capture and OCR analysis", False)
        self.add_message("• Automation execution with safety controls", False)
        self.add_message("• Voice recognition and text-to-speech", False)
        self.add_message("• Persistent conversation history with audit trail", False)
        self.add_message("", False)
        
        if DEMO_SAFE_MODE:
            self.add_message("🔒 **Demo Safe Mode:** ON - Automation execution disabled for safety", False)
            self.add_message("Click the 'Safe Mode' button to toggle automation execution", False)
        else:
            self.add_message("🔓 **Live Mode:** ON - Real automation execution enabled", False)
            self.add_message("⚠️ **Warning:** Automation will perform real actions on your system", False)
        
        self.add_message("", False)
        self.add_message("🎯 **Try Commands:**", False)
        self.add_message("• Click '🎤 Voice' to record voice commands", False)
        self.add_message("• 'Click the submit button' - Shows automation plan with execute/simulate options", False)
        self.add_message("• 'Scroll down' - Automation with safety confirmation", False)
        self.add_message("• Click '⚙️ Settings' to customize preferences", False)
        self.add_message("• Click '📤 Export' to save conversation history to JSON", False)
        self.add_message("", False)
        
        if VOICE_AVAILABLE:
            max_duration = get_setting('max_recording_duration', 8)
            self.add_message(f"🎤 Voice features ready! Recording duration: {max_duration}s", False)
        else:
            self.add_message("⚠️ Voice unavailable. Install: pip install pyttsx3 sounddevice", False)
        
        if SETTINGS_AVAILABLE:
            self.add_message("⚙️ Settings system ready! All preferences are saved to database.", False)
        else:
            self.add_message("⚠️ Settings system unavailable. Using default preferences.", False)
        
        self.add_message("", False)
        self.add_message("Ready for real AI assistance! What would you like me to do?", False)
        
        # Load conversation history
        self.load_conversation_history()
    
    def setup_ai(self):
        """Setup AI worker thread"""
        self.ai_worker = AIWorker()
        self.ai_worker.response_ready.connect(self.handle_ai_response)
        self.ai_worker.status_changed.connect(self.handle_status_change)
        self.ai_worker.start()
    
    def toggle_simulation_mode(self, checked):
        """Toggle simulation mode"""
        self.simulation_mode = checked
        if self.ai_worker:
            self.ai_worker.set_simulation_mode(checked)
        
        if SETTINGS_AVAILABLE:
            set_setting('simulation_mode', checked)
        
        mode_text = "ON (safe mode)" if checked else "OFF (real execution)"
        self.add_message(f"🔧 Simulation mode: {mode_text}", False)
    
    def toggle_voice_output(self, checked):
        """Toggle voice output"""
        self.voice_output_enabled = checked
        if SETTINGS_AVAILABLE:
            set_setting('voice_output_enabled', checked)
        status = "enabled" if checked else "disabled"
        self.add_message(f"🔊 Voice output {status}", False)
    
    def toggle_voice_recording(self):
        """Toggle voice recording on/off"""
        if not self.is_recording:
            self.start_voice_recording()
        else:
            self.stop_voice_recording()
    
    def start_voice_recording(self):
        """Start voice recording"""
        if not VOICE_AVAILABLE:
            self.show_toast("Voice components not available. Install: pip install pyttsx3 sounddevice")
            return
        
        if not self.voice_input_enabled:
            self.show_toast("Voice input is disabled in settings")
            return
        
        self.is_recording = True
        self.recording_start_time = datetime.now()
        
        # Update UI
        self.voice_btn.setText("🔴 Recording...")
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: #FF4444;
                color: white;
                border: 1px solid #FF6666;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #FF6666;
            }
        """)
        
        # Start recording worker
        self.voice_worker = VoiceRecordingWorker()
        self.voice_worker.max_duration = self.max_recording_duration  # Use setting
        self.voice_worker.recording_started.connect(self.handle_recording_started)
        self.voice_worker.recording_stopped.connect(self.handle_recording_stopped)
        self.voice_worker.transcription_ready.connect(self.handle_transcription_ready)
        self.voice_worker.recording_error.connect(self.handle_recording_error)
        self.voice_worker.recording_time_update.connect(self.handle_recording_time_update)
        self.voice_worker.start_recording()
        
        # Start UI timer for pulsing effect
        self.recording_timer.start(500)  # Update every 500ms
        
        self.add_message("🎤 Started voice recording... (max 8 seconds)", False)
    
    def stop_voice_recording(self):
        """Stop voice recording"""
        if self.voice_worker and self.is_recording:
            self.voice_worker.stop_recording()
    
    def handle_recording_started(self):
        """Handle recording started signal"""
        pass  # UI already updated in start_voice_recording
    
    def handle_recording_stopped(self):
        """Handle recording stopped signal"""
        self.is_recording = False
        self.recording_timer.stop()
        
        # Reset UI
        self.voice_btn.setText("🎤 Voice")
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: #3a3a3a;
                color: white;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #4a4a4a;
                border-color: #d4af37;
            }
        """)
        self.voice_btn.setChecked(False)
    
    def handle_transcription_ready(self, transcript):
        """Handle successful transcription"""
        self.add_message("🎤 Voice recording complete!", False)
        self.add_message(f"📝 Transcript: \"{transcript}\"", False)
        
        # Insert transcript into input field
        self.input_field.setText(transcript)
        
        # Auto-send if transcript is not empty and auto-send is enabled
        if transcript.strip() and self.auto_send_transcript:
            # Small delay to let user see the transcript
            QTimer.singleShot(1000, self.send_message)
    
    def handle_recording_error(self, error_msg):
        """Handle recording error"""
        self.is_recording = False
        self.recording_timer.stop()
        
        # Reset UI
        self.handle_recording_stopped()
        
        # Show error
        self.add_message(f"❌ Voice recording failed: {error_msg}", False)
        
        # Show toast for permission errors
        if "access denied" in error_msg.lower() or "permission" in error_msg.lower():
            self.show_toast(error_msg)
    
    def handle_recording_time_update(self, elapsed_seconds):
        """Handle recording time update"""
        if self.is_recording:
            self.voice_btn.setText(f"🔴 Recording... {elapsed_seconds}s")
    
    def update_recording_ui(self):
        """Update recording UI with pulsing effect"""
        if self.is_recording and self.recording_start_time:
            elapsed = (datetime.now() - self.recording_start_time).seconds
            
            # Pulsing effect by alternating button style
            if elapsed % 2 == 0:
                self.voice_btn.setStyleSheet("""
                    QPushButton {
                        background: #FF4444;
                        color: white;
                        border: 2px solid #FF6666;
                        border-radius: 8px;
                        padding: 10px 15px;
                        font-size: 12px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                """)
            else:
                self.voice_btn.setStyleSheet("""
                    QPushButton {
                        background: #CC3333;
                        color: white;
                        border: 2px solid #FF4444;
                        border-radius: 8px;
                        padding: 10px 15px;
                        font-size: 12px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                """)
    
    def show_toast(self, message):
        """Show a toast notification"""
        # Simple message box as toast (you could implement a proper toast later)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Heimdall")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.show()
        
        # Auto-close after 3 seconds
        QTimer.singleShot(3000, msg_box.close)
    
    def speak_text(self, text):
        """Speak text using TTS"""
        if not VOICE_AVAILABLE or not self.voice_output_enabled:
            return
        
        # Clean text for TTS (remove markdown and special characters)
        clean_text = text.replace('**', '').replace('*', '').replace('#', '').replace('`', '')
        clean_text = clean_text.replace('🤖', '').replace('👁', '').replace('✅', '').replace('❌', '')
        clean_text = clean_text.replace('🎯', '').replace('🔧', '').replace('🧠', '')
        
        # Limit text length for TTS
        if len(clean_text) > 200:
            clean_text = clean_text[:200] + "..."
        
        # Start TTS worker
        if clean_text.strip():
            self.tts_worker = TTSWorker(clean_text)
            self.tts_worker.tts_started.connect(self.handle_tts_started)
            self.tts_worker.tts_finished.connect(self.handle_tts_finished)
            self.tts_worker.tts_error.connect(self.handle_tts_error)
            self.tts_worker.start()
    
    def handle_tts_started(self):
        """Handle TTS started"""
        # Could add a speaking indicator here
        pass
    
    def handle_tts_finished(self):
        """Handle TTS finished"""
        # Could remove speaking indicator here
        pass
    
    def handle_tts_error(self, error_msg):
        """Handle TTS error"""
        print(f"TTS Error: {error_msg}")  # Log to console, don't spam user
    
    def load_conversation_history(self):
        """Load recent conversation history from database"""
        if not DATABASE_AVAILABLE:
            return
        
        try:
            # Load last 20 messages
            recent_messages = load_recent_messages(20)
            
            if recent_messages:
                # Add separator for history
                self.add_message("", False)
                self.add_message("📚 **Recent Conversation History:**", False)
                self.add_message("", False)
                
                # Add each message from history
                for msg in recent_messages:
                    user_msg = msg.get('user_message', '')
                    assistant_msg = msg.get('assistant_message', '')
                    timestamp = msg.get('timestamp', '')
                    
                    if user_msg:
                        # Format timestamp
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            time_str = dt.strftime('%H:%M')
                        except:
                            time_str = ''
                        
                        # Add user message with timestamp
                        user_display = f"{user_msg} {f'({time_str})' if time_str else ''}"
                        self.add_message(user_display, True)
                        
                        # Add assistant message
                        if assistant_msg:
                            self.add_message(assistant_msg, False)
                
                # Add separator after history
                self.add_message("", False)
                self.add_message("─" * 50, False)
                self.add_message("", False)
                
                print(f"✅ Loaded {len(recent_messages)} messages from conversation history")
            
        except Exception as e:
            print(f"❌ Failed to load conversation history: {e}")
    
    def export_conversation(self):
        """Export conversation history to JSON file"""
        try:
            if not DATABASE_AVAILABLE:
                self.show_toast("Database not available for export")
                return
            
            # Get all messages from database
            all_messages = load_recent_messages(1000)  # Get up to 1000 messages
            
            if not all_messages:
                self.show_toast("No conversation history to export")
                return
            
            # Prepare export data
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_messages': len(all_messages),
                    'exported_by': 'Heimdall AI Assistant',
                    'version': '1.0'
                },
                'conversations': []
            }
            
            # Format messages for export
            for msg in all_messages:
                conversation_entry = {
                    'id': msg.get('id'),
                    'timestamp': msg.get('timestamp'),
                    'user_message': msg.get('user_message'),
                    'assistant_message': msg.get('assistant_message'),
                    'intent': msg.get('intent'),
                    'created_at': msg.get('created_at')
                }
                export_data['conversations'].append(conversation_entry)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"heimdall_conversation_{timestamp}.json"
            filepath = os.path.join(os.getcwd(), filename)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # Show success message
            success_msg = f"""📤 **Conversation Exported Successfully!**

File: {filename}
Location: {filepath}
Messages: {len(all_messages)}
Size: {os.path.getsize(filepath)} bytes

The conversation history has been saved as a JSON file."""
            
            self.add_message(success_msg, False)
            
            # Show system notification
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Export Complete")
            msg_box.setText(f"Conversation exported to:\n{filename}")
            msg_box.setInformativeText(f"Location: {os.getcwd()}")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.show()
            
        except Exception as e:
            error_msg = f"❌ Export failed: {str(e)}"
            self.add_message(error_msg, False)
            self.show_toast(f"Export failed: {str(e)}")
    
    def clear_conversation_history(self):
        """Clear conversation history (for future use)"""
        reply = QMessageBox.question(
            self, 
            "Clear History", 
            "Are you sure you want to clear all conversation history?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear the chat area
                self.chat_area.clear()
                
                # Add confirmation message
                self.add_message("🗑️ Conversation history cleared", False)
                
                # Note: Database history is preserved for audit trail
                # Only the UI display is cleared
                
            except Exception as e:
                self.show_toast(f"Failed to clear history: {str(e)}")
    
    def get_conversation_stats(self):
        """Get conversation statistics"""
        if not DATABASE_AVAILABLE:
            return None
        
        try:
            all_messages = load_recent_messages(10000)  # Get many messages for stats
            
            if not all_messages:
                return None
            
            stats = {
                'total_messages': len(all_messages),
                'date_range': {
                    'oldest': all_messages[-1].get('created_at') if all_messages else None,
                    'newest': all_messages[0].get('created_at') if all_messages else None
                },
                'message_types': {},
                'total_characters': 0
            }
            
            # Calculate statistics
            for msg in all_messages:
                user_msg = msg.get('user_message', '')
                assistant_msg = msg.get('assistant_message', '')
                
                stats['total_characters'] += len(user_msg) + len(assistant_msg)
                
                # Count intent types
                intent = msg.get('intent')
                if intent and isinstance(intent, dict):
                    intent_type = intent.get('type', 'unknown')
                    stats['message_types'][intent_type] = stats['message_types'].get(intent_type, 0) + 1
            
            return stats
            
        except Exception as e:
            print(f"Failed to get conversation stats: {e}")
            return None
    
    def show_help_and_stats(self):
        """Show help message with conversation statistics"""
        # Send regular help message
        self.send_quick_message("Help")
        
        # Add conversation statistics
        stats = self.get_conversation_stats()
        if stats:
            stats_msg = f"""📊 **Conversation Statistics:**

• Total messages: {stats['total_messages']}
• Total characters: {stats['total_characters']:,}
• Message types: {', '.join([f"{k}: {v}" for k, v in stats['message_types'].items()])}

💾 Use '📤 Export' to save your conversation history to JSON."""
            
            self.add_message(stats_msg, False)
        else:
            self.add_message("📊 No conversation statistics available yet.", False)
    
    def toggle_safe_mode(self):
        """Toggle demo safe mode"""
        global DEMO_SAFE_MODE
        DEMO_SAFE_MODE = not DEMO_SAFE_MODE
        
        # Save to settings
        if SETTINGS_AVAILABLE:
            set_setting('demo_safe_mode', DEMO_SAFE_MODE)
        
        # Update button appearance
        self.safe_mode_btn.setText("🔒 Safe Mode" if DEMO_SAFE_MODE else "🔓 Live Mode")
        self.safe_mode_btn.setStyleSheet(f"""
            QPushButton {{
                background: {'#8B0000' if DEMO_SAFE_MODE else '#4CAF50'};
                color: white;
                border: 1px solid {'#A52A2A' if DEMO_SAFE_MODE else '#45a049'};
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: {'#A52A2A' if DEMO_SAFE_MODE else '#45a049'};
            }}
        """)
        
        # Update banner visibility
        if hasattr(self, 'safe_mode_banner'):
            if DEMO_SAFE_MODE:
                self.safe_mode_banner.show()
            else:
                self.safe_mode_banner.hide()
        
        # Add status message
        if DEMO_SAFE_MODE:
            self.add_message("🔒 **Demo Safe Mode Enabled:** Automation execution is now disabled for safety.", False)
        else:
            self.add_message("🔓 **Live Mode Enabled:** ⚠️ Real automation execution is now possible. Use with caution!", False)
    
    def show_settings(self):
        """Show settings dialog"""
        if SETTINGS_AVAILABLE:
            dialog_result = show_settings_dialog(self)
            if dialog_result:
                # Reload settings after dialog closes
                self.load_settings_from_db()
                self.apply_settings()
                self.add_message("⚙️ Settings updated successfully!", False)
        else:
            self.add_message("❌ Settings system not available", False)
    
    def apply_settings(self):
        """Apply loaded settings to UI"""
        # Update checkboxes
        self.simulation_checkbox.setChecked(self.simulation_mode)
        self.voice_output_checkbox.setChecked(self.voice_output_enabled)
        
        # Update AI worker
        if self.ai_worker:
            self.ai_worker.set_simulation_mode(self.simulation_mode)
        
        # Update safe mode
        global DEMO_SAFE_MODE
        DEMO_SAFE_MODE = get_setting('demo_safe_mode', True)
        
        # Update safe mode button
        self.safe_mode_btn.setText("🔒 Safe Mode" if DEMO_SAFE_MODE else "🔓 Live Mode")
        self.safe_mode_btn.setStyleSheet(f"""
            QPushButton {{
                background: {'#8B0000' if DEMO_SAFE_MODE else '#4CAF50'};
                color: white;
                border: 1px solid {'#A52A2A' if DEMO_SAFE_MODE else '#45a049'};
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: {'#A52A2A' if DEMO_SAFE_MODE else '#45a049'};
            }}
        """)
        
        # Update banner
        if hasattr(self, 'safe_mode_banner'):
            if DEMO_SAFE_MODE:
                self.safe_mode_banner.show()
            else:
                self.safe_mode_banner.hide()
        
        # Update window size if needed
        window_width = get_setting('window_width', 1000)
        window_height = get_setting('window_height', 800)
        if self.width() != window_width or self.height() != window_height:
            self.resize(window_width, window_height)
    
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
        
        # Store current user message for later saving with AI response
        self.current_user_message = text
        
        # Send to AI with current simulation mode
        if self.ai_worker:
            simulate = self.simulation_checkbox.isChecked()
            self.ai_worker.add_message(text, simulate)
    
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
    
    def handle_ai_response(self, result):
        """Handle AI response with full result information"""
        reply = result.get('reply', 'No response')
        intent = result.get('intent', {})
        executed = result.get('executed', False)
        execution_result = result.get('execution_result')
        execution_plan = result.get('execution_plan')
        
        # Add main response
        self.add_message(reply, False)
        
        # Handle automation intents with action buttons
        if intent.get('type') == 'automation' and execution_plan:
            if executed:
                self.add_message(f"✅ **Action Executed:** {execution_result}", False)
            else:
                # Add automation plan with action buttons
                self.add_automation_message(intent, execution_plan)
        
        # Add intent information for debugging
        if intent.get('type') not in ['error', 'chat', 'help']:
            intent_info = f"🧠 **Intent:** {intent.get('type', 'unknown')} - {intent.get('action', 'no action')}"
            if intent.get('confidence'):
                intent_info += f" (confidence: {intent.get('confidence'):.1f})"
            self.add_message(intent_info, False)
        
        # Save conversation to database
        if DATABASE_AVAILABLE and hasattr(self, 'current_user_message'):
            try:
                save_message(self.current_user_message, reply, intent)
            except Exception as e:
                print(f"Failed to save conversation: {e}")
        
        # Speak the reply if voice output is enabled
        if self.voice_output_enabled and VOICE_AVAILABLE:
            self.speak_text(reply)
    
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
        
        # Update button states
        if status == "Processing...":
            self.send_btn.setEnabled(False)
            self.send_btn.setText("...")
        else:
            self.send_btn.setEnabled(True)
            self.send_btn.setText("Send")
    
    def add_automation_message(self, intent, execution_plan):
        """Add automation message with simulate/execute buttons"""
        # Create the automation plan display
        plan_html = f'''
        <div style="background: #2a2a2a; border-radius: 8px; padding: 15px; margin: 10px 0;">
            <div style="color: #d4af37; font-weight: bold; margin-bottom: 10px;">
                🤖 Automation Plan
            </div>
            <div style="color: white; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4; white-space: pre-wrap; background: #1a1a1a; padding: 10px; border-radius: 5px;">
{execution_plan.replace('<', '&lt;').replace('>', '&gt;')}
            </div>
        </div>
        '''
        
        # Create action buttons
        buttons_html = '''
        <div style="margin: 10px 0;">
        '''
        
        # Simulate button (always available)
        buttons_html += '''
            <button onclick="simulateAction()" style="background: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 5px; margin-right: 10px; cursor: pointer; font-weight: bold;">
                🎭 SIMULATE
            </button>
        '''
        
        # Execute button (only if not in demo safe mode)
        if not DEMO_SAFE_MODE:
            buttons_html += '''
                <button onclick="executeAction()" style="background: #FF6B6B; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                    ⚡ EXECUTE
                </button>
            '''
        else:
            buttons_html += '''
                <button disabled style="background: #666; color: #999; border: none; padding: 8px 16px; border-radius: 5px; cursor: not-allowed; font-weight: bold;">
                    🔒 EXECUTE (DISABLED)
                </button>
            '''
        
        buttons_html += '</div>'
        
        # Complete formatted response
        formatted = f'''
        <div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #1a1a1a, #2a2a2a); border-radius: 15px; border-left: 4px solid #d4af37;">
            <b style="color: #d4af37; font-size: 16px;">🤖 Heimdall:</b><br>
            <span style="color: white; font-size: 14px; line-height: 1.6;">
                Ready to execute automation!
                {plan_html}
                {buttons_html}
            </span>
        </div>
        '''
        
        self.chat_area.append(formatted)
        
        # Auto-scroll to bottom
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Store intent for button actions
        self.current_automation_intent = intent
    
    def simulate_automation(self):
        """Simulate the automation (show steps without executing)"""
        if hasattr(self, 'current_automation_intent'):
            intent = self.current_automation_intent
            plan = render_plan(intent) if AUTOMATION_AVAILABLE else "Plan not available"
            
            simulation_msg = f"""🎭 **Simulation Complete**

The following steps would be executed:
{plan}

✅ Simulation successful - no actual actions performed on your system."""
            
            self.add_message(simulation_msg, False)
            
            # Log simulation
            if DATABASE_AVAILABLE:
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'intent': intent,
                    'action': 'simulation',
                    'user': 'user'
                }
                save_message(
                    f"SIMULATION: {intent.get('action', 'unknown')}",
                    json.dumps(log_data),
                    intent
                )
    
    def execute_automation(self):
        """Execute the automation with confirmation"""
        if DEMO_SAFE_MODE:
            self.add_message("🔒 **Execution Blocked:** Demo Safe Mode is enabled. Disable it to allow real automation.", False)
            return
        
        if not hasattr(self, 'current_automation_intent'):
            self.add_message("❌ **Error:** No automation intent available for execution.", False)
            return
        
        intent = self.current_automation_intent
        plan = render_plan(intent) if AUTOMATION_AVAILABLE else "Plan not available"
        
        # Show confirmation dialog
        dialog = ConfirmationDialog(intent, plan, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # User confirmed - execute the automation
            self.add_message("⚡ **Executing automation...** Please wait.", False)
            
            # Start execution worker
            self.execution_worker = ExecutionWorker(intent)
            self.execution_worker.execution_complete.connect(self.handle_execution_complete)
            self.execution_worker.execution_error.connect(self.handle_execution_error)
            self.execution_worker.start()
        else:
            self.add_message("🚫 **Execution Cancelled:** User cancelled the automation execution.", False)
    
    def handle_execution_complete(self, intent, result):
        """Handle successful automation execution"""
        success_msg = f"""✅ **Execution Complete**

Action: {intent.get('action', 'unknown')}
Result: {result}

The automation has been successfully executed on your system."""
        
        self.add_message(success_msg, False)
    
    def handle_execution_error(self, intent, error):
        """Handle automation execution error"""
        error_msg = f"""❌ **Execution Failed**

Action: {intent.get('action', 'unknown')}
Error: {error}

The automation could not be completed. Please check the error details above."""
        
        self.add_message(error_msg, False)
    
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
    app.setApplicationName("Heimdall AI Assistant - Real AI")
    
    # Create and show window
    window = HeimdallWindow()
    window.show()
    
    print("✅ Heimdall AI Assistant with Real AI started!")
    print("🎯 Features:")
    print("  • Real natural language understanding")
    print("  • Actual screen capture and OCR")
    print("  • Real automation (when simulation mode is off)")
    print("  • Persistent conversation history")
    print("🚀 Try: 'Read my screen', 'Click the blue button', 'Help'")
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())