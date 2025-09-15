#!/usr/bin/env python3
"""
Settings Dialog - UI for managing user preferences
Provides a comprehensive settings interface with validation
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QWidget, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox,
                           QComboBox, QPushButton, QGroupBox, QFormLayout,
                           QSlider, QMessageBox, QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.core.settings_manager import settings_manager

class SettingsDialog(QDialog):
    """Settings dialog with tabbed interface"""
    
    settings_changed = pyqtSignal()  # Emitted when settings are saved
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Heimdall Settings")
        self.setModal(True)
        self.setFixedSize(600, 500)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_general_tab()
        self.create_voice_tab()
        self.create_automation_tab()
        self.create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: #FF6B6B;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background: #FF5252; }
        """)
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #666;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background: #777; }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background: #45a049; }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background: #0a0a0a;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background: #1a1a1a;
            }
            QTabBar::tab {
                background: #2a2a2a;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #d4af37;
                color: black;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: white;
            }
            QCheckBox {
                color: white;
                spacing: 8px;
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
            QComboBox, QSpinBox, QDoubleSpinBox {
                background: #2a2a2a;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 8px;
                background: #2a2a2a;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #d4af37;
                border: 1px solid #b8860b;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
    
    def create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # UI Settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.simulation_mode_cb = QCheckBox("Enable Simulation Mode (Safe)")
        self.simulation_mode_cb.setToolTip("When enabled, automation actions are simulated without execution")
        ui_layout.addRow("Automation:", self.simulation_mode_cb)
        
        self.demo_safe_mode_cb = QCheckBox("Demo Safe Mode")
        self.demo_safe_mode_cb.setToolTip("Prevents all real automation execution")
        ui_layout.addRow("Safety:", self.demo_safe_mode_cb)
        
        self.auto_analyze_ocr_cb = QCheckBox("Auto-analyze OCR Results")
        self.auto_analyze_ocr_cb.setToolTip("Automatically analyze screen content with AI after OCR")
        ui_layout.addRow("Screen Reading:", self.auto_analyze_ocr_cb)
        
        self.debug_mode_cb = QCheckBox("Enable Debug Mode")
        self.debug_mode_cb.setToolTip("Show additional debug information")
        ui_layout.addRow("Debug:", self.debug_mode_cb)
        
        layout.addWidget(ui_group)
        
        # Window Settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout(window_group)
        
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 2000)
        self.window_width_spin.setSuffix(" px")
        window_layout.addRow("Width:", self.window_width_spin)
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 1500)
        self.window_height_spin.setSuffix(" px")
        window_layout.addRow("Height:", self.window_height_spin)
        
        layout.addWidget(window_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "General")
    
    def create_voice_tab(self):
        """Create voice settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Voice Input
        input_group = QGroupBox("Voice Input")
        input_layout = QFormLayout(input_group)
        
        self.voice_input_enabled_cb = QCheckBox("Enable Voice Input")
        self.voice_input_enabled_cb.setToolTip("Allow voice recording and transcription")
        input_layout.addRow("Microphone:", self.voice_input_enabled_cb)
        
        self.whisper_model_combo = QComboBox()
        self.whisper_model_combo.addItems(['tiny', 'base', 'small', 'medium', 'large'])
        self.whisper_model_combo.setToolTip("Whisper model size (larger = more accurate, slower)")
        input_layout.addRow("Model Size:", self.whisper_model_combo)
        
        self.max_recording_spin = QSpinBox()
        self.max_recording_spin.setRange(1, 30)
        self.max_recording_spin.setSuffix(" seconds")
        self.max_recording_spin.setToolTip("Maximum recording duration")
        input_layout.addRow("Max Duration:", self.max_recording_spin)
        
        self.auto_send_transcript_cb = QCheckBox("Auto-send Transcript")
        self.auto_send_transcript_cb.setToolTip("Automatically send transcribed text to AI")
        input_layout.addRow("Auto-send:", self.auto_send_transcript_cb)
        
        layout.addWidget(input_group)
        
        # Voice Output
        output_group = QGroupBox("Voice Output (TTS)")
        output_layout = QFormLayout(output_group)
        
        self.voice_output_enabled_cb = QCheckBox("Enable Voice Output")
        self.voice_output_enabled_cb.setToolTip("Speak AI responses using text-to-speech")
        output_layout.addRow("Speaker:", self.voice_output_enabled_cb)
        
        # TTS Rate
        rate_layout = QHBoxLayout()
        self.tts_rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.tts_rate_slider.setRange(50, 300)
        self.tts_rate_label = QLabel("150")
        self.tts_rate_slider.valueChanged.connect(lambda v: self.tts_rate_label.setText(str(v)))
        rate_layout.addWidget(self.tts_rate_slider)
        rate_layout.addWidget(self.tts_rate_label)
        output_layout.addRow("Speech Rate:", rate_layout)
        
        # TTS Volume
        volume_layout = QHBoxLayout()
        self.tts_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.tts_volume_slider.setRange(0, 100)
        self.tts_volume_label = QLabel("80%")
        self.tts_volume_slider.valueChanged.connect(lambda v: self.tts_volume_label.setText(f"{v}%"))
        volume_layout.addWidget(self.tts_volume_slider)
        volume_layout.addWidget(self.tts_volume_label)
        output_layout.addRow("Volume:", volume_layout)
        
        layout.addWidget(output_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Voice")
    
    def create_automation_tab(self):
        """Create automation settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Safety Settings
        safety_group = QGroupBox("Safety & Confirmation")
        safety_layout = QFormLayout(safety_group)
        
        safety_info = QLabel("These settings control automation safety and user confirmation requirements.")
        safety_info.setWordWrap(True)
        safety_info.setStyleSheet("color: #888; font-style: italic;")
        safety_layout.addRow(safety_info)
        
        # Add automation-specific settings here
        # (These would be implemented based on your automation needs)
        
        layout.addWidget(safety_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Automation")
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logging
        logging_group = QGroupBox("Logging & Debug")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.log_level_combo.setToolTip("Set logging verbosity level")
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        layout.addWidget(logging_group)
        
        # Settings Info
        info_group = QGroupBox("Settings Information")
        info_layout = QVBoxLayout(info_group)
        
        self.settings_info = QTextEdit()
        self.settings_info.setReadOnly(True)
        self.settings_info.setMaximumHeight(150)
        self.settings_info.setPlainText("Settings are stored in SQLite database with full audit trail.")
        info_layout.addWidget(self.settings_info)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Advanced")
    
    def load_settings(self):
        """Load current settings into UI"""
        # General tab
        self.simulation_mode_cb.setChecked(settings_manager.get('simulation_mode', True))
        self.demo_safe_mode_cb.setChecked(settings_manager.get('demo_safe_mode', True))
        self.auto_analyze_ocr_cb.setChecked(settings_manager.get('auto_analyze_ocr', True))
        self.debug_mode_cb.setChecked(settings_manager.get('debug_mode', False))
        self.window_width_spin.setValue(settings_manager.get('window_width', 1000))
        self.window_height_spin.setValue(settings_manager.get('window_height', 800))
        
        # Voice tab
        self.voice_input_enabled_cb.setChecked(settings_manager.get('voice_input_enabled', True))
        self.voice_output_enabled_cb.setChecked(settings_manager.get('voice_output_enabled', True))
        
        model_size = settings_manager.get('whisper_model_size', 'base')
        index = self.whisper_model_combo.findText(model_size)
        if index >= 0:
            self.whisper_model_combo.setCurrentIndex(index)
        
        self.max_recording_spin.setValue(settings_manager.get('max_recording_duration', 8))
        self.auto_send_transcript_cb.setChecked(settings_manager.get('auto_send_transcript', True))
        
        self.tts_rate_slider.setValue(int(settings_manager.get('tts_rate', 150)))
        self.tts_volume_slider.setValue(int(settings_manager.get('tts_volume', 0.8) * 100))
        
        # Advanced tab
        log_level = settings_manager.get('log_level', 'INFO')
        index = self.log_level_combo.findText(log_level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
    
    def save_settings(self):
        """Save settings and close dialog"""
        try:
            # General settings
            settings_manager.set('simulation_mode', self.simulation_mode_cb.isChecked())
            settings_manager.set('demo_safe_mode', self.demo_safe_mode_cb.isChecked())
            settings_manager.set('auto_analyze_ocr', self.auto_analyze_ocr_cb.isChecked())
            settings_manager.set('debug_mode', self.debug_mode_cb.isChecked())
            settings_manager.set('window_width', self.window_width_spin.value())
            settings_manager.set('window_height', self.window_height_spin.value())
            
            # Voice settings
            settings_manager.set('voice_input_enabled', self.voice_input_enabled_cb.isChecked())
            settings_manager.set('voice_output_enabled', self.voice_output_enabled_cb.isChecked())
            settings_manager.set('whisper_model_size', self.whisper_model_combo.currentText())
            settings_manager.set('max_recording_duration', self.max_recording_spin.value())
            settings_manager.set('auto_send_transcript', self.auto_send_transcript_cb.isChecked())
            settings_manager.set('tts_rate', self.tts_rate_slider.value())
            settings_manager.set('tts_volume', self.tts_volume_slider.value() / 100.0)
            
            # Advanced settings
            settings_manager.set('log_level', self.log_level_combo.currentText())
            
            # Emit signal that settings changed
            self.settings_changed.emit()
            
            # Show success message
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully!")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if settings_manager.reset_to_defaults():
                self.load_settings()  # Reload UI with defaults
                QMessageBox.information(self, "Settings Reset", "All settings have been reset to defaults!")
            else:
                QMessageBox.critical(self, "Error", "Failed to reset settings to defaults!")

# Convenience function to show settings dialog
def show_settings_dialog(parent=None):
    """Show the settings dialog"""
    dialog = SettingsDialog(parent)
    return dialog.exec()