#!/usr/bin/env python3
"""
Test script to verify AI integration works
"""
import sys
import os
import asyncio
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def test_ai_brain():
    """Test the AI brain functionality"""
    print("🧠 Testing Heimdall AI Brain...")
    
    try:
        from ai.heimdall_brain import HeimdallBrain
        print("✅ AI Brain imported successfully")
        
        # Initialize
        brain = HeimdallBrain()
        success = await brain.initialize()
        
        if success:
            print("✅ AI Brain initialized successfully")
            
            # Test basic message processing
            result = await brain.process_message("Hello, can you help me?")
            print(f"✅ Message processed: {result['reply'][:100]}...")
            
            # Test automation command
            result = await brain.process_message("Click the submit button")
            print(f"✅ Automation command processed: {result['reply'][:100]}...")
            
            print("🎉 All AI tests passed!")
            return True
            
        else:
            print("❌ AI Brain initialization failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_gui_import():
    """Test GUI imports"""
    print("🖥️ Testing GUI imports...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 available")
        return True
    except ImportError:
        try:
            from PyQt5.QtWidgets import QApplication
            print("✅ PyQt5 available")
            return True
        except ImportError:
            try:
                import tkinter
                print("✅ Tkinter available")
                return True
            except ImportError:
                print("❌ No GUI libraries available")
                return False

async def main():
    """Main test function"""
    print("🔍 Testing Heimdall AI Integration")
    print("=" * 50)
    
    # Test GUI imports
    gui_ok = test_gui_import()
    
    # Test AI brain
    ai_ok = await test_ai_brain()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"GUI Libraries: {'✅ OK' if gui_ok else '❌ FAIL'}")
    print(f"AI Backend: {'✅ OK' if ai_ok else '❌ FAIL'}")
    
    if gui_ok and ai_ok:
        print("\n🎉 Integration ready! You can now run:")
        print("   python heimdall_working.py")
    else:
        print("\n🔧 Setup needed. Please check the installation guide.")
    
    return 0 if (gui_ok and ai_ok) else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))