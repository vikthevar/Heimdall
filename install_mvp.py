#!/usr/bin/env python3
"""
Heimdall AI Assistant - MVP Installation Script
Installs all dependencies needed for the MVP demo
"""
import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Core dependencies that should work everywhere
    core_deps = [
        "PyQt6>=6.4.0",
        "Pillow>=10.0.0", 
        "numpy>=1.24.0",
        "requests>=2.31.0",
        "loguru>=0.7.0",
        "pyttsx3>=2.90",
        "pyautogui>=0.9.54"
    ]
    
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, continuing...")
    
    # AI dependencies (may take longer)
    ai_deps = [
        "openai-whisper>=20240930",
        "torch>=2.0.0",
        "opencv-python>=4.8.0"
    ]
    
    print("\n🤖 Installing AI dependencies (this may take a while)...")
    for dep in ai_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, some features may not work")
    
    # Audio dependencies (optional)
    print("\n🎤 Installing audio dependencies...")
    audio_deps = ["sounddevice>=0.4.6", "pytesseract>=0.3.10"]
    
    for dep in audio_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, audio features may not work")

def install_system_dependencies():
    """Install system dependencies based on platform"""
    system = platform.system().lower()
    
    print(f"\n🖥️ Detected system: {system}")
    
    if system == "darwin":  # macOS
        print("📋 For macOS, you may need to install:")
        print("   brew install tesseract")
        print("   brew install portaudio")
        
    elif system == "linux":
        print("📋 For Linux, you may need to install:")
        print("   sudo apt update")
        print("   sudo apt install tesseract-ocr portaudio19-dev python3-dev")
        print("   # or equivalent for your distribution")
        
    elif system == "windows":
        print("📋 For Windows:")
        print("   - Tesseract: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   - Audio should work out of the box")
    
    print("\n💡 These system dependencies are optional but recommended for full functionality")

def test_installation():
    """Test that key components can be imported"""
    print("\n🧪 Testing installation...")
    
    test_imports = [
        ("PyQt6.QtWidgets", "GUI framework"),
        ("whisper", "Speech recognition"),
        ("cv2", "Computer vision"),
        ("pyautogui", "Screen automation"),
        ("pyttsx3", "Text-to-speech"),
        ("PIL", "Image processing")
    ]
    
    success_count = 0
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description} ({module})")
            success_count += 1
        except ImportError:
            print(f"❌ {description} ({module}) - not available")
    
    print(f"\n📊 {success_count}/{len(test_imports)} components available")
    
    if success_count >= 4:
        print("🎉 Installation looks good! Ready for MVP demo.")
        return True
    else:
        print("⚠️ Some components missing. Basic functionality should still work.")
        return False

def main():
    """Main installation process"""
    print("🚀 HEIMDALL AI ASSISTANT - MVP INSTALLATION")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    install_python_dependencies()
    install_system_dependencies()
    
    # Test installation
    success = test_installation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 INSTALLATION COMPLETE!")
        print("\n🚀 Ready to run MVP demo:")
        print("   python heimdall_working.py")
    else:
        print("⚠️ INSTALLATION PARTIAL")
        print("\n🚀 You can still try running:")
        print("   python heimdall_working.py")
        print("   (Some features may show error messages)")
    
    print("\n📋 For full functionality, ensure system dependencies are installed")
    print("📖 See DEPLOYMENT_SUMMARY.md for detailed setup instructions")

if __name__ == "__main__":
    main()