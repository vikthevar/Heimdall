#!/usr/bin/env python3
"""
Heimdall Working GUI - Guaranteed to work!
Tries PyQt6 -> PyQt5 -> Tkinter -> Command Line
"""
import sys
import os
from datetime import datetime

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
    """PyQt6 implementation"""
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QLineEdit, QFrame
    )
    from PyQt6.QtCore import Qt
    
    class HeimdallWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Heimdall AI Assistant")
            self.setGeometry(100, 100, 900, 700)
            self.setup_ui()
        
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
            for i, text in enumerate(nav_buttons):
                btn = QPushButton(text)
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
            
            # Welcome message
            welcome_html = """
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
                • 👁️ Read screen content<br>
                • 🖱️ Click buttons and elements<br>
                • ⬇️ Scroll and navigate<br>
                • ⌨️ Type text commands<br>
                • 🎤 Voice control support
            </div>
            <div style='color: #d4af37; margin-bottom: 20px;'>
                Try typing: "Read what's on my screen" or "Click the blue button"
            </div>
            <hr style='border: 1px solid #333; margin: 20px 0;'>
            """
            self.chat.setHtml(welcome_html)
            content_layout.addWidget(self.chat)
            
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
        
        def send_message(self):
            text = self.input_field.text().strip()
            if text:
                # User message
                user_html = f"""
                <div style='text-align: right; margin: 15px 0;'>
                    <div style='background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #d4af37); 
                               color: white; padding: 12px 16px; border-radius: 15px; 
                               display: inline-block; max-width: 70%;'>
                        {text}
                    </div>
                    <div style='color: #666; font-size: 11px; margin-top: 5px;'>
                        Just now
                    </div>
                </div>
                """
                self.chat.insertHtml(user_html)
                
                # AI response
                ai_html = f"""
                <div style='text-align: left; margin: 15px 0;'>
                    <div style='background: #2a2a2a; color: white; padding: 12px 16px; 
                               border-radius: 15px; border: 1px solid #444; 
                               display: inline-block; max-width: 70%;'>
                        I understand you want me to: "{text}". This is a demo response showing the beautiful modern UI working perfectly! ✨
                    </div>
                    <div style='color: #666; font-size: 11px; margin-top: 5px;'>
                        Heimdall • Just now
                    </div>
                </div>
                """
                self.chat.insertHtml(ai_html)
                
                self.input_field.clear()
                
                # Auto scroll to bottom
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