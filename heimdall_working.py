#!/usr/bin/env python3
"""
Heimdall Working GUI - Guaranteed to work!
Tries PyQt6 -> PyQt5 -> Tkinter -> Command Line
Now with AI Backend Integration!
"""
import sys
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🏠 Starting Heimdall GUI...")
    
    # Try PyQt6 first
    try:
        print("🔍 Trying PyQt6...")
        return run_pyqt6()
    except Exception as e:
        print(f"❌ PyQt6 failed: {e}")
    
    # Try PyQt5
    try:
        print("🔍 Trying PyQt5...")
        return run_pyqt5()
    except Exception as e:
        print(f"❌ PyQt5 failed: {e}")
    
    # Try Tkinter
    try:
        print("🔍 Trying Tkinter...")
        return run_tkinter()
    except Exception as e:
        print(f"❌ Tkinter failed: {e}")
    
    # Fallback to CLI
    print("🔍 Using command line fallback...")
    return run_cli()

def run_pyqt6():
    """PyQt6 implementation with AI Backend Integration"""
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QLineEdit, QFrame
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    
    # Import AI Brain and components
    try:
        from ai.heimdall_brain import HeimdallBrain
        AI_AVAILABLE = True
        logger.info("✅ AI Backend imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import AI Backend: {e}")
        AI_AVAILABLE = False
        # Create dummy class for fallback
        class HeimdallBrain:
            async def initialize(self): return False
            async def process_message(self, text, **kwargs): return {'reply': 'AI not available'}
            async def record_voice_command(self): return "Voice not available"
            async def get_screen_content(self): return "Screen reading not available"

    class AIWorkerThread(QThread):
        """Background thread for AI processing to keep GUI responsive"""
        response_ready = pyqtSignal(dict)  # Emits the full AI response dict
        error_occurred = pyqtSignal(str)   # Emits error messages
        
        def __init__(self, ai_brain, message, parent=None):
            super().__init__(parent)
            self.ai_brain = ai_brain
            self.message = message
        
        def run(self):
            """Run AI processing in background thread with comprehensive error handling"""
            try:
                if not self.ai_brain:
                    self.error_occurred.emit("AI brain not available")
                    return
                
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Process the message using the real AI backend
                result = loop.run_until_complete(
                    self.ai_brain.process_message(self.message, simulate_actions=True)
                )
                
                # Emit the result
                self.response_ready.emit(result)
                
            except ImportError as e:
                logger.error(f"AI import error: {e}")
                self.error_occurred.emit(f"AI dependencies missing: {str(e)}")
            except ConnectionError as e:
                logger.error(f"AI connection error: {e}")
                self.error_occurred.emit(f"AI service connection failed: {str(e)}")
            except TimeoutError as e:
                logger.error(f"AI timeout error: {e}")
                self.error_occurred.emit(f"AI response timeout: {str(e)}")
            except Exception as e:
                logger.error(f"AI processing error: {e}")
                self.error_occurred.emit(f"AI processing failed: {str(e)}")
            finally:
                # Clean up the event loop
                try:
                    loop.close()
                except:
                    pass

    class VoiceWorkerThread(QThread):
        """Background thread for voice recording"""
        voice_result = pyqtSignal(str)     # Emits transcribed text
        error_occurred = pyqtSignal(str)   # Emits error messages
        
        def __init__(self, voice_handler, parent=None):
            super().__init__(parent)
            self.voice_handler = voice_handler
        
        def run(self):
            """Record and transcribe voice in background with comprehensive error handling"""
            try:
                if not self.voice_handler:
                    self.error_occurred.emit("Voice handler not available")
                    return
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Record voice command using real voice handler
                text = loop.run_until_complete(
                    self.voice_handler.listen_for_command(duration=5)
                )
                
                if text and not text.startswith("❌"):
                    self.voice_result.emit(text.strip())
                else:
                    self.error_occurred.emit(text or "Voice recording failed")
                    
            except ImportError as e:
                logger.error(f"Voice import error: {e}")
                self.error_occurred.emit(f"Voice dependencies missing: {str(e)}")
            except OSError as e:
                logger.error(f"Voice hardware error: {e}")
                self.error_occurred.emit(f"Microphone access failed: {str(e)}")
            except Exception as e:
                logger.error(f"Voice recording error: {e}")
                self.error_occurred.emit(f"Voice recording failed: {str(e)}")
            finally:
                try:
                    loop.close()
                except:
                    pass

    class ScreenReaderThread(QThread):
        """Background thread for screen reading"""
        screen_result = pyqtSignal(str)    # Emits screen content
        error_occurred = pyqtSignal(str)   # Emits error messages
        
        def __init__(self, screen_analyzer, parent=None):
            super().__init__(parent)
            self.screen_analyzer = screen_analyzer
        
        def run(self):
            """Capture and analyze screen in background with comprehensive error handling"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Use the real screen analyzer function
                from core.screen_analyzer import capture_fullscreen_and_ocr
                content = capture_fullscreen_and_ocr()
                
                self.screen_result.emit(content)
                
            except ImportError as e:
                logger.error(f"Screen analyzer import error: {e}")
                self.error_occurred.emit(f"OCR dependencies missing: {str(e)}")
            except PermissionError as e:
                logger.error(f"Screen capture permission error: {e}")
                self.error_occurred.emit(f"Screen capture permission denied: {str(e)}")
            except Exception as e:
                logger.error(f"Screen reading error: {e}")
                self.error_occurred.emit(f"Screen reading failed: {str(e)}")
            finally:
                try:
                    loop.close()
                except:
                    pass

    class CommandExecutorThread(QThread):
        """Background thread for command execution"""
        execution_result = pyqtSignal(str)  # Emits execution result
        error_occurred = pyqtSignal(str)    # Emits error messages
        
        def __init__(self, screen_controller, command, parent=None):
            super().__init__(parent)
            self.screen_controller = screen_controller
            self.command = command
        
        def run(self):
            """Execute screen command in background with comprehensive error handling"""
            try:
                # Use the real screen controller functions
                from core.screen_controller import execute_intent, render_plan
                
                # For now, simulate actions by showing the plan
                if isinstance(self.command, dict):
                    # Command is an intent dictionary
                    plan = render_plan(self.command)
                    result = f"🎯 **Action Plan:**\n{plan}\n\n⚠️ *Simulation mode - action not executed*\n\n💡 *To enable real automation, uncomment pyautogui calls in screen_controller.py*"
                else:
                    result = f"📋 Command received: {self.command}\n⚠️ *Simulation mode active*"
                
                self.execution_result.emit(result)
                
            except ImportError as e:
                logger.error(f"Screen controller import error: {e}")
                self.error_occurred.emit(f"Screen control dependencies missing: {str(e)}")
            except PermissionError as e:
                logger.error(f"Screen control permission error: {e}")
                self.error_occurred.emit(f"Screen control permission denied: {str(e)}")
            except Exception as e:
                logger.error(f"Command execution error: {e}")
                self.error_occurred.emit(f"Command execution failed: {str(e)}")
            finally:
                pass
    
    class HeimdallWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Heimdall AI Assistant")
            self.setGeometry(100, 100, 900, 700)
            
            # Initialize AI components
            self.ai_brain = None
            self.voice_handler = None
            self.screen_analyzer = None
            self.screen_controller = None
            self.database = None
            self.ai_initialized = False
            
            # Worker threads
            self.current_ai_worker = None
            self.current_voice_worker = None
            self.current_screen_worker = None
            self.current_command_worker = None
            
            # UI state
            self.current_view = "chat"  # chat, voice, screen, settings
            
            self.setup_ui()
            self.initialize_ai_components()
        
        def setup_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            
            # Main layout
            main_layout = QHBoxLayout(central)
            main_layout.setContentsMargins(0, 0, 0, 0)
            
            # Sidebar
            sidebar = QFrame()
            sidebar.setFixedWidth(250)
            sidebar.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1a1a1a, stop:1 #2a2a2a);
                    border-right: 1px solid #444;
                }
            """)
            
            sidebar_layout = QVBoxLayout(sidebar)
            sidebar_layout.setContentsMargins(20, 30, 20, 20)
            
            # Logo
            logo = QLabel("👁 Heimdall")
            logo.setStyleSheet("""
                QLabel {
                    color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #d4af37, stop:1 #8b5cf6);
                    font-size: 24px;
                    font-weight: bold;
                    padding: 10px;
                }
            """)
            sidebar_layout.addWidget(logo)
            
            # Navigation buttons
            nav_buttons = ["💬 Chat", "🎤 Voice", "🖥️ Screen", "⚙️ Settings"]
            self.nav_buttons = []
            
            for i, text in enumerate(nav_buttons):
                btn = QPushButton(text)
                btn.setObjectName(f"nav_btn_{i}")
                btn.clicked.connect(lambda checked, idx=i: self.switch_view(idx))
                
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #d4af37)' if i == 0 else 'transparent'};
                        color: {'white' if i == 0 else '#b0b0b0'};
                        border: none;
                        border-radius: 8px;
                        padding: 12px 16px;
                        text-align: left;
                        font-size: 14px;
                        font-weight: {'bold' if i == 0 else 'normal'};
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(139, 92, 246, 0.3), stop:1 rgba(212, 175, 55, 0.3));
                        color: white;
                    }}
                """)
                self.nav_buttons.append(btn)
                sidebar_layout.addWidget(btn)
            
            sidebar_layout.addStretch()
            
            # Status
            status = QLabel("🟢 Connected")
            status.setStyleSheet("color: #10b981; font-size: 12px; padding: 10px;")
            sidebar_layout.addWidget(status)
            
            main_layout.addWidget(sidebar)
            
            # Main content
            content = QFrame()
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(0, 0, 0, 0)
            
            # Header
            header = QFrame()
            header.setFixedHeight(80)
            header.setStyleSheet("""
                QFrame {
                    background: rgba(20, 20, 20, 0.8);
                    border-bottom: 1px solid #444;
                }
            """)
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(30, 0, 30, 0)
            
            title = QLabel("Chat with Heimdall")
            title.setStyleSheet("""
                QLabel {
                    color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #d4af37, stop:1 #8b5cf6);
                    font-size: 20px;
                    font-weight: bold;
                }
            """)
            header_layout.addWidget(title)
            
            header_layout.addStretch()
            
            # Action buttons container
            buttons_container = QFrame()
            buttons_layout = QHBoxLayout(buttons_container)
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            buttons_layout.setSpacing(10)
            
            # Voice button
            self.voice_btn = QPushButton("🎤")
            self.voice_btn.setFixedSize(40, 40)
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    background: #2a2a2a;
                    color: #d4af37;
                    border: 2px solid #444;
                    border-radius: 20px;
                    font-size: 16px;
                }
                QPushButton:hover { 
                    background: #8b5cf6; 
                    color: white;
                    border-color: #8b5cf6;
                }
                QPushButton:pressed { background: #7c3aed; }
                QPushButton:disabled { 
                    background: #1a1a1a; 
                    color: #666; 
                    border-color: #333; 
                }
            """)
            self.voice_btn.clicked.connect(self.start_voice_recording)
            self.voice_btn.setToolTip("Click to record voice command")
            buttons_layout.addWidget(self.voice_btn)
            
            # Screen reading button
            self.screen_btn = QPushButton("📸")
            self.screen_btn.setFixedSize(40, 40)
            self.screen_btn.setStyleSheet("""
                QPushButton {
                    background: #2a2a2a;
                    color: #d4af37;
                    border: 2px solid #444;
                    border-radius: 20px;
                    font-size: 16px;
                }
                QPushButton:hover { 
                    background: #d4af37; 
                    color: black;
                    border-color: #d4af37;
                }
                QPushButton:pressed { background: #b8860b; }
                QPushButton:disabled { 
                    background: #1a1a1a; 
                    color: #666; 
                    border-color: #333; 
                }
            """)
            self.screen_btn.clicked.connect(self.read_screen)
            self.screen_btn.setToolTip("Click to read screen content")
            buttons_layout.addWidget(self.screen_btn)
            
            header_layout.addWidget(buttons_container)
            
            # Close button
            close_btn = QPushButton("×")
            close_btn.setFixedSize(30, 30)
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #444;
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-size: 16px;
                }
                QPushButton:hover { background: #e74c3c; }
            """)
            close_btn.clicked.connect(self.close)
            header_layout.addWidget(close_btn)
            
            content_layout.addWidget(header)
            
            # Main content stack
            from PyQt6.QtWidgets import QStackedWidget
            self.content_stack = QStackedWidget()
            
            # Chat view
            self.chat_widget = self.create_chat_view()
            self.content_stack.addWidget(self.chat_widget)
            
            # Voice view
            self.voice_widget = self.create_voice_view()
            self.content_stack.addWidget(self.voice_widget)
            
            # Screen view
            self.screen_widget = self.create_screen_view()
            self.content_stack.addWidget(self.screen_widget)
            
            # Settings view
            self.settings_widget = self.create_settings_view()
            self.content_stack.addWidget(self.settings_widget)
            
            content_layout.addWidget(self.content_stack)
            
            # Input area
            input_frame = QFrame()
            input_frame.setFixedHeight(80)
            input_frame.setStyleSheet("""
                QFrame {
                    background: rgba(20, 20, 20, 0.8);
                    border-top: 1px solid #444;
                }
            """)
            
            input_layout = QHBoxLayout(input_frame)
            input_layout.setContentsMargins(30, 15, 30, 15)
            
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText("Type your message or command...")
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
            
            send_btn = QPushButton("Send")
            send_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #8b5cf6, stop:1 #d4af37);
                    color: white;
                    border: none;
                    border-radius: 20px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #7c3aed, stop:1 #b8860b);
                }
            """)
            send_btn.clicked.connect(self.send_message)
            
            input_layout.addWidget(self.input_field)
            input_layout.addWidget(send_btn)
            
            content_layout.addWidget(input_frame)
            main_layout.addWidget(content)
            
            # Apply main window style
            self.setStyleSheet("""
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0a0a0a, stop:0.5 #1a1a1a, stop:1 #0a0a0a);
                }
            """)
        
        def create_chat_view(self):
            """Create the chat interface"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Chat area
            self.chat = QTextEdit()
            self.chat.setStyleSheet("""
                QTextEdit {
                    background: #0a0a0a;
                    color: white;
                    border: none;
                    font-size: 14px;
                    padding: 20px;
                }
            """)
            
            # Welcome message - will be updated after AI initialization
            self.welcome_html = """
            <div style='color: #d4af37; font-weight: bold; font-size: 18px; margin-bottom: 15px;'>
                🎉 Welcome to Heimdall AI Assistant!
            </div>
            <div style='color: white; margin-bottom: 10px;'>
                I'm your AI companion for screen navigation and control.
            </div>
            <div style='color: #b0b0b0; margin-bottom: 15px;'>
                ✨ Features available:
            </div>
            <div style='color: #8b5cf6; margin-left: 20px; margin-bottom: 15px;'>
                • 👁️ Read screen content (📸 button)<br>
                • 🖱️ Click buttons and elements<br>
                • ⬇️ Scroll and navigate<br>
                • ⌨️ Type text commands<br>
                • 🎤 Voice control support (🎤 button)
            </div>
            <div style='color: #d4af37; margin-bottom: 20px;'>
                Try typing: "Read what's on my screen" or "Click the blue button"
            </div>
            <div style='color: #f59e0b; margin-bottom: 20px;'>
                🔄 Initializing AI components...
            </div>
            <hr style='border: 1px solid #333; margin: 20px 0;'>
            """
            self.chat.setHtml(self.welcome_html)
            layout.addWidget(self.chat)
            
            return widget
        
        def create_voice_view(self):
            """Create the voice interface"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Voice status
            self.voice_status = QLabel("🎤 Voice Control Ready")
            self.voice_status.setStyleSheet("""
                QLabel {
                    color: #d4af37;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 20px;
                    text-align: center;
                }
            """)
            layout.addWidget(self.voice_status)
            
            # Voice instructions
            instructions = QLabel("""
            <div style='color: white; text-align: center; line-height: 1.6;'>
                <p>Click the microphone button to start voice recording</p>
                <p style='color: #8b5cf6;'>Try saying:</p>
                <ul style='color: #b0b0b0; text-align: left; max-width: 400px; margin: 0 auto;'>
                    <li>"Read what's on my screen"</li>
                    <li>"Click the blue button"</li>
                    <li>"Scroll down"</li>
                    <li>"Type hello world"</li>
                </ul>
            </div>
            """)
            instructions.setWordWrap(True)
            layout.addWidget(instructions)
            
            layout.addStretch()
            return widget
        
        def create_screen_view(self):
            """Create the screen analysis interface"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Screen status
            self.screen_status = QLabel("📸 Screen Analysis Ready")
            self.screen_status.setStyleSheet("""
                QLabel {
                    color: #d4af37;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 20px;
                    text-align: center;
                }
            """)
            layout.addWidget(self.screen_status)
            
            # Screen content display
            self.screen_content = QTextEdit()
            self.screen_content.setStyleSheet("""
                QTextEdit {
                    background: #1a1a1a;
                    color: white;
                    border: 1px solid #444;
                    border-radius: 8px;
                    padding: 15px;
                    font-family: monospace;
                    font-size: 12px;
                }
            """)
            self.screen_content.setPlaceholderText("Screen content will appear here after clicking the 📸 button...")
            layout.addWidget(self.screen_content)
            
            return widget
        
        def create_settings_view(self):
            """Create the settings interface"""
            from PyQt6.QtWidgets import QScrollArea, QFormLayout, QComboBox, QSlider, QCheckBox, QSpinBox
            
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Settings title
            title = QLabel("⚙️ Settings")
            title.setStyleSheet("""
                QLabel {
                    color: #d4af37;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 20px 0;
                }
            """)
            layout.addWidget(title)
            
            # Scrollable settings area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
                QScrollArea {
                    background: transparent;
                    border: none;
                }
                QScrollBar:vertical {
                    background: #2a2a2a;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background: #8b5cf6;
                    border-radius: 6px;
                    min-height: 20px;
                }
            """)
            
            settings_content = QWidget()
            settings_layout = QFormLayout(settings_content)
            settings_layout.setSpacing(15)
            
            # Voice Settings
            voice_group = QLabel("🎤 Voice Settings")
            voice_group.setStyleSheet("color: #8b5cf6; font-weight: bold; font-size: 14px; margin-top: 10px;")
            settings_layout.addRow(voice_group)
            
            # Voice volume
            self.voice_volume_slider = QSlider(Qt.Orientation.Horizontal)
            self.voice_volume_slider.setRange(0, 100)
            self.voice_volume_slider.setValue(90)
            self.voice_volume_slider.valueChanged.connect(self.update_voice_volume)
            settings_layout.addRow("Voice Volume:", self.voice_volume_slider)
            
            # Voice rate
            self.voice_rate_slider = QSlider(Qt.Orientation.Horizontal)
            self.voice_rate_slider.setRange(50, 300)
            self.voice_rate_slider.setValue(200)
            self.voice_rate_slider.valueChanged.connect(self.update_voice_rate)
            settings_layout.addRow("Voice Rate (WPM):", self.voice_rate_slider)
            
            # Voice selection
            self.voice_combo = QComboBox()
            self.voice_combo.addItems(["Default", "Voice 1", "Voice 2", "Voice 3"])
            self.voice_combo.currentTextChanged.connect(self.update_voice_selection)
            settings_layout.addRow("Voice:", self.voice_combo)
            
            # AI Settings
            ai_group = QLabel("🧠 AI Settings")
            ai_group.setStyleSheet("color: #8b5cf6; font-weight: bold; font-size: 14px; margin-top: 20px;")
            settings_layout.addRow(ai_group)
            
            # AI model
            self.ai_model_combo = QComboBox()
            self.ai_model_combo.addItems(["llama3.2:1b", "llama3.2:3b", "llama3.2:7b"])
            self.ai_model_combo.setCurrentText("llama3.2:3b")
            self.ai_model_combo.currentTextChanged.connect(self.update_ai_model)
            settings_layout.addRow("AI Model:", self.ai_model_combo)
            
            # OCR Settings
            ocr_group = QLabel("📸 OCR Settings")
            ocr_group.setStyleSheet("color: #8b5cf6; font-weight: bold; font-size: 14px; margin-top: 20px;")
            settings_layout.addRow(ocr_group)
            
            # OCR language
            self.ocr_language_combo = QComboBox()
            self.ocr_language_combo.addItems(["English", "Spanish", "French", "German", "Chinese", "Japanese"])
            self.ocr_language_combo.currentTextChanged.connect(self.update_ocr_language)
            settings_layout.addRow("OCR Language:", self.ocr_language_combo)
            
            # OCR confidence threshold
            self.ocr_confidence_slider = QSlider(Qt.Orientation.Horizontal)
            self.ocr_confidence_slider.setRange(50, 95)
            self.ocr_confidence_slider.setValue(70)
            self.ocr_confidence_slider.valueChanged.connect(self.update_ocr_confidence)
            settings_layout.addRow("OCR Confidence:", self.ocr_confidence_slider)
            
            # UI Settings
            ui_group = QLabel("🎨 Interface Settings")
            ui_group.setStyleSheet("color: #8b5cf6; font-weight: bold; font-size: 14px; margin-top: 20px;")
            settings_layout.addRow(ui_group)
            
            # Theme
            self.theme_combo = QComboBox()
            self.theme_combo.addItems(["Dark (Default)", "Light", "High Contrast"])
            self.theme_combo.currentTextChanged.connect(self.update_theme)
            settings_layout.addRow("Theme:", self.theme_combo)
            
            # Auto-scroll chat
            self.auto_scroll_check = QCheckBox()
            self.auto_scroll_check.setChecked(True)
            self.auto_scroll_check.toggled.connect(self.update_auto_scroll)
            settings_layout.addRow("Auto-scroll Chat:", self.auto_scroll_check)
            
            # Apply common styling to form elements
            for i in range(settings_layout.rowCount()):
                item = settings_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
                if item and item.widget():
                    widget_item = item.widget()
                    if isinstance(widget_item, (QComboBox, QSlider, QCheckBox, QSpinBox)):
                        widget_item.setStyleSheet("""
                            QComboBox, QSlider, QCheckBox, QSpinBox {
                                background: #2a2a2a;
                                color: white;
                                border: 1px solid #444;
                                border-radius: 4px;
                                padding: 5px;
                            }
                            QComboBox::drop-down {
                                border: none;
                                background: #8b5cf6;
                            }
                            QComboBox::down-arrow {
                                image: none;
                                border: none;
                            }
                            QSlider::groove:horizontal {
                                background: #444;
                                height: 6px;
                                border-radius: 3px;
                            }
                            QSlider::handle:horizontal {
                                background: #8b5cf6;
                                width: 16px;
                                height: 16px;
                                border-radius: 8px;
                                margin: -5px 0;
                            }
                            QCheckBox::indicator {
                                width: 16px;
                                height: 16px;
                                border: 1px solid #444;
                                border-radius: 3px;
                                background: #2a2a2a;
                            }
                            QCheckBox::indicator:checked {
                                background: #8b5cf6;
                            }
                        """)
            
            scroll.setWidget(settings_content)
            layout.addWidget(scroll)
            
            return widget
        
        def switch_view(self, index):
            """Switch between different views"""
            self.current_view = ["chat", "voice", "screen", "settings"][index]
            self.content_stack.setCurrentIndex(index)
            
            # Update navigation button styles
            for i, btn in enumerate(self.nav_buttons):
                if i == index:
                    btn.setStyleSheet("""
                        QPushButton {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #d4af37);
                            color: white;
                            border: none;
                            border-radius: 8px;
                            padding: 12px 16px;
                            text-align: left;
                            font-size: 14px;
                            font-weight: bold;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background: transparent;
                            color: #b0b0b0;
                            border: none;
                            border-radius: 8px;
                            padding: 12px 16px;
                            text-align: left;
                            font-size: 14px;
                            font-weight: normal;
                        }
                        QPushButton:hover {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 rgba(139, 92, 246, 0.3), stop:1 rgba(212, 175, 55, 0.3));
                            color: white;
                        }
                    """)
        
        def initialize_ai_components(self):
            """Initialize all AI components with comprehensive error handling"""
            if not AI_AVAILABLE:
                self.show_error_bubble("AI components not available. Please check installation.")
                self.update_status_message("❌ AI components not available. Please check installation.", "#ef4444")
                return
            
            try:
                # Initialize AI Brain
                self.ai_brain = HeimdallBrain()
                
                # Initialize other AI components with error handling
                self.initialize_voice_handler()
                self.initialize_screen_analyzer()
                self.initialize_screen_controller()
                
                # Use QTimer to initialize AI brain asynchronously
                self.init_timer = QTimer()
                self.init_timer.timeout.connect(self.complete_ai_initialization)
                self.init_timer.setSingleShot(True)
                self.init_timer.start(100)  # Start after 100ms
                
            except Exception as e:
                logger.error(f"Failed to initialize AI components: {e}")
                self.show_error_bubble(f"AI initialization failed: {str(e)}")
                self.update_status_message(f"❌ AI initialization failed: {str(e)}", "#ef4444")
        
        def initialize_voice_handler(self):
            """Initialize voice handler with error handling"""
            try:
                from core.voice_handler import VoiceHandler
                self.voice_handler = VoiceHandler()
                # Initialize the voice handler asynchronously
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.voice_handler.initialize())
                loop.close()
                logger.info("✅ Voice handler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize voice handler: {e}")
                self.voice_handler = None
                self.show_error_bubble(f"Voice handler initialization failed: {str(e)}")
        
        def initialize_screen_analyzer(self):
            """Initialize screen analyzer with error handling"""
            try:
                from core.screen_analyzer import ScreenAnalyzer
                self.screen_analyzer = ScreenAnalyzer()
                logger.info("✅ Screen analyzer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize screen analyzer: {e}")
                self.screen_analyzer = None
                self.show_error_bubble(f"Screen analyzer initialization failed: {str(e)}")
        
        def initialize_screen_controller(self):
            """Initialize screen controller with error handling"""
            try:
                from core.screen_controller import execute_screen_command
                self.screen_controller = execute_screen_command
                logger.info("✅ Screen controller initialized")
            except Exception as e:
                logger.error(f"Failed to initialize screen controller: {e}")
                self.screen_controller = None
                self.show_error_bubble(f"Screen controller initialization failed: {str(e)}")

        def initialize_ai_brain(self):
            """Initialize AI brain in background"""
            if not AI_AVAILABLE:
                self.update_status_message("❌ AI components not available. Please check installation.", "#ef4444")
                return
            
            try:
                self.ai_brain = HeimdallBrain()
                
                # Use QTimer to initialize AI brain asynchronously
                self.init_timer = QTimer()
                self.init_timer.timeout.connect(self.complete_ai_initialization)
                self.init_timer.setSingleShot(True)
                self.init_timer.start(100)  # Start after 100ms
                
            except Exception as e:
                logger.error(f"Failed to create AI brain: {e}")
                self.show_error_bubble(f"AI brain creation failed: {str(e)}")
                self.update_status_message(f"❌ AI initialization failed: {str(e)}", "#ef4444")
        
        def complete_ai_initialization(self):
            """Complete AI initialization with comprehensive error handling"""
            try:
                # Create event loop for initialization
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Initialize AI brain
                success = loop.run_until_complete(self.ai_brain.initialize())
                
                if success:
                    self.ai_initialized = True
                    self.update_status_message("✅ AI system ready!", "#10b981")
                    logger.info("✅ AI Brain initialized successfully")
                else:
                    self.show_error_bubble("AI brain initialization failed - check AI model availability")
                    self.update_status_message("❌ AI initialization failed", "#ef4444")
                    logger.error("❌ AI Brain initialization failed")
                
            except ImportError as e:
                logger.error(f"AI import error: {e}")
                self.show_error_bubble(f"AI dependencies missing: {str(e)}")
                self.update_status_message(f"❌ AI import error: {str(e)}", "#ef4444")
            except ConnectionError as e:
                logger.error(f"AI connection error: {e}")
                self.show_error_bubble(f"AI service connection failed: {str(e)}")
                self.update_status_message(f"❌ AI connection error: {str(e)}", "#ef4444")
            except Exception as e:
                logger.error(f"AI initialization error: {e}")
                self.show_error_bubble(f"AI initialization error: {str(e)}")
                self.update_status_message(f"❌ AI error: {str(e)}", "#ef4444")
            finally:
                try:
                    loop.close()
                except:
                    pass
        
        def update_status_message(self, message, color="#10b981"):
            """Update the status message in the welcome area"""
            updated_html = self.welcome_html.replace(
                "🔄 Initializing AI components...",
                f"<span style='color: {color};'>{message}</span>"
            )
            self.chat.setHtml(updated_html)
        
        def start_voice_recording(self):
            """Start voice recording with comprehensive error handling"""
            if not self.ai_initialized:
                self.show_error_bubble("AI system not ready. Please wait for initialization.")
                return
            
            if not self.voice_handler:
                self.show_error_bubble("Voice handler not available. Check microphone permissions.")
                return
            
            try:
                # Update button appearance
                self.voice_btn.setText("🔴")
                self.voice_btn.setStyleSheet("""
                    QPushButton {
                        background: #e74c3c;
                        color: white;
                        border: 2px solid #e74c3c;
                        border-radius: 20px;
                        font-size: 16px;
                    }
                """)
                self.voice_btn.setEnabled(False)
                
                # Add status message
                self.add_system_message("🎤 Listening... Speak your command now.")
                
                # Start voice worker
                if self.current_voice_worker and self.current_voice_worker.isRunning():
                    self.current_voice_worker.terminate()
                    self.current_voice_worker.wait()
                
                self.current_voice_worker = VoiceWorkerThread(self.voice_handler, self)
                self.current_voice_worker.voice_result.connect(self.handle_voice_result)
                self.current_voice_worker.error_occurred.connect(self.handle_voice_error)
                self.current_voice_worker.start()
                
            except Exception as e:
                logger.error(f"Failed to start voice recording: {e}")
                self.show_error_bubble(f"Voice recording failed to start: {str(e)}")
                self.reset_voice_button()
        
        def handle_voice_result(self, text):
            """Handle voice transcription result and send to AI"""
            # Reset voice button
            self.reset_voice_button()
            
            # Display transcribed text in chat
            voice_html = f"""
            <div style='text-align: left; margin: 15px 0;'>
                <div style='background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706); 
                           color: white; padding: 12px 16px; 
                           border-radius: 15px; border: 1px solid #f59e0b; 
                           display: inline-block; max-width: 70%; word-wrap: break-word;'>
                    🎤 <strong>Voice Input:</strong><br><br>
                    "{self.escape_html(text)}"
                </div>
                <div style='color: #666; font-size: 11px; margin-top: 5px;'>
                    Speech Recognition • Just now
                </div>
            </div>
            """
            self.chat.insertHtml(voice_html)
            self.scroll_to_bottom()
            
            # Set transcribed text in input field and send to AI
            self.input_field.setText(text)
            self.send_message()
        
        def handle_voice_error(self, error_msg):
            """Handle voice recording error"""
            self.reset_voice_button()
            self.show_error_bubble(f"Voice recording failed: {error_msg}")
            self.show_error_message(f"Voice recording failed: {error_msg}")
        
        def reset_voice_button(self):
            """Reset voice button to normal state"""
            self.voice_btn.setText("🎤")
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    background: #2a2a2a;
                    color: #d4af37;
                    border: 2px solid #444;
                    border-radius: 20px;
                    font-size: 16px;
                }
                QPushButton:hover { 
                    background: #8b5cf6; 
                    color: white;
                    border-color: #8b5cf6;
                }
                QPushButton:pressed { background: #7c3aed; }
            """)
            self.voice_btn.setEnabled(True)
        
        def read_screen(self):
            """Read current screen content with comprehensive error handling"""
            if not self.ai_initialized:
                self.show_error_bubble("AI system not ready. Please wait for initialization.")
                return
            
            if not self.screen_analyzer:
                self.show_error_bubble("Screen analyzer not available. Check OCR dependencies.")
                return
            
            try:
                # Update button appearance
                self.screen_btn.setEnabled(False)
                self.screen_btn.setText("📷")
                
                # Add status message
                self.add_system_message("📸 Capturing and analyzing screen...")
                
                # Start screen reader worker
                if self.current_screen_worker and self.current_screen_worker.isRunning():
                    self.current_screen_worker.terminate()
                    self.current_screen_worker.wait()
                
                self.current_screen_worker = ScreenReaderThread(self.screen_analyzer, self)
                self.current_screen_worker.screen_result.connect(self.handle_screen_result)
                self.current_screen_worker.error_occurred.connect(self.handle_screen_error)
                self.current_screen_worker.start()
                
            except Exception as e:
                logger.error(f"Failed to start screen reading: {e}")
                self.show_error_bubble(f"Screen reading failed to start: {str(e)}")
                self.reset_screen_button()
        
        def handle_screen_result(self, content):
            """Handle screen reading result with purple OCR bubble"""
            # Reset screen button
            self.reset_screen_button()
            
            # Display screen content in purple bubble
            if content and not content.startswith("❌"):
                # Truncate very long content
                if len(content) > 1000:
                    content = content[:1000] + "...\n\n(Content truncated for display)"
                
                # Purple bubble for OCR results
                screen_html = f"""
                <div style='text-align: left; margin: 15px 0;'>
                    <div style='background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #a855f7); 
                               color: white; padding: 12px 16px; 
                               border-radius: 15px; border: 1px solid #8b5cf6; 
                               display: inline-block; max-width: 70%; word-wrap: break-word;'>
                        📸 <strong>Screen OCR Result:</strong><br><br>
                        {self.escape_html(content)}
                    </div>
                    <div style='color: #666; font-size: 11px; margin-top: 5px;'>
                        OCR Scanner • Just now
                    </div>
                </div>
                """
                self.chat.insertHtml(screen_html)
                
                # Also update the screen view if we're on that tab
                if hasattr(self, 'screen_content'):
                    self.screen_content.setPlainText(content)
                    
            else:
                self.show_error_message(f"Screen reading failed: {content}")
            
            self.scroll_to_bottom()
        
        def handle_screen_error(self, error_msg):
            """Handle screen reading error"""
            self.reset_screen_button()
            self.show_error_bubble(f"Screen reading failed: {error_msg}")
            self.show_error_message(f"Screen reading failed: {error_msg}")
        
        def reset_screen_button(self):
            """Reset screen button to normal state"""
            self.screen_btn.setText("📸")
            self.screen_btn.setEnabled(True)
        
        def add_system_message(self, message):
            """Add system message to chat"""
            system_html = f"""
            <div style='text-align: center; margin: 10px 0;'>
                <div style='background: rgba(139, 92, 246, 0.1); color: #8b5cf6; padding: 8px 12px; 
                           border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3); 
                           display: inline-block; font-size: 12px;'>
                    {self.escape_html(message)}
                </div>
            </div>
            """
            self.chat.insertHtml(system_html)
            self.scroll_to_bottom()
        
        def update_voice_volume(self, value):
            """Update voice volume setting"""
            try:
                if hasattr(self, 'voice_handler') and self.voice_handler:
                    # Voice volume setting - placeholder for now
                    logger.info(f"Voice volume set to: {value}%")
            except Exception as e:
                logger.error(f"Failed to update voice volume: {e}")
                self.show_error_bubble(f"Failed to update voice volume: {str(e)}")
        
        def update_voice_rate(self, value):
            """Update voice rate setting"""
            try:
                if hasattr(self, 'voice_handler') and self.voice_handler:
                    # Voice rate setting - placeholder for now
                    logger.info(f"Voice rate set to: {value} WPM")
            except Exception as e:
                logger.error(f"Failed to update voice rate: {e}")
                self.show_error_bubble(f"Failed to update voice rate: {str(e)}")
        
        def update_voice_selection(self, voice_name):
            """Update voice selection setting"""
            try:
                if hasattr(self, 'voice_handler') and self.voice_handler:
                    # Voice selection setting - placeholder for now
                    logger.info(f"Voice selected: {voice_name}")
            except Exception as e:
                logger.error(f"Failed to update voice selection: {e}")
                self.show_error_bubble(f"Failed to update voice selection: {str(e)}")
        
        def update_ai_model(self, model_name):
            """Update AI model setting"""
            try:
                if hasattr(self, 'ai_brain') and self.ai_brain:
                    # AI model setting - placeholder for now
                    logger.info(f"AI model set to: {model_name}")
            except Exception as e:
                logger.error(f"Failed to update AI model: {e}")
                self.show_error_bubble(f"Failed to update AI model: {str(e)}")
        
        def update_ocr_language(self, language):
            """Update OCR language setting"""
            try:
                if hasattr(self, 'screen_analyzer') and self.screen_analyzer:
                    # OCR language setting - placeholder for now
                    logger.info(f"OCR language set to: {language}")
            except Exception as e:
                logger.error(f"Failed to update OCR language: {e}")
                self.show_error_bubble(f"Failed to update OCR language: {str(e)}")
        
        def update_ocr_confidence(self, value):
            """Update OCR confidence threshold setting"""
            try:
                if hasattr(self, 'screen_analyzer') and self.screen_analyzer:
                    # OCR confidence setting - placeholder for now
                    logger.info(f"OCR confidence set to: {value}%")
            except Exception as e:
                logger.error(f"Failed to update OCR confidence: {e}")
                self.show_error_bubble(f"Failed to update OCR confidence: {str(e)}")
        
        def update_theme(self, theme_name):
            """Update UI theme setting"""
            try:
                # Theme setting - placeholder for now
                logger.info(f"Theme set to: {theme_name}")
            except Exception as e:
                logger.error(f"Failed to update theme: {e}")
                self.show_error_bubble(f"Failed to update theme: {str(e)}")
        
        def update_auto_scroll(self, enabled):
            """Update auto-scroll chat setting"""
            try:
                # Auto-scroll setting - placeholder for now
                logger.info(f"Auto-scroll set to: {enabled}")
            except Exception as e:
                logger.error(f"Failed to update auto-scroll: {e}")
                self.show_error_bubble(f"Failed to update auto-scroll: {str(e)}")
        
        def closeEvent(self, event):
            """Handle window close event"""
            try:
                # Terminate any running workers
                if self.current_ai_worker and self.current_ai_worker.isRunning():
                    self.current_ai_worker.terminate()
                    self.current_ai_worker.wait()
                
                if self.current_voice_worker and self.current_voice_worker.isRunning():
                    self.current_voice_worker.terminate()
                    self.current_voice_worker.wait()
                
                if self.current_screen_worker and self.current_screen_worker.isRunning():
                    self.current_screen_worker.terminate()
                    self.current_screen_worker.wait()
                
                # Cleanup AI brain
                if self.ai_brain:
                    self.ai_brain.cleanup()
                
                logger.info("Application closed cleanly")
                
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            
            event.accept()
        
        def send_message(self):
            """Send user message and get AI response with comprehensive error handling"""
            text = self.input_field.text().strip()
            if not text:
                return
            
            # Check if AI is available
            if not AI_AVAILABLE or not self.ai_initialized:
                self.show_error_bubble("AI system not available. Please check the setup.")
                return
            
            if not self.ai_brain:
                self.show_error_bubble("AI brain not initialized. Please restart the application.")
                return
            
            try:
                # Disable input while processing
                self.input_field.setEnabled(False)
                self.input_field.setPlaceholderText("Processing...")
                
                # Display user message
                self.add_user_message(text)
                
                # Show processing indicator
                self.add_processing_message()
                
                # Clear input
                self.input_field.clear()
                
                # Start AI processing in background thread
                if self.current_ai_worker and self.current_ai_worker.isRunning():
                    self.current_ai_worker.terminate()
                    self.current_ai_worker.wait()
                
                self.current_ai_worker = AIWorkerThread(self.ai_brain, text, self)
                self.current_ai_worker.response_ready.connect(self.handle_ai_response)
                self.current_ai_worker.error_occurred.connect(self.handle_ai_error)
                self.current_ai_worker.start()
                
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                self.show_error_bubble(f"Message processing failed: {str(e)}")
                # Re-enable input
                self.input_field.setEnabled(True)
                self.input_field.setPlaceholderText("Type your message or command...")
                self.input_field.setFocus()
        
        def add_user_message(self, text):
            """Add user message to chat"""
            user_html = f"""
            <div style='text-align: right; margin: 15px 0;'>
                <div style='background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #d4af37); 
                           color: white; padding: 12px 16px; border-radius: 15px; 
                           display: inline-block; max-width: 70%; word-wrap: break-word;'>
                    {self.escape_html(text)}
                </div>
                <div style='color: #666; font-size: 11px; margin-top: 5px;'>
                    Just now
                </div>
            </div>
            """
            self.chat.insertHtml(user_html)
            self.scroll_to_bottom()
        
        def add_processing_message(self):
            """Add processing indicator"""
            processing_html = """
            <div id='processing-msg' style='text-align: left; margin: 15px 0;'>
                <div style='background: #2a2a2a; color: #f59e0b; padding: 12px 16px; 
                           border-radius: 15px; border: 1px solid #444; 
                           display: inline-block; max-width: 70%;'>
                    🤔 Thinking...
                </div>
            </div>
            """
            self.chat.insertHtml(processing_html)
            self.scroll_to_bottom()
        
        def handle_ai_response(self, result):
            """Handle AI response from worker thread with action execution"""
            try:
                # Remove processing message by replacing chat content
                current_html = self.chat.toHtml()
                # Remove the processing message
                import re
                current_html = re.sub(r"<div id='processing-msg'.*?</div>", "", current_html, flags=re.DOTALL)
                self.chat.setHtml(current_html)
                
                # Add AI response
                reply = result.get('reply', 'No response generated')
                intent = result.get('intent', {})
                executed = result.get('executed', False)
                
                # Format the response with intent information
                formatted_reply = self.format_ai_response(reply, intent, executed)
                
                ai_html = f"""
                <div style='text-align: left; margin: 15px 0;'>
                    <div style='background: #2a2a2a; color: white; padding: 12px 16px; 
                               border-radius: 15px; border: 1px solid #444; 
                               display: inline-block; max-width: 70%; word-wrap: break-word;'>
                        {formatted_reply}
                    </div>
                    <div style='color: #666; font-size: 11px; margin-top: 5px;'>
                        Heimdall • Just now
                    </div>
                </div>
                """
                self.chat.insertHtml(ai_html)
                
                # Check if AI response includes actions to execute
                if intent.get('type') == 'automation' and not executed:
                    self.execute_automation_action(intent)
                
                # Add TTS output for AI response
                self.speak_response(reply)
                
            except Exception as e:
                logger.error(f"Error handling AI response: {e}")
                self.show_error_message(f"Error displaying response: {str(e)}")
            
            finally:
                # Re-enable input
                self.input_field.setEnabled(True)
                self.input_field.setPlaceholderText("Type your message or command...")
                self.input_field.setFocus()
                self.scroll_to_bottom()
        
        def handle_ai_error(self, error_msg):
            """Handle AI processing errors"""
            # Remove processing message
            current_html = self.chat.toHtml()
            import re
            current_html = re.sub(r"<div id='processing-msg'.*?</div>", "", current_html, flags=re.DOTALL)
            self.chat.setHtml(current_html)
            
            # Show error bubble and message
            self.show_error_bubble(f"AI Error: {error_msg}")
            self.show_error_message(f"AI Error: {error_msg}")
            
            # Re-enable input
            self.input_field.setEnabled(True)
            self.input_field.setPlaceholderText("Type your message or command...")
            self.input_field.setFocus()
        
        def format_ai_response(self, reply, intent, executed):
            """Format AI response with proper HTML escaping and styling"""
            # Escape HTML in the reply
            escaped_reply = self.escape_html(reply)
            
            # Add intent information if available
            if intent.get('type') == 'automation':
                if executed:
                    escaped_reply += "<br><br><span style='color: #10b981;'>✅ Action executed</span>"
                else:
                    escaped_reply += "<br><br><span style='color: #f59e0b;'>⚠️ Simulation mode - action not executed</span>"
            
            return escaped_reply
        
        def escape_html(self, text):
            """Escape HTML characters and preserve line breaks"""
            import html
            escaped = html.escape(str(text))
            # Convert newlines to <br> tags
            escaped = escaped.replace('\n', '<br>')
            return escaped
        
        def show_error_message(self, error_text):
            """Display error message in chat"""
            error_html = f"""
            <div style='text-align: left; margin: 15px 0;'>
                <div style='background: rgba(239, 68, 68, 0.1); color: #ef4444; padding: 12px 16px; 
                           border-radius: 15px; border: 1px solid #ef4444; 
                           display: inline-block; max-width: 70%; word-wrap: break-word;'>
                    ⚠️ {self.escape_html(error_text)}
                </div>
                <div style='color: #666; font-size: 11px; margin-top: 5px;'>
                    System • Just now
                </div>
            </div>
            """
            self.chat.insertHtml(error_html)
            self.scroll_to_bottom()
        
        def show_error_bubble(self, error_text):
            """Show a red error bubble notification"""
            try:
                from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect
                from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
                
                # Create error bubble
                self.error_bubble = QLabel(self)
                self.error_bubble.setText(f"❌ {error_text}")
                self.error_bubble.setStyleSheet("""
                    QLabel {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #ef4444, stop:1 #dc2626);
                        color: white;
                        border: 2px solid #b91c1c;
                        border-radius: 12px;
                        padding: 12px 20px;
                        font-weight: bold;
                        font-size: 14px;
                        max-width: 400px;
                    }
                """)
                self.error_bubble.setWordWrap(True)
                self.error_bubble.adjustSize()
                
                # Position at top center
                bubble_width = self.error_bubble.width()
                x = (self.width() - bubble_width) // 2
                y = 20
                self.error_bubble.move(x, y)
                self.error_bubble.show()
                
                # Auto-hide after 5 seconds
                self.error_timer = QTimer()
                self.error_timer.timeout.connect(self.hide_error_bubble)
                self.error_timer.setSingleShot(True)
                self.error_timer.start(5000)
                
                logger.error(f"Error bubble shown: {error_text}")
                
            except Exception as e:
                logger.error(f"Failed to show error bubble: {e}")
                # Fallback to console
                print(f"ERROR: {error_text}")
        
        def hide_error_bubble(self):
            """Hide the error bubble"""
            try:
                if hasattr(self, 'error_bubble') and self.error_bubble:
                    self.error_bubble.hide()
                    self.error_bubble.deleteLater()
                    self.error_bubble = None
            except Exception as e:
                logger.error(f"Failed to hide error bubble: {e}")
        
        def execute_automation_action(self, intent):
            """Execute automation action from AI response"""
            try:
                if not intent or intent.get('type') != 'automation':
                    return
                
                # Start command executor worker
                if self.current_command_worker and self.current_command_worker.isRunning():
                    self.current_command_worker.terminate()
                    self.current_command_worker.wait()
                
                self.current_command_worker = CommandExecutorThread(None, intent, self)
                self.current_command_worker.execution_result.connect(self.handle_execution_result)
                self.current_command_worker.error_occurred.connect(self.handle_execution_error)
                self.current_command_worker.start()
                
            except Exception as e:
                logger.error(f"Failed to execute automation action: {e}")
                self.show_error_bubble(f"Automation execution failed: {str(e)}")
        
        def handle_execution_result(self, result):
            """Handle automation execution result"""
            try:
                # Show execution result in a green confirmation bubble
                execution_html = f"""
                <div style='text-align: left; margin: 15px 0;'>
                    <div style='background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669); 
                               color: white; padding: 12px 16px; 
                               border-radius: 15px; border: 1px solid #10b981; 
                               display: inline-block; max-width: 70%; word-wrap: break-word;'>
                        🤖 <strong>Automation Result:</strong><br><br>
                        {self.escape_html(result)}
                    </div>
                    <div style='color: #666; font-size: 11px; margin-top: 5px;'>
                        Automation Engine • Just now
                    </div>
                </div>
                """
                self.chat.insertHtml(execution_html)
                self.scroll_to_bottom()
                
            except Exception as e:
                logger.error(f"Error handling execution result: {e}")
        
        def handle_execution_error(self, error_msg):
            """Handle automation execution error"""
            self.show_error_bubble(f"Automation failed: {error_msg}")
            self.show_error_message(f"Automation execution failed: {error_msg}")
        
        def speak_response(self, text):
            """Speak AI response using TTS"""
            try:
                # Clean text for TTS (remove markdown and special characters)
                clean_text = self.clean_text_for_tts(text)
                
                if len(clean_text.strip()) > 0:
                    # Start TTS in background thread to avoid blocking GUI
                    import threading
                    tts_thread = threading.Thread(target=self._speak_text_sync, args=(clean_text,))
                    tts_thread.daemon = True
                    tts_thread.start()
                    
            except Exception as e:
                logger.error(f"TTS error: {e}")
        
        def _speak_text_sync(self, text):
            """Synchronous TTS function to run in background thread"""
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)  # Speed
                engine.setProperty('volume', 0.8)  # Volume
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS synthesis error: {e}")
        
        def clean_text_for_tts(self, text):
            """Clean text for TTS by removing markdown and special formatting"""
            import re
            
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
            text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
            text = re.sub(r'`(.*?)`', r'\1', text)        # Code
            text = re.sub(r'#{1,6}\s*(.*)', r'\1', text)  # Headers
            text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Links
            
            # Remove special symbols that don't read well
            text = re.sub(r'[📸🤖⚠️✅❌💡🎯📋]', '', text)
            
            # Clean up extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Limit length for TTS
            if len(text) > 200:
                text = text[:200] + "..."
            
            return text
        
        def scroll_to_bottom(self):
            """Scroll chat to bottom"""
            scrollbar = self.chat.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    app = QApplication(sys.argv)
    window = HeimdallWindow()
    window.show()
    print("✅ PyQt6 GUI started successfully!")
    return app.exec()

def run_pyqt5():
    """PyQt5 fallback"""
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QLineEdit
    )
    
    class SimpleWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Heimdall AI Assistant (PyQt5)")
            self.setGeometry(100, 100, 800, 600)
            
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            
            # Header
            header = QLabel("Heimdall AI Assistant")
            header.setStyleSheet("color: #d4af37; font-size: 18px; font-weight: bold; padding: 20px;")
            layout.addWidget(header)
            
            # Chat
            self.chat = QTextEdit()
            self.chat.setStyleSheet("background: #1a1a1a; color: white;")
            self.chat.append("Welcome to Heimdall! (PyQt5 version)")
            layout.addWidget(self.chat)
            
            # Input
            input_layout = QHBoxLayout()
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText("Type message...")
            self.input_field.returnPressed.connect(self.send_message)
            
            send_btn = QPushButton("Send")
            send_btn.clicked.connect(self.send_message)
            
            input_layout.addWidget(self.input_field)
            input_layout.addWidget(send_btn)
            layout.addLayout(input_layout)
            
            self.setStyleSheet("QMainWindow { background: #0a0a0a; color: white; }")
        
        def send_message(self):
            text = self.input_field.text().strip()
            if text:
                self.chat.append(f"You: {text}")
                self.chat.append(f"Heimdall: Got it - '{text}'!")
                self.input_field.clear()
    
    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    print("✅ PyQt5 GUI started!")
    return app.exec_()

def run_tkinter():
    """Tkinter fallback"""
    import tkinter as tk
    from tkinter import scrolledtext
    
    root = tk.Tk()
    root.title("Heimdall AI Assistant")
    root.geometry("900x700")
    root.configure(bg="#0a0a0a")
    
    # Header
    header = tk.Label(
        root, text="👁 Heimdall AI Assistant",
        font=("Arial", 18, "bold"), bg="#1a1a1a", fg="#d4af37", pady=15
    )
    header.pack(fill=tk.X)
    
    # Chat
    chat_display = scrolledtext.ScrolledText(
        root, wrap=tk.WORD, font=("Arial", 11),
        bg="#1a1a1a", fg="#ffffff", insertbackground="#d4af37"
    )
    chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Welcome message
    chat_display.insert(tk.END, "🎉 Welcome to Heimdall AI Assistant!\n\n")
    chat_display.insert(tk.END, "✨ Modern dark theme with gold & purple accents\n")
    chat_display.insert(tk.END, "💬 Type your messages below\n")
    chat_display.insert(tk.END, "🎤 Voice commands supported\n\n")
    
    # Input
    input_frame = tk.Frame(root, bg="#1a1a1a")
    input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    entry_var = tk.StringVar()
    entry = tk.Entry(
        input_frame, textvariable=entry_var, font=("Arial", 12),
        bg="#2a2a2a", fg="#ffffff", insertbackground="#d4af37", relief=tk.FLAT, bd=5
    )
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
    
    def send_message():
        text = entry_var.get().strip()
        if text:
            chat_display.insert(tk.END, f"🧑 You: {text}\n")
            chat_display.insert(tk.END, f"🤖 Heimdall: I understand '{text}'. Demo response!\n\n")
            chat_display.see(tk.END)
            entry_var.set("")
    
    entry.bind("<Return>", lambda e: send_message())
    
    send_btn = tk.Button(
        input_frame, text="Send", command=send_message,
        bg="#8b5cf6", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, padx=20
    )
    send_btn.pack(side=tk.RIGHT, padx=(5, 5))
    
    print("✅ Tkinter GUI started!")
    root.mainloop()
    return 0

def run_cli():
    """Command line fallback"""
    print("\n" + "="*60)
    print("🏠 HEIMDALL AI ASSISTANT - COMMAND LINE MODE")
    print("="*60)
    print("💡 GUI libraries not available, running in terminal")
    print("🎨 For the full experience, install: pip install PyQt6")
    print("="*60 + "\n")
    
    print("🤖 Heimdall: Hello! I'm your AI assistant.")
    print("💬 Type commands below (or 'quit' to exit):\n")
    
    while True:
        try:
            user_input = input("🧑 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("🤖 Heimdall: Goodbye! 👋")
                break
            
            if user_input:
                print(f"🤖 Heimdall: I got your command '{user_input}'.")
                print("   This is a demo response. Install GUI for full functionality!\n")
            
        except (KeyboardInterrupt, EOFError):
            print("\n🤖 Heimdall: Goodbye! 👋")
            break
    
    return 0

if __name__ == "__main__":
    # Ensure data directories exist
    os.makedirs("./data/logs", exist_ok=True)
    os.makedirs("./data/screenshots", exist_ok=True)
    
    sys.exit(main())