"""
Tkinter-based GUI for Heimdall (Maximum Compatibility)
Uses built-in Python GUI framework for universal compatibility
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
from datetime import datetime
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.voice_handler import VoiceHandler
    from core.voice_output import VoiceOutput
    from core.intent_parser import IntentParser
    from core.screenshot_capturer import ScreenshotCapturer
    from core.screen_analyzer import ScreenAnalyzer
    from core.screen_controller import ScreenController
    from storage.database import LocalDatabase
    from utils.config import get_config
except ImportError as e:
    print(f"Import error: {e}")
    print("Running in demo mode without AI functionality")


class ModernStyle:
    """Modern styling for Tkinter"""
    
    # Color palette
    PRIMARY = "#667eea"
    SECONDARY = "#764ba2"
    BACKGROUND = "#ffffff"
    SURFACE = "#f8f9fa"
    TEXT_PRIMARY = "#212529"
    TEXT_SECONDARY = "#6c757d"
    SUCCESS = "#28a745"
    WARNING = "#ffc107"
    ERROR = "#dc3545"
    
    @staticmethod
    def configure_style():
        """Configure ttk styles"""
        style = ttk.Style()
        
        # Configure button styles
        style.configure(
            "Primary.TButton",
            background=ModernStyle.PRIMARY,
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            padding=(20, 10)
        )
        
        style.map(
            "Primary.TButton",
            background=[("active", "#5a6fd8"), ("pressed", "#4e5bc6")]
        )
        
        # Configure frame styles
        style.configure(
            "Card.TFrame",
            background=ModernStyle.SURFACE,
            relief="flat",
            borderwidth=1
        )
        
        return style


class ChatMessage:
    """Represents a chat message"""
    
    def __init__(self, text, is_user=True, timestamp=None):
        self.text = text
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()


class StatusIndicator:
    """Simple status indicator"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.status_var = tk.StringVar(value="● Ready")
        self.status_label = ttk.Label(
            self.frame, 
            textvariable=self.status_var,
            foreground=ModernStyle.SUCCESS
        )
        self.status_label.pack()
    
    def update_status(self, status):
        """Update status display"""
        status_colors = {
            "idle": ModernStyle.SUCCESS,
            "listening": ModernStyle.PRIMARY,
            "processing": ModernStyle.WARNING,
            "speaking": ModernStyle.SUCCESS,
            "error": ModernStyle.ERROR
        }
        
        status_text = {
            "idle": "● Ready",
            "listening": "● Listening...",
            "processing": "● Processing...",
            "speaking": "● Speaking...",
            "error": "● Error"
        }
        
        self.status_var.set(status_text.get(status, "● Ready"))
        self.status_label.configure(foreground=status_colors.get(status, ModernStyle.SUCCESS))


class HeimdallTkinterGUI:
    """Main Tkinter GUI application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.messages = []
        self.ai_components = None
        self.ai_thread = None
        
        self.setup_window()
        self.create_widgets()
        self.setup_ai_components()
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("Heimdall AI Assistant")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure colors
        self.root.configure(bg=ModernStyle.BACKGROUND)
        
        # Configure styles
        self.style = ModernStyle.configure_style()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Chat area
        self.create_chat_area(main_frame)
        
        # Input area
        self.create_input_area(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create header with title and controls"""
        header_frame = ttk.Frame(parent, style="Card.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="Heimdall AI Assistant",
            font=("Segoe UI", 18, "bold"),
            foreground=ModernStyle.PRIMARY
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Controls frame
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Voice button
        self.voice_btn = ttk.Button(
            controls_frame,
            text="🎤 Voice",
            command=self.toggle_voice,
            style="Primary.TButton"
        )
        self.voice_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Settings button
        settings_btn = ttk.Button(
            controls_frame,
            text="⚙️ Settings",
            command=self.show_settings
        )
        settings_btn.pack(side=tk.RIGHT)
    
    def create_chat_area(self, parent):
        """Create chat display area"""
        chat_frame = ttk.Frame(parent, style="Card.TFrame")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg=ModernStyle.BACKGROUND,
            fg=ModernStyle.TEXT_PRIMARY,
            borderwidth=0,
            highlightthickness=0,
            padx=20,
            pady=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags for styling
        self.chat_display.tag_configure(
            "user_message",
            background=ModernStyle.PRIMARY,
            foreground="white",
            spacing1=10,
            spacing3=10,
            lmargin1=100,
            rmargin=20
        )
        
        self.chat_display.tag_configure(
            "ai_message",
            background=ModernStyle.SURFACE,
            foreground=ModernStyle.TEXT_PRIMARY,
            spacing1=10,
            spacing3=10,
            lmargin1=20,
            rmargin=100
        )
        
        self.chat_display.tag_configure(
            "timestamp",
            foreground=ModernStyle.TEXT_SECONDARY,
            font=("Segoe UI", 9)
        )
        
        # Add welcome message
        self.add_message(
            "Hello! I'm Heimdall, your AI assistant. I can help you navigate your screen, "
            "control applications, and answer questions. Try typing a command or click the voice button!",
            is_user=False
        )
    
    def create_input_area(self, parent):
        """Create message input area"""
        input_frame = ttk.Frame(parent, style="Card.TFrame")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input container
        input_container = ttk.Frame(input_frame)
        input_container.pack(fill=tk.X, padx=20, pady=15)
        
        # Message entry
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(
            input_container,
            textvariable=self.message_var,
            font=("Segoe UI", 12),
            width=50
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        # Send button
        send_btn = ttk.Button(
            input_container,
            text="Send",
            command=self.send_message,
            style="Primary.TButton"
        )
        send_btn.pack(side=tk.RIGHT)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        # Status indicator
        self.status_indicator = StatusIndicator(status_frame)
        self.status_indicator.frame.pack(side=tk.LEFT)
        
        # Version info
        version_label = ttk.Label(
            status_frame,
            text="Heimdall v1.0 - Free AI Assistant",
            foreground=ModernStyle.TEXT_SECONDARY,
            font=("Segoe UI", 9)
        )
        version_label.pack(side=tk.RIGHT)
    
    def add_message(self, text, is_user=True):
        """Add a message to the chat display"""
        message = ChatMessage(text, is_user)
        self.messages.append(message)
        
        # Format timestamp
        timestamp = message.timestamp.strftime("%H:%M")
        
        # Insert message
        self.chat_display.configure(state=tk.NORMAL)
        
        if is_user:
            self.chat_display.insert(tk.END, f"\nYou ({timestamp}):\n", "timestamp")
            self.chat_display.insert(tk.END, f"{text}\n", "user_message")
        else:
            self.chat_display.insert(tk.END, f"\nHeimdall ({timestamp}):\n", "timestamp")
            self.chat_display.insert(tk.END, f"{text}\n", "ai_message")
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """Send a message"""
        text = self.message_var.get().strip()
        if not text:
            return
        
        # Add user message
        self.add_message(text, is_user=True)
        self.message_var.set("")
        
        # Process message
        self.process_message(text)
    
    def process_message(self, text):
        """Process user message"""
        self.status_indicator.update_status("processing")
        
        # Simple responses for demo mode
        if not self.ai_components:
            self.handle_demo_response(text)
            return
        
        # Process with AI in background thread
        threading.Thread(
            target=self.process_with_ai,
            args=(text,),
            daemon=True
        ).start()
    
    def handle_demo_response(self, text):
        """Handle responses in demo mode"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["hello", "hi", "hey"]):
            response = "Hello! I'm running in demo mode. Install the AI components to unlock full functionality."
        elif "help" in text_lower:
            response = ("I can help you with:\n"
                       "• Screen reading and analysis\n"
                       "• Clicking and navigation\n"
                       "• Voice commands\n"
                       "• Text input automation\n\n"
                       "Install the full AI components for complete functionality!")
        elif any(word in text_lower for word in ["click", "scroll", "type"]):
            response = "I understand you want to control the screen. Please install the AI components for full functionality."
        elif "read" in text_lower:
            response = "I can read screen content when the AI components are installed."
        else:
            response = "I'm running in demo mode. Install the AI components to process your commands!"
        
        # Simulate processing delay
        self.root.after(1000, lambda: self.add_ai_response(response))
    
    def process_with_ai(self, text):
        """Process message with AI components"""
        try:
            # This would contain the actual AI processing
            # For now, just a placeholder
            response = "AI processing is not yet implemented in this version."
            
            # Update UI in main thread
            self.root.after(0, lambda: self.add_ai_response(response))
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.root.after(0, lambda: self.add_ai_response(error_msg))
    
    def add_ai_response(self, response):
        """Add AI response to chat"""
        self.add_message(response, is_user=False)
        self.status_indicator.update_status("idle")
    
    def toggle_voice(self):
        """Toggle voice input"""
        self.status_indicator.update_status("listening")
        
        # Simulate voice input
        self.root.after(2000, lambda: self.add_ai_response(
            "Voice input is not yet implemented. Please type your message instead."
        ))
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=ModernStyle.BACKGROUND)
        
        # Settings content
        ttk.Label(
            settings_window,
            text="Heimdall Settings",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=20)
        
        ttk.Label(
            settings_window,
            text="Settings panel coming soon...",
            foreground=ModernStyle.TEXT_SECONDARY
        ).pack(pady=10)
        
        ttk.Button(
            settings_window,
            text="Close",
            command=settings_window.destroy
        ).pack(pady=20)
    
    def setup_ai_components(self):
        """Setup AI components if available"""
        try:
            # Try to initialize AI components
            # This is a placeholder for now
            self.ai_components = None
            print("AI components not yet integrated with Tkinter GUI")
        except Exception as e:
            print(f"Could not initialize AI components: {e}")
            self.ai_components = None
    
    def run(self):
        """Run the GUI application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application interrupted")
        finally:
            if self.ai_thread:
                # Clean up AI thread
                pass


def main():
    """Main entry point"""
    print("Starting Heimdall Tkinter GUI...")
    
    try:
        app = HeimdallTkinterGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())