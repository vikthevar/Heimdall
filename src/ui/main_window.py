"""
Modern Desktop UI for Heimdall AI Assistant - Framer Motion Style
Built with PyQt6 with dark theme, gold/purple accents, and smooth animations
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QScrollArea,
    QSplitter, QStackedWidget, QListWidget, QListWidgetItem, QSystemTrayIcon,
    QMenu, QToolButton, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect,
    QGraphicsBlurEffect, QSlider, QCheckBox, QComboBox
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QThread,
    QSequentialAnimationGroup, QParallelAnimationGroup, QRect, QPoint, QSize
)
from PyQt6.QtGui import (
    QFont, QPixmap, QPainter, QPainterPath, QColor, QLinearGradient,
    QIcon, QAction, QPalette, QBrush, QPen, QRadialGradient
)
from datetime import datetime
import json
import math


class ModernMessageBubble(QFrame):
    """Modern message bubble with Framer Motion styling"""
    
    def __init__(self, message, is_user=True, timestamp=None):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        
        self.setup_ui()
        self.apply_animations()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        if not self.is_user:
            # AI Avatar
            avatar = QLabel("H")
            avatar.setFixedSize(40, 40)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #8b5cf6, stop:1 #d4af37);
                    border-radius: 20px;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                }
            """)
            layout.addWidget(avatar)
        
        # Message container
        message_container = QFrame()
        message_container.setObjectName("message_bubble")
        message_layout = QVBoxLayout(message_container)
        message_layout.setContentsMargins(16, 12, 16, 12)
        
        # Message text
        message_text = QLabel(self.message)
        message_text.setObjectName("message_text")
        message_text.setWordWrap(True)
        message_text.setFont(QFont("Inter", 11))
        
        # Timestamp
        time_text = QLabel(self.timestamp.strftime("%H:%M"))
        time_text.setObjectName("message_time")
        time_text.setFont(QFont("Inter", 9))
        
        message_layout.addWidget(message_text)
        message_layout.addWidget(time_text)
        
        if self.is_user:
            layout.addStretch()
            layout.addWidget(message_container)
        else:
            layout.addWidget(message_container)
            layout.addStretch()
        
        # Apply styles
        from .modern_styles import get_message_bubble_style
        message_container.setStyleSheet(get_message_bubble_style(self.is_user))
    
    def apply_animations(self):
        """Apply entrance animations"""
        # Fade in animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Start animation
        QTimer.singleShot(50, self.fade_animation.start)


class ChatMessage(QFrame):
    """Individual chat message widget"""
    
    def __init__(self, message, is_user=True, timestamp=None):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        if not self.is_user:
            # AI Avatar
            avatar = QLabel()
            avatar.setFixedSize(40, 40)
            avatar.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    border-radius: 20px;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                }
            """)
            avatar.setText("H")
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(avatar)
        
        # Message bubble
        message_frame = QFrame()
        message_layout = QVBoxLayout(message_frame)
        message_layout.setContentsMargins(15, 10, 15, 10)
        
        # Message text
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Segoe UI", 11))
        
        # Timestamp
        time_label = QLabel(self.timestamp.strftime("%H:%M"))
        time_label.setFont(QFont("Segoe UI", 9))
        time_label.setStyleSheet("color: rgba(0, 0, 0, 0.5);")
        
        message_layout.addWidget(message_label)
        message_layout.addWidget(time_label)
        
        if self.is_user:
            message_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    border-radius: 15px;
                    color: white;
                }
            """)
            message_label.setStyleSheet("color: white;")
            time_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            layout.addStretch()
            layout.addWidget(message_frame)
        else:
            message_frame.setStyleSheet("""
                QFrame {
                    background: rgba(0, 0, 0, 0.05);
                    border-radius: 15px;
                    border: 1px solid rgba(0, 0, 0, 0.1);
                }
            """)
            layout.addWidget(message_frame)
            layout.addStretch()


class StatusIndicator(QLabel):
    """AI status indicator with animations"""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(12, 12)
        self.status = "idle"  # idle, listening, processing, speaking
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.update_status("idle")
    
    def update_status(self, status):
        self.status = status
        colors = {
            "idle": "#95a5a6",
            "listening": "#3498db",
            "processing": "#f39c12",
            "speaking": "#2ecc71"
        }
        
        self.setStyleSheet(f"""
            QLabel {{
                background: {colors.get(status, '#95a5a6')};
                border-radius: 6px;
            }}
        """)
        
        if status in ["listening", "processing"]:
            self.start_pulse_animation()
        else:
            self.animation.stop()
    
    def start_pulse_animation(self):
        self.animation.finished.connect(self.reverse_animation)
        self.animation.start()
    
    def reverse_animation(self):
        # Create pulsing effect
        pass


class SidebarButton(QPushButton):
    """Sidebar navigation button"""
    
    def __init__(self, text, icon_name=None, active=False):
        super().__init__(text)
        self.active = active
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.apply_style()
    
    def apply_style(self):
        if self.active:
            style = """
                QPushButton {
                    background: rgba(102, 126, 234, 0.1);
                    color: #667eea;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    text-align: left;
                    padding-left: 20px;
                }
            """
        else:
            style = """
                QPushButton {
                    background: transparent;
                    color: #666;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background: rgba(0, 0, 0, 0.05);
                    color: #333;
                }
            """
        self.setStyleSheet(style)
    
    def set_active(self, active):
        self.active = active
        self.apply_style()


class HeimdallMainWindow(QMainWindow):
    """Main application window - Framer Motion Style"""
    
    # Signals
    message_sent = pyqtSignal(str)
    voice_command_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_view = "chat"
        self.messages = []
        self.setup_ui()
        self.setup_animations()
        self.apply_theme()
    
    def setup_ui(self):
        self.setWindowTitle("Heimdall AI Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        
        # Remove window frame for modern look
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.create_sidebar(main_layout)
        
        # Create main content area
        self.create_main_content(main_layout)
        
        # Create status bar
        self.create_status_bar()
    
    def create_sidebar(self, parent_layout):
        """Create the modern sidebar navigation"""
        from .animated_widgets import SlideInWidget, PulsingDot
        from .modern_styles import get_sidebar_style, get_nav_button_style
        
        # Sidebar container
        sidebar = SlideInWidget(direction="left")
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(get_sidebar_style())
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(24, 30, 24, 20)
        sidebar_layout.setSpacing(16)
        
        # Logo section with animated icon
        logo_container = QFrame()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # Animated logo icon
        logo_icon = QLabel("👁")
        logo_icon.setFixedSize(48, 48)
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8b5cf6, stop:1 #d4af37);
                border-radius: 12px;
                font-size: 24px;
            }
        """)
        
        # Logo text
        logo_text_container = QVBoxLayout()
        logo_title = QLabel("Heimdall")
        logo_title.setObjectName("logo_title")
        logo_subtitle = QLabel("AI Assistant")
        logo_subtitle.setObjectName("logo_subtitle")
        
        logo_text_container.addWidget(logo_title)
        logo_text_container.addWidget(logo_subtitle)
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addLayout(logo_text_container)
        logo_layout.addStretch()
        
        sidebar_layout.addWidget(logo_container)
        
        # Connection status
        connection_frame = QFrame()
        connection_layout = QHBoxLayout(connection_frame)
        connection_layout.setContentsMargins(12, 8, 12, 8)
        
        self.connection_dot = PulsingDot()
        self.connection_dot.set_status("idle")
        connection_text = QLabel("Connected")
        connection_text.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        
        connection_layout.addWidget(self.connection_dot)
        connection_layout.addWidget(connection_text)
        connection_layout.addStretch()
        
        connection_frame.setStyleSheet("""
            QFrame {
                background: rgba(42, 42, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        
        sidebar_layout.addWidget(connection_frame)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("💬", "Chat"),
            ("🎤", "Voice"),
            ("🖥️", "Screen"),
            ("⚙️", "Settings")
        ]
        
        nav_container = QFrame()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setSpacing(8)
        
        for icon, text in nav_items:
            btn = QPushButton(f"{icon}  {text}")
            btn.setObjectName("nav_button")
            btn.setCheckable(True)
            btn.setChecked(text == "Chat")
            btn.clicked.connect(lambda checked, t=text: self.switch_view(t.lower()))
            btn.setStyleSheet(get_nav_button_style())
            
            self.nav_buttons[text] = btn
            nav_layout.addWidget(btn)
        
        sidebar_layout.addWidget(nav_container)
        sidebar_layout.addStretch()
        
        # AI Status section
        ai_status_frame = QFrame()
        ai_status_layout = QVBoxLayout(ai_status_frame)
        ai_status_layout.setContentsMargins(16, 12, 16, 12)
        
        status_header = QLabel("⚡ AI Status")
        status_header.setStyleSheet("color: #d4af37; font-weight: 600; font-size: 12px;")
        
        status_info_layout = QHBoxLayout()
        self.ai_status_dot = PulsingDot()
        self.ai_status_dot.set_status("idle")
        self.ai_status_text = QLabel("Ready")
        self.ai_status_text.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        
        status_info_layout.addWidget(self.ai_status_dot)
        status_info_layout.addWidget(self.ai_status_text)
        status_info_layout.addStretch()
        
        ai_status_layout.addWidget(status_header)
        ai_status_layout.addLayout(status_info_layout)
        
        ai_status_frame.setStyleSheet("""
            QFrame {
                background: rgba(42, 42, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        
        sidebar_layout.addWidget(ai_status_frame)
        
        parent_layout.addWidget(sidebar)
        
        # Animate sidebar entrance
        QTimer.singleShot(100, sidebar.slide_in)
    
    def create_main_content(self, parent_layout):
        """Create the main content area"""
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header
        self.create_header(content_layout)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Create views
        self.create_chat_view()
        self.create_voice_view()
        self.create_screen_view()
        self.create_settings_view()
        
        content_layout.addWidget(self.stacked_widget)
        parent_layout.addWidget(content_frame)
    
    def create_header(self, parent_layout):
        """Create the modern header with glass effect"""
        from .modern_styles import get_header_style, get_button_style
        from .animated_widgets import AnimatedButton
        
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(80)
        header.setStyleSheet(get_header_style())
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(32, 0, 32, 0)
        
        # Title section
        title_container = QVBoxLayout()
        self.header_title = QLabel("Chat with Heimdall")
        self.header_title.setObjectName("header_title")
        
        self.header_subtitle = QLabel("Your AI assistant for screen navigation and control")
        self.header_subtitle.setObjectName("header_subtitle")
        
        title_container.addWidget(self.header_title)
        title_container.addWidget(self.header_subtitle)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Control buttons
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        # Voice button
        self.voice_btn = AnimatedButton("🎤")
        self.voice_btn.setFixedSize(44, 44)
        self.voice_btn.setStyleSheet(get_button_style("ghost"))
        self.voice_btn.clicked.connect(self.toggle_voice_listening)
        
        # Screenshot button
        screenshot_btn = AnimatedButton("📸")
        screenshot_btn.setFixedSize(44, 44)
        screenshot_btn.setStyleSheet(get_button_style("ghost"))
        
        # Settings button
        settings_btn = AnimatedButton("⚙️")
        settings_btn.setFixedSize(44, 44)
        settings_btn.setStyleSheet(get_button_style("ghost"))
        
        # Window controls
        minimize_btn = AnimatedButton("−")
        minimize_btn.setFixedSize(32, 32)
        minimize_btn.setStyleSheet(get_button_style("ghost"))
        minimize_btn.clicked.connect(self.showMinimized)
        
        close_btn = AnimatedButton("×")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet(get_button_style("ghost"))
        close_btn.clicked.connect(self.close)
        
        controls_layout.addWidget(self.voice_btn)
        controls_layout.addWidget(screenshot_btn)
        controls_layout.addWidget(settings_btn)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(minimize_btn)
        controls_layout.addWidget(close_btn)
        
        header_layout.addLayout(controls_layout)
        parent_layout.addWidget(header)
    
    def create_chat_view(self):
        """Create the modern chat interface"""
        from .modern_styles import get_chat_style, get_input_style, get_button_style
        from .animated_widgets import FadeInWidget, TypingIndicator
        
        chat_widget = FadeInWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        # Chat messages area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setObjectName("chat_scroll")
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarNever)
        self.chat_scroll.setStyleSheet(get_chat_style())
        
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setContentsMargins(32, 24, 32, 24)
        self.chat_layout.setSpacing(16)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_content)
        chat_layout.addWidget(self.chat_scroll)
        
        # Typing indicator (hidden by default)
        self.typing_indicator = TypingIndicator()
        self.typing_indicator.hide()
        
        # Quick actions (shown when no messages)
        self.create_quick_actions()
        
        # Input area with glass effect
        input_container = QFrame()
        input_container.setObjectName("input_container")
        input_container.setStyleSheet(get_input_style())
        
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(32, 20, 32, 20)
        
        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(12)
        
        # Message input with modern styling
        input_wrapper = QFrame()
        input_wrapper.setStyleSheet("""
            QFrame {
                background: rgba(42, 42, 42, 0.8);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 25px;
            }
            QFrame:focus-within {
                border-color: #d4af37;
            }
        """)
        
        input_wrapper_layout = QHBoxLayout(input_wrapper)
        input_wrapper_layout.setContentsMargins(4, 4, 4, 4)
        
        self.message_input = QLineEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setPlaceholderText("Type your message or command...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                padding: 12px 20px;
                font-size: 16px;
                color: white;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        
        # Voice button
        voice_input_btn = QPushButton("🎤")
        voice_input_btn.setFixedSize(44, 44)
        voice_input_btn.setStyleSheet("""
            QPushButton {
                background: rgba(139, 92, 246, 0.2);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 22px;
                color: #8b5cf6;
                font-size: 18px;
            }
            QPushButton:hover {
                background: rgba(139, 92, 246, 0.3);
            }
        """)
        
        # Send button
        send_btn = QPushButton("Send")
        send_btn.setFixedSize(80, 44)
        send_btn.setStyleSheet(get_button_style("primary"))
        send_btn.clicked.connect(self.send_message)
        
        input_wrapper_layout.addWidget(self.message_input)
        input_wrapper_layout.addWidget(voice_input_btn)
        input_wrapper_layout.addWidget(send_btn)
        
        input_row.addWidget(input_wrapper)
        
        # Status indicators
        status_row = QHBoxLayout()
        
        connection_status = QLabel("🟢 Connected")
        connection_status.setStyleSheet("color: #666666; font-size: 12px;")
        
        ai_status = QLabel("⚡ Ready")
        ai_status.setStyleSheet("color: #666666; font-size: 12px;")
        
        status_row.addWidget(connection_status)
        status_row.addStretch()
        status_row.addWidget(ai_status)
        
        input_layout.addLayout(input_row)
        input_layout.addLayout(status_row)
        
        chat_layout.addWidget(input_container)
        
        self.stacked_widget.addWidget(chat_widget)
        
        # Add welcome message
        QTimer.singleShot(500, lambda: self.add_message(
            "Hello! I'm Heimdall, your AI assistant. I can help you navigate your screen, "
            "control applications, and answer questions. Try commands like 'Read what's on my screen' "
            "or 'Click the blue button'.", False
        ))
        
        # Fade in the chat view
        QTimer.singleShot(100, chat_widget.fade_in)
    
    def create_quick_actions(self):
        """Create quick action buttons"""
        self.quick_actions_container = QFrame()
        quick_layout = QVBoxLayout(self.quick_actions_container)
        quick_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Try these commands:")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #b0b0b0; font-size: 16px; font-weight: 500; margin: 20px;")
        quick_layout.addWidget(title)
        
        actions_grid = QHBoxLayout()
        actions_grid.setSpacing(16)
        
        quick_actions = [
            ("👁️", "Read what's on my screen"),
            ("🖱️", "Click the blue button"),
            ("⬇️", "Scroll down"),
            ("🧭", "Help me navigate")
        ]
        
        for icon, text in quick_actions:
            btn = QPushButton(f"{icon}\n{text}")
            btn.setFixedSize(160, 80)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(30, 30, 30, 0.8);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    color: white;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(139, 92, 246, 0.2),
                        stop:1 rgba(212, 175, 55, 0.2));
                    border-color: #d4af37;
                }
            """)
            btn.clicked.connect(lambda checked, t=text: self.send_message_text(t))
            actions_grid.addWidget(btn)
        
        quick_layout.addLayout(actions_grid)
        self.chat_layout.insertWidget(0, self.quick_actions_container)
    
    def create_voice_view(self):
        """Create voice commands view"""
        voice_widget = QWidget()
        voice_layout = QVBoxLayout(voice_widget)
        voice_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Voice Commands")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        voice_layout.addWidget(title)
        
        # Voice commands list
        commands_text = """
        <h3>Available Voice Commands:</h3>
        <ul>
            <li><b>"Read what's on my screen"</b> - Reads all visible text</li>
            <li><b>"Click the [element]"</b> - Clicks on specified UI element</li>
            <li><b>"Scroll down/up"</b> - Scrolls the page</li>
            <li><b>"Type [text]"</b> - Types the specified text</li>
            <li><b>"Press [key]"</b> - Presses keyboard keys</li>
            <li><b>"What's in the top right?"</b> - Analyzes screen regions</li>
            <li><b>"Go back/forward"</b> - Browser navigation</li>
            <li><b>"Stop Heimdall"</b> - Exits the application</li>
        </ul>
        """
        
        commands_label = QLabel(commands_text)
        commands_label.setWordWrap(True)
        commands_label.setStyleSheet("font-size: 14px; line-height: 1.6;")
        
        voice_layout.addWidget(commands_label)
        voice_layout.addStretch()
        
        self.stacked_widget.addWidget(voice_widget)
    
    def create_screen_view(self):
        """Create screen analysis view"""
        screen_widget = QWidget()
        screen_layout = QVBoxLayout(screen_widget)
        screen_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Screen Analysis")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        screen_layout.addWidget(title)
        
        # Placeholder for screen analysis features
        placeholder = QLabel("Screen analysis features will be displayed here.")
        placeholder.setStyleSheet("color: #666; font-size: 14px;")
        screen_layout.addWidget(placeholder)
        screen_layout.addStretch()
        
        self.stacked_widget.addWidget(screen_widget)
    
    def create_settings_view(self):
        """Create settings view"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        settings_layout.addWidget(title)
        
        # Theme toggle
        theme_frame = QFrame()
        theme_layout = QHBoxLayout(theme_frame)
        
        theme_label = QLabel("Dark Mode")
        theme_label.setStyleSheet("font-size: 14px;")
        
        theme_toggle = ModernButton("Toggle", primary=False)
        theme_toggle.clicked.connect(self.toggle_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addStretch()
        theme_layout.addWidget(theme_toggle)
        
        settings_layout.addWidget(theme_frame)
        settings_layout.addStretch()
        
        self.stacked_widget.addWidget(settings_widget)
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/heimdall_icon.png"))  # You'll need to add this
        
        tray_menu = QMenu()
        show_action = QAction("Show Heimdall", self)
        show_action.triggered.connect(self.show)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def switch_view(self, view_name):
        """Switch between different views"""
        # Update navigation buttons
        for name, btn in self.nav_buttons.items():
            btn.set_active(name == view_name)
        
        # Update header title
        self.header_title.setText(view_name)
        
        # Switch stacked widget
        view_index = {
            "Chat": 0,
            "Voice Commands": 1,
            "Screen Analysis": 2,
            "Settings": 3
        }.get(view_name, 0)
        
        self.stacked_widget.setCurrentIndex(view_index)
    
    def add_message(self, message, is_user=True):
        """Add a message to the chat"""
        message_widget = ChatMessage(message, is_user)
        
        # Insert before the stretch
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_widget)
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Send a message"""
        text = self.message_input.text().strip()
        if text:
            self.add_message(text, True)
            self.message_input.clear()
            self.message_sent.emit(text)
    
    def toggle_voice_listening(self):
        """Toggle voice listening"""
        self.status_indicator.update_status("listening")
        # Emit signal to start voice recognition
        # This will be connected to the voice handler
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme"""
        if self.dark_mode:
            # Dark theme styles
            self.setStyleSheet("""
                QMainWindow {
                    background: #2c3e50;
                    color: white;
                }
                QFrame {
                    background: #34495e;
                    color: white;
                }
                QLabel {
                    color: white;
                }
            """)
        else:
            # Light theme (default)
            self.setStyleSheet("""
                QMainWindow {
                    background: white;
                    color: #333;
                }
            """)
    
    def closeEvent(self, event):
        """Handle close event - minimize to tray"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Heimdall",
            "Application was minimized to tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Heimdall AI Assistant")
    app.setQuitOnLastWindowClosed(False)
    
    # Set application icon
    app.setWindowIcon(QIcon("assets/heimdall_icon.png"))
    
    window = HeimdallMainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())