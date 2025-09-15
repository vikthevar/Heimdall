#!/usr/bin/env python3
"""
Heimdall Startup Script with AI Integration
Handles setup and graceful fallbacks
"""
import sys
import os
import subprocess
from pathlib import Path

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Try to start Ollama"""
    print("🔄 Starting Ollama...")
    try:
        # Try to start Ollama in background
        if os.name == 'nt':  # Windows
            subprocess.Popen(['ollama', 'serve'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix-like
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a moment for startup
        import time
        time.sleep(3)
        
        return check_ollama()
    except Exception as e:
        print(f"❌ Failed to start Ollama: {e}")
        return False

def check_model():
    """Check if required model is available"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        return 'llama3.2:3b' in result.stdout or 'llama3.2' in result.stdout
    except:
        return False

def download_model():
    """Download required model"""
    print("📥 Downloading AI model (this may take a few minutes)...")
    try:
        result = subprocess.run(['ollama', 'pull', 'llama3.2:3b'], timeout=600)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        return False

def main():
    """Main startup function"""
    print("🏠 Starting Heimdall AI Assistant...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return 1
    
    # Check if Ollama is available
    if not check_ollama():
        print("🔄 Ollama not running, attempting to start...")
        if not start_ollama():
            print("❌ Could not start Ollama")
            print("💡 Please install Ollama: https://ollama.ai/download")
            print("   Then run: ollama serve")
            print("\n🔄 Starting in demo mode...")
        else:
            print("✅ Ollama started successfully")
    else:
        print("✅ Ollama is running")
    
    # Check if model is available
    if check_ollama() and not check_model():
        print("📥 Required AI model not found")
        if input("Download llama3.2:3b model? (y/n): ").lower().startswith('y'):
            if not download_model():
                print("❌ Model download failed")
        else:
            print("⚠️ Running without AI model (limited functionality)")
    
    # Create data directories
    os.makedirs("./data/logs", exist_ok=True)
    os.makedirs("./data/screenshots", exist_ok=True)
    
    print("\n🚀 Launching Heimdall GUI...")
    
    # Start the main application
    try:
        import heimdall_working
        return heimdall_working.main()
    except Exception as e:
        print(f"❌ Failed to start GUI: {e}")
        print("💡 Try running: python heimdall_working.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())