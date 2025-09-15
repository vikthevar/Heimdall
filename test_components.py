#!/usr/bin/env python3
"""
Test all Heimdall components step by step
"""
import sys
import time
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_whisper():
    """Test OpenAI Whisper"""
    print("🎤 Testing Whisper...")
    try:
        import whisper
        model = whisper.load_model('base')
        print("✅ Whisper model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Whisper failed: {e}")
        return False

def test_pyautogui():
    """Test PyAutoGUI screen control"""
    print("🖱️ Testing PyAutoGUI...")
    try:
        import pyautogui
        pyautogui.FAILSAFE = True
        screen_size = pyautogui.size()
        print(f"✅ PyAutoGUI working - Screen: {screen_size}")
        
        # Test safe mouse movement (just get current position)
        current_pos = pyautogui.position()
        print(f"✅ Current mouse position: {current_pos}")
        return True
    except Exception as e:
        print(f"❌ PyAutoGUI failed: {e}")
        return False

def test_pyttsx3():
    """Test pyttsx3 text-to-speech"""
    print("🔊 Testing pyttsx3...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voice_count = len(voices) if voices else 0
        print(f"✅ pyttsx3 working - {voice_count} voices available")
        
        # Test speech (without actually speaking to avoid noise)
        engine.setProperty('rate', 200)
        engine.setProperty('volume', 0.5)
        print("✅ Voice properties set successfully")
        return True
    except Exception as e:
        print(f"❌ pyttsx3 failed: {e}")
        return False

def test_heimdall_components():
    """Test Heimdall AI components"""
    print("🧠 Testing Heimdall AI components...")
    
    # Test AI Brain
    try:
        from ai.heimdall_brain import HeimdallBrain
        print("✅ HeimdallBrain import successful")
    except Exception as e:
        print(f"❌ HeimdallBrain import failed: {e}")
    
    # Test Voice Handler
    try:
        from core.voice_handler import VoiceHandler
        print("✅ VoiceHandler import successful")
    except Exception as e:
        print(f"❌ VoiceHandler import failed: {e}")
    
    # Test Screen Analyzer
    try:
        from core.screen_analyzer import ScreenAnalyzer
        print("✅ ScreenAnalyzer import successful")
    except Exception as e:
        print(f"❌ ScreenAnalyzer import failed: {e}")
    
    # Test Screen Controller
    try:
        from core.screen_controller import execute_screen_command
        print("✅ ScreenController import successful")
    except ImportError:
        try:
            # Try alternative import
            import core.screen_controller
            print("✅ ScreenController module import successful")
        except Exception as e:
            print(f"❌ ScreenController import failed: {e}")

def test_gui():
    """Test GUI components"""
    print("🖥️ Testing GUI...")
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Create minimal app to test
        app = QApplication(sys.argv)
        print("✅ PyQt6 application created")
        
        # Test if our main GUI can be imported
        import heimdall_working
        print("✅ Heimdall GUI module imported")
        
        app.quit()
        return True
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def main():
    """Run all component tests"""
    print("🧪 HEIMDALL COMPONENT TESTING")
    print("=" * 50)
    
    results = []
    
    # Test each component
    results.append(("Whisper", test_whisper()))
    results.append(("PyAutoGUI", test_pyautogui()))
    results.append(("pyttsx3", test_pyttsx3()))
    results.append(("GUI", test_gui()))
    
    print("\n🧠 Testing Heimdall Components...")
    test_heimdall_components()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for component, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{component:15} {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} core components working")
    
    if passed == len(results):
        print("🎉 All components ready! Heimdall should work perfectly.")
    else:
        print("⚠️ Some components failed. Check error messages above.")
    
    print("\n🚀 Ready to run: python heimdall_working.py")

if __name__ == "__main__":
    main()