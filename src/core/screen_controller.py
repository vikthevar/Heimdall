#!/usr/bin/env python3
"""
Screen Controller - AI-Powered UI Automation and Control
Executes automation actions on the screen with intelligent element detection
"""
import pyautogui
import time
import logging
import cv2
import numpy as np
from PIL import Image, ImageGrab
import pytesseract
import re
import platform
from typing import Dict, Any, Optional, Tuple, List
import subprocess

logger = logging.getLogger(__name__)

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Window management imports based on platform
if platform.system() == "Windows":
    try:
        import win32gui
        import win32con
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
elif platform.system() == "Darwin":  # macOS
    try:
        import Quartz
        MACOS_AVAILABLE = True
    except ImportError:
        MACOS_AVAILABLE = False
else:  # Linux
    LINUX_AVAILABLE = True

def execute_intent(intent: Dict[str, Any]) -> str:
    """
    Execute automation intent on the screen with AI-powered element detection
    
    Args:
        intent: Intent dictionary with action details
        
    Returns:
        Result message describing what was executed
    """
    try:
        action = intent.get('action', '').lower()
        
        if action == 'click':
            return _execute_click(intent)
        elif action == 'scroll':
            return _execute_scroll(intent)
        elif action == 'type':
            return _execute_type(intent)
        elif action == 'key':
            return _execute_key(intent)
        elif action == 'minimize':
            return _execute_minimize(intent)
        elif action == 'close':
            return _execute_close(intent)
        elif action == 'maximize':
            return _execute_maximize(intent)
        else:
            return f"❌ Unknown action: {action}"
    
    except Exception as e:
        logger.error(f"Failed to execute intent: {e}")
        return f"❌ Execution failed: {str(e)}"

def render_plan(intent: Dict[str, Any]) -> str:
    """
    Render execution plan for an intent without executing
    
    Args:
        intent: Intent dictionary with action details
        
    Returns:
        Human-readable execution plan
    """
    try:
        action = intent.get('action', '').lower()
        
        if action == 'click':
            target = intent.get('target', 'element')
            coordinates = intent.get('coordinates')
            if coordinates:
                return f"1. Move mouse to coordinates ({coordinates[0]}, {coordinates[1]})\n2. Click {target}"
            else:
                return f"1. Search for '{target}' on screen\n2. Move mouse to {target}\n3. Click {target}"
        
        elif action == 'scroll':
            direction = intent.get('direction', 'down')
            amount = intent.get('amount', 3)
            return f"1. Scroll {direction} by {amount} units\n2. Wait for page to settle"
        
        elif action == 'type':
            text = intent.get('text', '')
            return f"1. Focus on active input field\n2. Type: '{text}'\n3. Confirm text entry"
        
        elif action == 'key':
            key = intent.get('key', '')
            return f"1. Press key: {key}\n2. Wait for system response"
        
        else:
            return f"Unknown action plan for: {action}"
    
    except Exception as e:
        return f"❌ Failed to render plan: {str(e)}"

def _execute_click(intent: Dict[str, Any]) -> str:
    """Execute click action with AI-powered element detection"""
    try:
        target = intent.get('target', 'element')
        coordinates = intent.get('coordinates')
        
        if coordinates:
            # Direct coordinate click
            x, y = coordinates
            pyautogui.click(x, y)
            return f"✅ Clicked at coordinates ({x}, {y})"
        else:
            # Use AI to find the element
            element_location = find_element_by_description(target)
            
            if element_location:
                x, y = element_location
                pyautogui.click(x, y)
                return f"✅ Found and clicked '{target}' at ({x}, {y})"
            else:
                return f"❌ Could not find '{target}' on screen"
    
    except Exception as e:
        return f"❌ Click failed: {str(e)}"

def _execute_scroll(intent: Dict[str, Any]) -> str:
    """Execute scroll action"""
    try:
        direction = intent.get('direction', 'down')
        amount = intent.get('amount', 3)
        
        if direction.lower() == 'up':
            pyautogui.scroll(amount)
        else:
            pyautogui.scroll(-amount)
        
        return f"✅ Scrolled {direction} by {amount} units"
    
    except Exception as e:
        return f"❌ Scroll failed: {str(e)}"

def _execute_type(intent: Dict[str, Any]) -> str:
    """Execute typing action"""
    try:
        text = intent.get('text', '')
        
        if not text:
            return "❌ No text specified to type"
        
        # Add small delay for safety
        time.sleep(0.5)
        pyautogui.typewrite(text, interval=0.05)
        
        return f"✅ Typed: '{text}'"
    
    except Exception as e:
        return f"❌ Typing failed: {str(e)}"

def _execute_key(intent: Dict[str, Any]) -> str:
    """Execute key press action"""
    try:
        key = intent.get('key', '')
        
        if not key:
            return "❌ No key specified to press"
        
        pyautogui.press(key)
        
        return f"✅ Pressed key: {key}"
    
    except Exception as e:
        return f"❌ Key press failed: {str(e)}"

# Utility functions for screen interaction
def get_screen_size() -> Tuple[int, int]:
    """Get screen dimensions"""
    return pyautogui.size()

def take_screenshot(filename: Optional[str] = None) -> str:
    """Take a screenshot"""
    try:
        if filename:
            screenshot = pyautogui.screenshot(filename)
            return f"✅ Screenshot saved to {filename}"
        else:
            screenshot = pyautogui.screenshot()
            return "✅ Screenshot taken"
    except Exception as e:
        return f"❌ Screenshot failed: {str(e)}"

def move_mouse(x: int, y: int) -> str:
    """Move mouse to coordinates"""
    try:
        pyautogui.moveTo(x, y)
        return f"✅ Mouse moved to ({x}, {y})"
    except Exception as e:
        return f"❌ Mouse move failed: {str(e)}"

def find_element_by_description(description: str) -> Optional[Tuple[int, int]]:
    """
    Find UI element by description using AI-powered screen analysis
    
    Args:
        description: Natural language description of element (e.g., "close button", "submit button")
        
    Returns:
        Tuple of (x, y) coordinates if found, None otherwise
    """
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        
        # Convert to OpenCV format
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Look for common UI patterns based on description
        description_lower = description.lower()
        
        # Handle window control buttons (close, minimize, maximize)
        if any(word in description_lower for word in ['close', 'x button', 'exit']):
            return find_close_button(screenshot_cv)
        elif any(word in description_lower for word in ['minimize', 'minimize button']):
            return find_minimize_button(screenshot_cv)
        elif any(word in description_lower for word in ['maximize', 'maximize button']):
            return find_maximize_button(screenshot_cv)
        
        # Handle text-based elements
        elif any(word in description_lower for word in ['button', 'submit', 'ok', 'cancel', 'save']):
            return find_button_by_text(screenshot_cv, description)
        
        # Handle links
        elif 'link' in description_lower:
            return find_link_by_text(screenshot_cv, description)
        
        # Generic text search
        else:
            return find_text_element(screenshot_cv, description)
    
    except Exception as e:
        logger.error(f"Element detection failed: {e}")
        return None

def find_close_button(screenshot_cv: np.ndarray) -> Optional[Tuple[int, int]]:
    """Find the close button (X) in the top-right corner of windows"""
    try:
        height, width = screenshot_cv.shape[:2]
        
        # Search in top-right area (typical close button location)
        search_area = screenshot_cv[0:100, width-150:width]
        
        # Convert to grayscale for template matching
        gray = cv2.cvtColor(search_area, cv2.COLOR_BGR2GRAY)
        
        # Look for X-shaped patterns or red circular buttons
        # Method 1: Look for red circular close buttons (common on macOS/modern apps)
        hsv = cv2.cvtColor(search_area, cv2.COLOR_BGR2HSV)
        red_mask = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
        
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 500:  # Reasonable size for close button
                x, y, w, h = cv2.boundingRect(contour)
                # Return coordinates relative to full screen
                return (width - 150 + x + w//2, y + h//2)
        
        # Method 2: Look for X text patterns
        try:
            # Use OCR to find X or × symbols
            ocr_data = pytesseract.image_to_data(search_area, output_type=pytesseract.Output.DICT)
            for i, text in enumerate(ocr_data['text']):
                if text.strip() in ['X', '×', '✕']:
                    x = ocr_data['left'][i] + ocr_data['width'][i] // 2
                    y = ocr_data['top'][i] + ocr_data['height'][i] // 2
                    return (width - 150 + x, y)
        except:
            pass
        
        # Method 3: Default to top-right corner (common close button location)
        return (width - 20, 20)
    
    except Exception as e:
        logger.error(f"Close button detection failed: {e}")
        return None

def find_minimize_button(screenshot_cv: np.ndarray) -> Optional[Tuple[int, int]]:
    """Find the minimize button (usually left of close button)"""
    try:
        close_pos = find_close_button(screenshot_cv)
        if close_pos:
            # Minimize button is typically 30-40 pixels left of close button
            return (close_pos[0] - 35, close_pos[1])
        
        # Fallback: top-right area, left of close
        height, width = screenshot_cv.shape[:2]
        return (width - 55, 20)
    
    except Exception as e:
        logger.error(f"Minimize button detection failed: {e}")
        return None

def find_maximize_button(screenshot_cv: np.ndarray) -> Optional[Tuple[int, int]]:
    """Find the maximize button (usually between minimize and close)"""
    try:
        close_pos = find_close_button(screenshot_cv)
        if close_pos:
            # Maximize button is typically between minimize and close
            return (close_pos[0] - 70, close_pos[1])
        
        # Fallback: top-right area, left of minimize
        height, width = screenshot_cv.shape[:2]
        return (width - 90, 20)
    
    except Exception as e:
        logger.error(f"Maximize button detection failed: {e}")
        return None

def find_button_by_text(screenshot_cv: np.ndarray, description: str) -> Optional[Tuple[int, int]]:
    """Find button by text content using OCR"""
    try:
        # Extract key words from description
        key_words = extract_key_words(description)
        
        # Use OCR to find text
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        ocr_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        best_match = None
        best_score = 0
        
        for i, text in enumerate(ocr_data['text']):
            if text.strip():
                # Calculate similarity score
                score = calculate_text_similarity(text.lower(), key_words)
                if score > best_score and score > 0.3:  # Minimum similarity threshold
                    best_score = score
                    x = ocr_data['left'][i] + ocr_data['width'][i] // 2
                    y = ocr_data['top'][i] + ocr_data['height'][i] // 2
                    best_match = (x, y)
        
        return best_match
    
    except Exception as e:
        logger.error(f"Button text detection failed: {e}")
        return None

def find_link_by_text(screenshot_cv: np.ndarray, description: str) -> Optional[Tuple[int, int]]:
    """Find link by text content (similar to button but may look for underlined text)"""
    return find_button_by_text(screenshot_cv, description)

def find_text_element(screenshot_cv: np.ndarray, description: str) -> Optional[Tuple[int, int]]:
    """Find any text element by description"""
    return find_button_by_text(screenshot_cv, description)

def extract_key_words(description: str) -> List[str]:
    """Extract key words from description for matching"""
    # Remove common words and extract meaningful terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'button', 'link'}
    words = re.findall(r'\w+', description.lower())
    return [word for word in words if word not in stop_words and len(word) > 2]

def calculate_text_similarity(text: str, key_words: List[str]) -> float:
    """Calculate similarity between text and key words"""
    if not key_words:
        return 0.0
    
    matches = 0
    for word in key_words:
        if word in text or any(word in text_word for text_word in text.split()):
            matches += 1
    
    return matches / len(key_words)

def _execute_minimize(intent: Dict[str, Any]) -> str:
    """Execute window minimize action with window selection"""
    try:
        window_title = intent.get('window', 'current')
        
        # Handle Heimdall-specific commands
        if window_title in ['heimdall', 'this', 'this app']:
            # Minimize Heimdall itself
            pyautogui.hotkey('alt', 'f9')  # Safe minimize shortcut
            return f"✅ Minimized Heimdall AI Assistant"
        
        # Get list of available windows
        available_windows = get_window_list()
        
        if window_title == 'current':
            window_titles = [w.get('title', 'Unknown') for w in available_windows[:5]]
            return f"🔍 Available windows to minimize:\n" + "\n".join([f"• {w}" for w in window_titles]) + f"\n\nPlease specify which window to minimize (e.g., 'minimize notepad')"
        else:
            # Try to minimize specific window
            result = minimize_window_by_title(window_title)
            if result and not result.startswith("❌"):
                return result
            else:
                window_titles = [w.get('title', 'Unknown') for w in available_windows[:5]]
                return f"❌ Could not find window: {window_title}\n\nAvailable windows:\n" + "\n".join([f"• {w}" for w in window_titles])
    
    except Exception as e:
        return f"❌ Minimize failed: {str(e)}"

def _execute_close(intent: Dict[str, Any]) -> str:
    """Execute window close action with safety checks"""
    try:
        window_title = intent.get('window', 'current')
        
        # Safety check: Don't close Heimdall or Kiro
        if window_title in ['current', 'this', 'heimdall', 'kiro']:
            return f"🛡️ Safety check: Cannot close Heimdall AI Assistant. Use the X button if you really want to exit."
        
        # Get list of available windows for user to choose from
        available_windows = get_window_list()
        
        if window_title == 'current':
            window_titles = [w.get('title', 'Unknown') for w in available_windows[:5]]
            return f"🔍 Available windows to close:\n" + "\n".join([f"• {w}" for w in window_titles]) + f"\n\nPlease specify which window to close (e.g., 'close notepad')"
        else:
            # Try to close specific window
            result = close_window_by_title(window_title)
            if result and not result.startswith("❌"):
                return result
            else:
                window_titles = [w.get('title', 'Unknown') for w in available_windows[:5]]
                return f"❌ Could not find window: {window_title}\n\nAvailable windows:\n" + "\n".join([f"• {w}" for w in window_titles])
    
    except Exception as e:
        return f"❌ Close failed: {str(e)}"

def _execute_maximize(intent: Dict[str, Any]) -> str:
    """Execute window maximize action with window selection"""
    try:
        window_title = intent.get('window', 'current')
        
        # Handle Heimdall-specific commands
        if window_title in ['heimdall', 'this', 'this app']:
            # Maximize Heimdall itself
            pyautogui.hotkey('win', 'up')  # Windows maximize shortcut
            return f"✅ Maximized Heimdall AI Assistant"
        
        # Get list of available windows
        available_windows = get_window_list()
        
        if window_title == 'current':
            window_titles = [w.get('title', 'Unknown') for w in available_windows[:5]]
            return f"🔍 Available windows to maximize:\n" + "\n".join([f"• {w}" for w in window_titles]) + f"\n\nPlease specify which window to maximize (e.g., 'maximize notepad')"
        else:
            # Try to maximize specific window
            result = maximize_window_by_title(window_title)
            if result and not result.startswith("❌"):
                return result
            else:
                window_titles = [w.get('title', 'Unknown') for w in available_windows[:5]]
                return f"❌ Could not find window: {window_title}\n\nAvailable windows:\n" + "\n".join([f"• {w}" for w in window_titles])
    
    except Exception as e:
        return f"❌ Maximize failed: {str(e)}"

def get_window_list() -> List[Dict[str, Any]]:
    """Get list of open windows"""
    windows = []
    
    try:
        if platform.system() == "Windows" and WINDOWS_AVAILABLE:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            'title': title,
                            'hwnd': hwnd,
                            'rect': rect
                        })
                return True
            
            win32gui.EnumWindows(enum_windows_callback, windows)
        
        elif platform.system() == "Darwin" and MACOS_AVAILABLE:
            # macOS window enumeration
            window_list = Quartz.CGWindowListCopyWindowInfo(
                Quartz.kCGWindowListOptionOnScreenOnly,
                Quartz.kCGNullWindowID
            )
            
            for window in window_list:
                title = window.get('kCGWindowName', '')
                if title:
                    bounds = window.get('kCGWindowBounds', {})
                    windows.append({
                        'title': title,
                        'bounds': bounds
                    })
        
        else:  # Linux
            # Use wmctrl if available
            try:
                result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            windows.append({
                                'title': parts[3],
                                'id': parts[0]
                            })
            except FileNotFoundError:
                logger.warning("wmctrl not available for Linux window management")
    
    except Exception as e:
        logger.error(f"Failed to get window list: {e}")
    
    return windows

def minimize_window_by_title(title: str) -> str:
    """Minimize window by title"""
    try:
        windows = get_window_list()
        for window in windows:
            if title.lower() in window['title'].lower():
                if platform.system() == "Windows" and WINDOWS_AVAILABLE:
                    win32gui.ShowWindow(window['hwnd'], win32con.SW_MINIMIZE)
                    return f"✅ Minimized window: {window['title']}"
        
        return f"❌ Window not found: {title}"
    
    except Exception as e:
        return f"❌ Failed to minimize window: {str(e)}"

def close_window_by_title(title: str) -> str:
    """Close window by title"""
    try:
        windows = get_window_list()
        for window in windows:
            if title.lower() in window['title'].lower():
                if platform.system() == "Windows" and WINDOWS_AVAILABLE:
                    win32gui.PostMessage(window['hwnd'], win32con.WM_CLOSE, 0, 0)
                    return f"✅ Closed window: {window['title']}"
        
        return f"❌ Window not found: {title}"
    
    except Exception as e:
        return f"❌ Failed to close window: {str(e)}"

def maximize_window_by_title(title: str) -> str:
    """Maximize window by title"""
    try:
        windows = get_window_list()
        for window in windows:
            if title.lower() in window['title'].lower():
                if platform.system() == "Windows" and WINDOWS_AVAILABLE:
                    win32gui.ShowWindow(window['hwnd'], win32con.SW_MAXIMIZE)
                    return f"✅ Maximized window: {window['title']}"
        
        return f"❌ Window not found: {title}"
    
    except Exception as e:
        return f"❌ Failed to maximize window: {str(e)}"

def capture_window_screenshot(window_title: Optional[str] = None) -> Optional[Image.Image]:
    """Capture screenshot of specific window or entire screen"""
    try:
        if window_title:
            windows = get_window_list()
            for window in windows:
                if window_title.lower() in window['title'].lower():
                    if platform.system() == "Windows" and WINDOWS_AVAILABLE:
                        # Get window rectangle and capture that area
                        rect = window['rect']
                        screenshot = ImageGrab.grab(bbox=rect)
                        return screenshot
        
        # Fallback to full screen
        return ImageGrab.grab()
    
    except Exception as e:
        logger.error(f"Window screenshot failed: {e}")
        return ImageGrab.grab()  # Fallback to full screen

# Test function
if __name__ == "__main__":
    # Test intent execution
    test_intents = [
        {
            'action': 'click',
            'target': 'close button'
        },
        {
            'action': 'minimize',
            'window': 'current'
        },
        {
            'action': 'click',
            'target': 'submit button'
        }
    ]
    
    print("🧪 Testing Enhanced Screen Controller...")
    for intent in test_intents:
        plan = render_plan(intent)
        print(f"\nIntent: {intent}")
        print(f"Plan: {plan}")
    
    # Test window detection
    windows = get_window_list()
    print(f"\n📱 Found {len(windows)} windows:")
    for window in windows[:5]:  # Show first 5
        print(f"  - {window['title']}")
    
    print("\n✅ Enhanced Screen Controller tests completed!")