#!/usr/bin/env python3
"""
LLM Wrapper - Intent parsing and response generation with Ollama integration
Handles natural language understanding and response generation
"""
import logging
import subprocess
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

def call_ollama(prompt: str, model: str = "llama3.2") -> str:
    """
    Call Ollama LLM for intelligent responses
    
    Args:
        prompt: Input prompt for the LLM
        model: Ollama model to use
        
    Returns:
        LLM response text
    """
    try:
        # Construct the full prompt with system context
        system_prompt = """You are Heimdall, an AI assistant that helps users control their computer through voice and text commands. You can:

1. Analyze screen content using OCR
2. Click buttons and UI elements  
3. Scroll and navigate pages
4. Type text into fields
5. Provide helpful responses

When users ask for automation tasks, respond helpfully and indicate what action you'll take. Keep responses concise and friendly.

User request: """
        
        full_prompt = system_prompt + prompt
        
        # Call Ollama using subprocess with full path on Windows
        import platform
        import os
        
        ollama_cmd = "ollama"
        if platform.system() == "Windows":
            # Try common Ollama installation paths
            ollama_paths = [
                os.path.expanduser(r"~\AppData\Local\Programs\Ollama\ollama.exe"),
                r"C:\Program Files\Ollama\ollama.exe",
                r"C:\Program Files (x86)\Ollama\ollama.exe"
            ]
            
            for path in ollama_paths:
                if os.path.exists(path):
                    ollama_cmd = path
                    break
        
        result = subprocess.run(
            [ollama_cmd, "run", model, full_prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',  # Ignore encoding errors
            timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            logger.info(f"Ollama response received: {len(response)} characters")
            return response
        else:
            logger.error(f"Ollama error: {result.stderr}")
            return f"❌ Ollama error: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        logger.error("Ollama request timed out")
        return "❌ Request timed out. Please try again."
    except FileNotFoundError:
        logger.error("Ollama not found - falling back to rule-based responses")
        return None  # Will trigger fallback
    except Exception as e:
        logger.error(f"Ollama call failed: {e}")
        return f"❌ LLM error: {str(e)}"

def intent_and_reply(text: str) -> Dict[str, Any]:
    """
    Parse user intent and generate appropriate reply using Ollama + fallback rules
    
    Args:
        text: User input text
        
    Returns:
        Dict with 'reply' and 'intent' keys
    """
    try:
        text_lower = text.lower().strip()
        
        # Try Ollama first for intelligent responses
        ollama_response = call_ollama(text)
        
        # Parse intent using rule-based system (reliable for automation)
        intent = parse_intent_rules(text_lower)
        
        # Use Ollama response if available, otherwise use rule-based reply
        if ollama_response and not ollama_response.startswith("❌"):
            reply = ollama_response
        else:
            reply = generate_fallback_reply(text, intent)
        
        return {
            'reply': reply,
            'intent': intent
        }
    
    except Exception as e:
        logger.error(f"Error in intent_and_reply: {e}")
        return {
            'reply': f"❌ Sorry, I encountered an error processing your request: {str(e)}",
            'intent': {
                'type': 'error',
                'error': str(e),
                'confidence': 0.0
            }
        }

def parse_intent_rules(text_lower: str) -> Dict[str, Any]:
    """
    Parse intent using rule-based system for reliable automation detection
    
    Args:
        text_lower: Lowercase user input
        
    Returns:
        Intent dictionary
    """
    # Volume control intents
    if any(word in text_lower for word in ['volume', 'sound', 'audio']):
        if any(word in text_lower for word in ['up', 'increase', 'louder', 'higher']):
            return {
                'type': 'automation',
                'action': 'volume',
                'volume_action': 'increase',
                'confidence': 0.9
            }
        elif any(word in text_lower for word in ['down', 'decrease', 'lower', 'quieter']):
            return {
                'type': 'automation',
                'action': 'volume',
                'volume_action': 'decrease',
                'confidence': 0.9
            }
        elif any(word in text_lower for word in ['mute', 'silent', 'off']):
            return {
                'type': 'automation',
                'action': 'volume',
                'volume_action': 'mute',
                'confidence': 0.9
            }
    
    # Window management intents
    elif any(word in text_lower for word in ['close', 'exit', 'quit']):
        window = extract_window_reference(text_lower)
        return {
            'type': 'automation',
            'action': 'close',
            'window': window,
            'confidence': 0.9
        }
    
    elif any(word in text_lower for word in ['minimize', 'hide']):
        window = extract_window_reference(text_lower)
        return {
            'type': 'automation',
            'action': 'minimize',
            'window': window,
            'confidence': 0.9
        }
    
    elif any(word in text_lower for word in ['maximize', 'fullscreen', 'full screen']):
        window = extract_window_reference(text_lower)
        return {
            'type': 'automation',
            'action': 'maximize',
            'window': window,
            'confidence': 0.9
        }
    
    # Screen reading intents
    elif any(word in text_lower for word in ['read', 'screen', 'see', 'what', 'show', 'display', 'capture', 'screenshot']):
        window = extract_window_reference(text_lower)
        return {
            'type': 'screen_read',
            'action': 'analyze_screen',
            'window': window,
            'confidence': 0.9
        }
    
    # Click/automation intents
    elif any(word in text_lower for word in ['click', 'press', 'tap', 'select']):
        # Extract target from text
        target = extract_click_target(text_lower)
        
        # Special handling for Heimdall UI elements
        if any(word in text_lower for word in ['screen button', 'camera button', 'screen']):
            target = 'screen button'
        elif any(word in text_lower for word in ['voice button', 'microphone', 'mic']):
            target = 'voice button'
        elif any(word in text_lower for word in ['send button', 'send']):
            target = 'send button'
        
        return {
            'type': 'automation',
            'action': 'click',
            'target': target,
            'coordinates': None,  # Will be determined by screen analysis
            'confidence': 0.8
        }
    
    # Scroll intents
    elif any(word in text_lower for word in ['scroll', 'move', 'navigate', 'page']):
        direction = "down"  # Default
        if "up" in text_lower:
            direction = "up"
        elif "down" in text_lower:
            direction = "down"
        
        return {
            'type': 'automation',
            'action': 'scroll',
            'direction': direction,
            'amount': 3,  # Default scroll amount
            'confidence': 0.8
        }
    
    # Type/input intents
    elif any(word in text_lower for word in ['type', 'enter', 'input', 'write']):
        # Extract text to type (simplified)
        text_to_type = text_lower.replace('type', '').replace('enter', '').replace('input', '').strip()
        if not text_to_type:
            text_to_type = "hello world"
        
        return {
            'type': 'automation',
            'action': 'type',
            'text': text_to_type,
            'confidence': 0.7
        }
    
    # Voice intents
    elif any(word in text_lower for word in ['voice', 'speak', 'say', 'listen', 'microphone']):
        return {
            'type': 'voice',
            'action': 'voice_help',
            'confidence': 0.9
        }
    
    # Help intents
    elif any(word in text_lower for word in ['help', 'what', 'how', 'can', 'commands']):
        return {
            'type': 'help',
            'action': 'show_help',
            'confidence': 1.0
        }
    
    # Status/greeting intents
    elif any(word in text_lower for word in ['hello', 'hi', 'hey', 'status', 'ready']):
        return {
            'type': 'greeting',
            'action': 'greet_user',
            'confidence': 0.9
        }
    
    # Default/unknown intent
    else:
        return {
            'type': 'chat',
            'action': 'general_response',
            'user_input': text_lower,
            'confidence': 0.5
        }

# Removed duplicate function - using the one below

def extract_click_target(text: str) -> str:
    """Extract click target from text"""
    # Heimdall-specific UI elements
    if any(word in text for word in ['screen button', 'screen', 'camera button', '📸']):
        return 'screen button'
    elif any(word in text for word in ['voice button', 'microphone', 'mic button', '🎤']):
        return 'voice button'
    elif any(word in text for word in ['send button', 'send']):
        return 'send button'
    
    # Window controls
    elif any(word in text for word in ['close', 'x', 'exit']):
        return 'close button'
    elif any(word in text for word in ['minimize', 'hide']):
        return 'minimize button'
    elif any(word in text for word in ['maximize', 'fullscreen']):
        return 'maximize button'
    
    # Common buttons
    elif 'submit' in text:
        return 'submit button'
    elif 'ok' in text:
        return 'ok button'
    elif 'cancel' in text:
        return 'cancel button'
    elif 'save' in text:
        return 'save button'
    elif 'button' in text:
        # Extract the word before 'button'
        words = text.split()
        for i, word in enumerate(words):
            if word == 'button' and i > 0:
                return f"{words[i-1]} button"
        return 'button'
    elif 'link' in text:
        return 'link'
    else:
        return 'button'

def generate_fallback_reply(text: str, intent: Dict[str, Any]) -> str:
    """
    Generate fallback reply when Ollama is not available
    
    Args:
        text: Original user input
        intent: Parsed intent dictionary
        
    Returns:
        Fallback reply text
    """
    intent_type = intent.get('type', 'unknown')
    
    if intent_type == 'screen_read':
        return "📖 I'll analyze your screen content for you."
    
    elif intent_type == 'automation':
        action = intent.get('action', 'action')
        if action == 'click':
            target = intent.get('target', 'element')
            return f"🖱️ I'll click the {target} for you."
        elif action == 'scroll':
            direction = intent.get('direction', 'down')
            return f"⬇️ I'll scroll {direction} for you."
        elif action == 'type':
            text_to_type = intent.get('text', 'text')
            return f"⌨️ I'll type '{text_to_type}' for you."
    
    elif intent_type == 'voice':
        return "🎤 Voice features are available! I can listen to voice commands and speak responses."
    
    elif intent_type == 'help':
        return """🆘 **Heimdall AI Assistant Help**

I can help you with:

🖥️ **Screen Control:**
• "Read my screen" - Analyze screen content
• "Click the blue button" - Click UI elements  
• "Scroll down" - Navigate pages
• "Type hello world" - Enter text

🎤 **Voice Commands:**
• "Listen for voice" - Voice recognition
• "Speak this text" - Text-to-speech

⚙️ **System Control:**
• "Take screenshot" - Capture screen
• "Find window" - Locate applications

Try any command to see how I work!"""
    
    elif intent_type == 'greeting':
        return f"""👋 Hello! I'm Heimdall, your AI assistant.

🟢 **Status:** All systems operational
⏰ **Time:** {__import__('datetime').datetime.now().strftime('%H:%M:%S')}
🎯 **Ready for:** Screen control, voice commands, automation

What would you like me to help you with?"""
    
    else:
        return f"""🤖 I understand you said: "{text}"

I'm ready to help! Here are some things you can try:
• "Read my screen" - Analyze what's on your screen
• "Click the submit button" - Interact with UI elements
• "Minimize notepad" - Control specific windows
• "Increase volume" - Control system volume
• "Help" - See all available commands

What would you like me to do?"""

def extract_window_reference(text_lower: str) -> str:
    """
    Extract window reference from user input
    
    Args:
        text_lower: Lowercase user input
        
    Returns:
        Window reference string
    """
    # Check for specific window references
    if 'this' in text_lower or 'heimdall' in text_lower:
        return 'heimdall'
    elif 'kiro' in text_lower:
        return 'kiro'
    elif 'notepad' in text_lower:
        return 'notepad'
    elif 'browser' in text_lower or 'chrome' in text_lower or 'firefox' in text_lower:
        return 'browser'
    elif 'explorer' in text_lower or 'file' in text_lower:
        return 'explorer'
    elif 'calculator' in text_lower:
        return 'calculator'
    elif 'terminal' in text_lower or 'cmd' in text_lower or 'powershell' in text_lower:
        return 'terminal'
    else:
        return 'current'

# Test function
if __name__ == "__main__":
    # Test various inputs
    test_inputs = [
        "Hello",
        "Read my screen",
        "Click the submit button", 
        "Scroll down",
        "Type hello world",
        "Help me",
        "What can you do?"
    ]
    
    print("🧪 Testing LLM Wrapper...")
    for test_input in test_inputs:
        result = intent_and_reply(test_input)
        print(f"\nInput: '{test_input}'")
        print(f"Intent: {result['intent']['type']} - {result['intent']['action']}")
        print(f"Reply: {result['reply'][:100]}...")
    
    print("\n✅ LLM Wrapper tests completed!")