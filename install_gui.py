#!/usr/bin/env python3
"""
GUI Installation Helper for Heimdall
Automatically detects and installs the best GUI framework for your system
"""
import sys
import subprocess
import platform
import importlib


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3.8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def try_import(module_name):
    """Try to import a module"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def install_package(package_name):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package_name}...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False


def detect_and_install_gui():
    """Detect the best GUI framework and install it"""
    system = platform.system().lower()
    
    print("🔍 Detecting GUI framework compatibility...")
    
    # Check if tkinter is available (should be built-in)
    if try_import("tkinter"):
        print("✅ Tkinter is available (built-in)")
        return "tkinter"
    
    # Try PyQt5 (good compatibility)
    if try_import("PyQt5"):
        print("✅ PyQt5 is already installed")
        return "pyqt5"
    
    # Try PyQt6 (latest features)
    if try_import("PyQt6"):
        print("✅ PyQt6 is already installed")
        return "pyqt6"
    
    # Try to install PyQt5 (most compatible)
    print("📦 Attempting to install PyQt5...")
    if install_package("PyQt5>=5.15.0"):
        if try_import("PyQt5"):
            print("✅ PyQt5 installed successfully")
            return "pyqt5"
    
    # Try to install PyQt6
    print("📦 Attempting to install PyQt6...")
    if install_package("PyQt6>=6.4.0"):
        if try_import("PyQt6"):
            print("✅ PyQt6 installed successfully")
            return "pyqt6"
    
    # Fallback to tkinter
    print("⚠️  Could not install PyQt. Using Tkinter fallback.")
    return "tkinter"


def install_minimal_dependencies():
    """Install minimal dependencies for GUI"""
    minimal_deps = [
        "python-dotenv",
        "loguru",
        "Pillow",
        "requests",
        "aiosqlite"
    ]
    
    print("📦 Installing minimal dependencies...")
    
    for dep in minimal_deps:
        if not install_package(dep):
            print(f"⚠️  Could not install {dep}, continuing anyway...")
    
    print("✅ Minimal dependencies installation complete")


def create_gui_launcher():
    """Create appropriate GUI launcher based on available framework"""
    gui_framework = detect_and_install_gui()
    
    launcher_content = f'''#!/usr/bin/env python3
"""
Auto-generated GUI launcher for Heimdall
Framework: {gui_framework}
"""
import sys
import os
from pathlib import Path

def main():
    """Launch appropriate GUI"""
    print("🏠 Starting Heimdall GUI...")
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        if "{gui_framework}" == "tkinter":
            print("🖥️  Using Tkinter GUI (maximum compatibility)")
            from ui.tkinter_gui import main as gui_main
            return gui_main()
        elif "{gui_framework}" == "pyqt5":
            print("🖥️  Using PyQt5 GUI")
            # Import PyQt5 version when available
            from ui.tkinter_gui import main as gui_main  # Fallback for now
            return gui_main()
        elif "{gui_framework}" == "pyqt6":
            print("🖥️  Using PyQt6 GUI")
            from ui.gui_main import main as gui_main
            return gui_main()
        else:
            print("🖥️  Using simple fallback GUI")
            from main_simple import main as simple_main
            return simple_main()
    
    except ImportError as e:
        print(f"❌ Import error: {{e}}")
        print("🔄 Falling back to simple GUI...")
        try:
            from main_simple import main as simple_main
            return simple_main()
        except Exception as e2:
            print(f"❌ Fallback failed: {{e2}}")
            return 1
    
    except Exception as e:
        print(f"❌ GUI error: {{e}}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open("heimdall_gui.py", "w") as f:
        f.write(launcher_content)
    
    print("✅ Created heimdall_gui.py launcher")
    return gui_framework


def main():
    """Main installation function"""
    print("🏠 Heimdall GUI Installation Helper")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install minimal dependencies
    install_minimal_dependencies()
    
    # Detect and install GUI framework
    gui_framework = create_gui_launcher()
    
    print("\n🎉 Installation complete!")
    print(f"📱 GUI Framework: {gui_framework}")
    print("\n📋 Next steps:")
    print("1. Run the GUI: python heimdall_gui.py")
    print("2. For full AI features, install Ollama:")
    print("   - Visit: https://ollama.ai/")
    print("   - Run: ollama serve")
    print("   - Run: ollama pull llama3.2:3b")
    print("3. Install additional dependencies if needed:")
    print("   - pip install -r requirements-minimal.txt")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())