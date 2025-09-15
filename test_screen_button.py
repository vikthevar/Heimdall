#!/usr/bin/env python3
"""
Test screen button clicking functionality
"""
import sys
from pathlib import Path
import time

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_screen_button_detection():
    """Test the screen button detection and clicking"""
    print("🧪 Testing Screen Button Detection")
    print("=" * 40)
    
    try:
        from core.screen_controller import find_element_by_description, _execute_click
        import pyautogui
        
        print("📸 Looking for screen button...")
        
        # Test the screen button detection
        location = find_element_by_description("screen button")
        
        if location:
            x, y = location
            print(f"✅ Found screen button at: ({x}, {y})")
            
            # Show where we found it by moving mouse there
            print("🖱️ Moving mouse to show location...")
            current_pos = pyautogui.position()
            pyautogui.moveTo(x, y, duration=1.0)
            
            # Wait a moment so user can see
            print("⏳ Pausing 2 seconds so you can see the location...")
            time.sleep(2)
            
            # Move back
            pyautogui.moveTo(current_pos.x, current_pos.y, duration=0.5)
            
            print("✅ Screen button detection test completed!")
            print(f"   Location: ({x}, {y})")
            
        else:
            print("❌ Could not find screen button")
            print("   This might be because:")
            print("   1. Heimdall window is not visible")
            print("   2. Screen button is not in expected location")
            print("   3. OCR/detection methods need adjustment")
        
        # Test the click execution
        print("\n🖱️ Testing click execution...")
        test_intent = {
            'action': 'click',
            'target': 'screen button'
        }
        
        result = _execute_click(test_intent)
        print(f"Click result: {result}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Make sure Heimdall is running in another window!")
    print("   Run: python heimdall_working.py")
    print("   Then run this test to see if screen button detection works.")
    print()
    
    input("Press Enter when Heimdall is running and visible...")
    test_screen_button_detection()