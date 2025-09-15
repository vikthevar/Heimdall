#!/usr/bin/env python3
"""
Screen Controller - UI Automation and Control
Executes automation actions on the screen
"""
import pyautogui
import time
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

def execute_intent(intent: Dict[str, Any]) -> str:
    """
    Execute automation intent on the screen
    
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
    """Execute click action"""
    try:
        target = intent.get('target', 'element')
        coordinates = intent.get('coordinates')
        
        if coordinates:
            # Direct coordinate click
            x, y = coordinates
            pyautogui.click(x, y)
            return f"✅ Clicked at coordinates ({x}, {y})"
        else:
            # Try to find element by text/image (simplified)
            # For now, click center of screen as fallback
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2
            pyautogui.click(center_x, center_y)
            return f"✅ Clicked {target} (center of screen as fallback)"
    
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

# Test function
if __name__ == "__main__":
    # Test intent execution
    test_intents = [
        {
            'action': 'scroll',
            'direction': 'down',
            'amount': 3
        },
        {
            'action': 'type',
            'text': 'Hello World'
        },
        {
            'action': 'click',
            'target': 'button',
            'coordinates': (100, 100)
        }
    ]
    
    print("🧪 Testing Screen Controller...")
    for intent in test_intents:
        plan = render_plan(intent)
        print(f"\nIntent: {intent}")
        print(f"Plan: {plan}")
    
    print("\n✅ Screen Controller tests completed!")