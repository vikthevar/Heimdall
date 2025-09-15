"""
Reusable UI Components for Heimdall
"""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QFrame, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QIcon
from datetime import datetime
import math


class AnimatedButton(QPushButton):
    """Button with smooth hover animations"""
    
    def __init__(self, text="", icon=None, primary=False):
        super().__init__(text)
        self.primary = primary
        self.default_height = 40
        self.setFixedHeight(self.default_height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if icon:
            self.setIcon(QIcon(icon))
        
        # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
        self.apply_style()
    
    def apply_style(self):
        """Apply button styling"""
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-weight: 600;
                    font-size: 14px;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5a6fd8, stop:1 #6a4190);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4e5bc6, stop:1 #5e3778);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.9);
                    color: #333;
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    border-radius: 20px;
                    font-size: 14px;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background: white;
                    border: 1px solid rgba(0, 0, 0, 0.2);
                }
                QPushButton:pressed {
                    background: rgba(0, 0, 0, 0.05);
                }
            """)


class StatusCard(QFrame):
    """Card component for displaying status information"""
    
    def __init__(self, title, value, icon=None, color="#667eea"):
        super().__init__()
        self.title = title
        self.value = value
        self.color = color
        
        self.setFixedHeight(120)
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        """Setup the card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 12))
        title_label.setStyleSheet("color: rgba(0, 0, 0, 0.6);")
        
        # Value
        value_label = QLabel(str(self.value))
        value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {self.color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
    
    def apply_style(self):
        """Apply card styling"""
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }}
            QFrame:hover {{
                border: 1px solid {self.color};
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def update_value(self, new_value):
        """Update the card value"""
        self.value = new_value
        # Find and update the value label
        for child in self.findChildren(QLabel):
            if child.font().pointSize() == 24:
                child.setText(str(new_value))
                break


class PulsingIndicator(QLabel):
    """Animated pulsing indicator for AI status"""
    
    def __init__(self, size=16):
        super().__init__()
        self.setFixedSize(size, size)
        self.status = "idle"
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(1500)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.setLoopCount(-1)  # Infinite loop
        
        self.update_status("idle")
    
    def update_status(self, status):
        """Update indicator status with color and animation"""
        self.status = status
        
        colors = {
            "idle": "#95a5a6",
            "listening": "#3498db", 
            "processing": "#f39c12",
            "speaking": "#2ecc71",
            "error": "#e74c3c"
        }
        
        color = colors.get(status, "#95a5a6")
        
        self.setStyleSheet(f"""
            QLabel {{
                background: {color};
                border-radius: {self.width() // 2}px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }}
        """)
        
        # Start animation for active states
        if status in ["listening", "processing", "speaking"]:
            self.start_pulse()
        else:
            self.stop_pulse()
    
    def start_pulse(self):
        """Start pulsing animation"""
        original_size = self.size()
        larger_size = original_size * 1.2
        
        # Create pulsing effect by changing opacity
        self.animation.finished.connect(self.reverse_pulse)
        self.animation.start()
    
    def stop_pulse(self):
        """Stop pulsing animation"""
        self.animation.stop()
    
    def reverse_pulse(self):
        """Reverse the pulse animation"""
        # This creates a continuous pulsing effect
        pass


class VoiceWaveform(QWidget):
    """Animated waveform display for voice input"""
    
    def __init__(self, width=200, height=60):
        super().__init__()
        self.setFixedSize(width, height)
        self.bars = []
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        # Initialize bars
        self.num_bars = 20
        for i in range(self.num_bars):
            self.bars.append(0.1)  # Minimum height
    
    def start_animation(self):
        """Start waveform animation"""
        self.animation_timer.start(50)  # Update every 50ms
    
    def stop_animation(self):
        """Stop waveform animation"""
        self.animation_timer.stop()
        # Reset bars to minimum
        self.bars = [0.1] * self.num_bars
        self.update()
    
    def update_animation(self):
        """Update waveform bars"""
        import random
        
        # Simulate audio levels
        for i in range(self.num_bars):
            # Create wave-like pattern
            base_height = 0.3 + 0.4 * math.sin(i * 0.5)
            noise = random.uniform(-0.2, 0.2)
            self.bars[i] = max(0.1, min(1.0, base_height + noise))
        
        self.update()
    
    def paintEvent(self, event):
        """Paint the waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bar_width = self.width() / self.num_bars
        max_height = self.height() - 10
        
        for i, height in enumerate(self.bars):
            x = i * bar_width + 2
            bar_height = height * max_height
            y = (self.height() - bar_height) / 2
            
            # Color gradient based on height
            if height > 0.7:
                color = QColor("#e74c3c")  # Red for high levels
            elif height > 0.4:
                color = QColor("#f39c12")  # Orange for medium levels
            else:
                color = QColor("#3498db")  # Blue for low levels
            
            painter.fillRect(int(x), int(y), int(bar_width - 4), int(bar_height), color)


class NotificationToast(QFrame):
    """Toast notification component"""
    
    def __init__(self, message, notification_type="info", duration=3000):
        super().__init__()
        self.message = message
        self.type = notification_type
        self.duration = duration
        
        self.setup_ui()
        self.apply_style()
        
        # Auto-hide timer
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.fade_out)
        self.hide_timer.setSingleShot(True)
        
        # Fade animations
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        
    def setup_ui(self):
        """Setup notification UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon based on type
        icons = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌"
        }
        
        icon_label = QLabel(icons.get(self.type, "ℹ️"))
        icon_label.setFont(QFont("Segoe UI", 16))
        
        # Message
        message_label = QLabel(self.message)
        message_label.setFont(QFont("Segoe UI", 12))
        message_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label)
        layout.addStretch()
    
    def apply_style(self):
        """Apply notification styling"""
        colors = {
            "info": "#3498db",
            "success": "#2ecc71",
            "warning": "#f39c12", 
            "error": "#e74c3c"
        }
        
        color = colors.get(self.type, "#3498db")
        
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 10px;
            }}
            QLabel {{
                color: #333;
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def show_notification(self):
        """Show notification with fade in"""
        self.setWindowOpacity(0)
        self.show()
        
        # Fade in
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.start()
        
        # Start hide timer
        self.hide_timer.start(self.duration)
    
    def fade_out(self):
        """Fade out and hide notification"""
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.finished.connect(self.hide)
        self.fade_out_animation.start()


class ProgressIndicator(QProgressBar):
    """Modern progress indicator"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(4)
        self.setTextVisible(False)
        
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 2px;
                background: rgba(0, 0, 0, 0.1);
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 2px;
            }
        """)
    
    def start_indeterminate(self):
        """Start indeterminate progress animation"""
        self.setRange(0, 0)  # Indeterminate mode
    
    def stop_indeterminate(self):
        """Stop indeterminate progress"""
        self.setRange(0, 100)
        self.setValue(0)


class ChatBubble(QFrame):
    """Enhanced chat bubble with better styling"""
    
    def __init__(self, message, is_user=True, timestamp=None, avatar_text="H"):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        self.avatar_text = avatar_text
        
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        """Setup chat bubble UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 10)
        
        if not self.is_user:
            # AI Avatar
            avatar = QLabel(self.avatar_text)
            avatar.setFixedSize(36, 36)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    border-radius: 18px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            main_layout.addWidget(avatar)
        
        # Message container
        message_container = QFrame()
        message_layout = QVBoxLayout(message_container)
        message_layout.setContentsMargins(16, 12, 16, 12)
        message_layout.setSpacing(4)
        
        # Message text
        message_text = QLabel(self.message)
        message_text.setWordWrap(True)
        message_text.setFont(QFont("Segoe UI", 11))
        
        # Timestamp
        time_text = QLabel(self.timestamp.strftime("%H:%M"))
        time_text.setFont(QFont("Segoe UI", 9))
        
        message_layout.addWidget(message_text)
        message_layout.addWidget(time_text)
        
        if self.is_user:
            main_layout.addStretch()
            main_layout.addWidget(message_container)
        else:
            main_layout.addWidget(message_container)
            main_layout.addStretch()
    
    def apply_style(self):
        """Apply chat bubble styling"""
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    border-radius: 18px;
                    color: white;
                }
                QLabel {
                    color: white;
                    background: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: rgba(0, 0, 0, 0.04);
                    border-radius: 18px;
                    border: 1px solid rgba(0, 0, 0, 0.08);
                }
                QLabel {
                    color: #333;
                    background: transparent;
                }
            """)


class LoadingSpinner(QLabel):
    """Animated loading spinner"""
    
    def __init__(self, size=32):
        super().__init__()
        self.setFixedSize(size, size)
        self.angle = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        
    def start_spinning(self):
        """Start spinner animation"""
        self.timer.start(50)  # Update every 50ms
    
    def stop_spinning(self):
        """Stop spinner animation"""
        self.timer.stop()
        self.angle = 0
        self.update()
    
    def rotate(self):
        """Rotate the spinner"""
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        """Paint the spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw spinning circle
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        
        # Draw arcs with gradient opacity
        for i in range(8):
            painter.rotate(45)
            opacity = 255 - (i * 30)
            painter.setPen(QColor(102, 126, 234, max(50, opacity)))
            painter.drawLine(0, -self.width() // 3, 0, -self.width() // 4)