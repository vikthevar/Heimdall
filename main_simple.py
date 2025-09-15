#!/usr/bin/env python3
"""
Simple Heimdall GUI - Maximum Compatibility Version
Uses Tkinter (built into Python) for universal compatibility
"""
import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point for simple GUI"""
    print("🏠 Starting Heimdall Simple GUI...")
    
    try:
        from ui.tkinter_gui import main as tkinter_main
        return tkinter_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Trying fallback GUI...")
        return run_fallback_gui()
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        return 1

def run_fallback_gui():
    """Fallback GUI using basic tkinter"""
    try:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext
        
        root = tk.Tk()
        root.title("Heimdall AI Assistant (Simple Mode)")
        root.geometry("600x400")
        
        # Header
        header = tk.Label(
            root, 
            text="Heimdall AI Assistant", 
            font=("Arial", 16, "bold"),
            bg="#667eea",
            fg="white",
            pady=10
        )
        header.pack(fill=tk.X)
        
        # Chat area
        chat_frame = tk.Frame(root)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Add welcome message
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, "Welcome to Heimdall AI Assistant!\n\n")
        chat_display.insert(tk.END, "This is the simple compatibility mode.\n")
        chat_display.insert(tk.END, "To unlock full AI features:\n")
        chat_display.insert(tk.END, "1. Install dependencies: pip install -r requirements-minimal.txt\n")
        chat_display.insert(tk.END, "2. Set up Ollama: ollama serve && ollama pull llama3.2:3b\n")
        chat_display.insert(tk.END, "3. Run: python main.py\n\n")
        chat_display.config(state=tk.DISABLED)
        
        # Input area
        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        entry_var = tk.StringVar()
        entry = tk.Entry(input_frame, textvariable=entry_var, font=("Arial", 10))
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def send_message():
            text = entry_var.get().strip()
            if text:
                chat_display.config(state=tk.NORMAL)
                chat_display.insert(tk.END, f"You: {text}\n")
                chat_display.insert(tk.END, "Heimdall: Please install the full version for AI responses.\n\n")
                chat_display.config(state=tk.DISABLED)
                chat_display.see(tk.END)
                entry_var.set("")
        
        entry.bind("<Return>", lambda e: send_message())
        
        send_btn = tk.Button(
            input_frame,
            text="Send",
            command=send_message,
            bg="#667eea",
            fg="white",
            font=("Arial", 10)
        )
        send_btn.pack(side=tk.RIGHT)
        
        # Status bar
        status_bar = tk.Label(
            root,
            text="Status: Simple Mode - Install dependencies for full functionality",
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 8)
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        print("✅ Simple GUI started successfully!")
        print("💡 This is a basic version. Install dependencies for full features.")
        
        root.mainloop()
        return 0
        
    except Exception as e:
        print(f"❌ Even fallback GUI failed: {e}")
        print("💡 Please check your Python installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())