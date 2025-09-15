#!/usr/bin/env python3
"""
LLM Wrapper - Intent parsing and response generation
Handles natural language understanding and response generation
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def intent_and_reply(text: str) -> Dict[str, Any]:
    """
    Parse user intent and generate appropriate reply
    
    Args:
        text: User input text
        
    Returns:
        Dict with 'reply' and 'intent' keys
    """
    try:
        text_lower = text.lower().strip()
        
        # Screen reading intents
        if any(word in text_lower for word in ['read', 'screen', 'see', 'what', 'show', 'display']):
            return {
                'reply': "📖 I'll analyze your screen content for you.",
                'intent': {
                    'type': 'screen_read',
                    'action': 'analyze_screen',
                    'confidence': 0.9
                }
            }
        
        # Click/automation intents
        elif any(word in text_lower for word in ['click', 'press', 'tap', 'select']):
            # Extract target from text
            target = "button"  # Default
            if "button" in text_lower:
                target = "button"
            elif "link" in text_lower:
                target = "link"
            elif "submit" in text_lower:
                target = "submit button"
            
            return {
                'reply': f"🖱️ I'll click the {target} for you.",
                'intent': {
                    'type': 'automation',
                    'action': 'click',
                    'target': target,
                    'coordinates': None,  # Will be determined by screen analysis
                    'confidence': 0.8
                }
            }
        
        # Scroll intents
        elif any(word in text_lower for word in ['scroll', 'move', 'navigate', 'page']):
            direction = "down"  # Default
            if "up" in text_lower:
                direction = "up"
            elif "down" in text_lower:
                direction = "down"
            
            return {
                'reply': f"⬇️ I'll scroll {direction} for you.",
                'intent': {
                    'type': 'automation',
                    'action': 'scroll',
                    'direction': direction,
                    'amount': 3,  # Default scroll amount
                    'confidence': 0.8
                }
            }
        
        # Type/input intents
        elif any(word in text_lower for word in ['type', 'enter', 'input', 'write']):
            # Extract text to type (simplified)
            text_to_type = text.replace('type', '').replace('enter', '').replace('input', '').strip()
            if not text_to_type:
                text_to_type = "hello world"
            
            return {
                'reply': f"⌨️ I'll type '{text_to_type}' for you.",
                'intent': {
                    'type': 'automation',
                    'action': 'type',
                    'text': text_to_type,
                    'confidence': 0.7
                }
            }
        
        # Voice intents
        elif any(word in text_lower for word in ['voice', 'speak', 'say', 'listen', 'microphone']):
            return {
                'reply': "🎤 Voice features are available! I can listen to voice commands and speak responses.",
                'intent': {
                    'type': 'voice',
                    'action': 'voice_help',
                    'confidence': 0.9
                }
            }
        
        # Help intents
        elif any(word in text_lower for word in ['help', 'what', 'how', 'can', 'commands']):
            return {
                'reply': """🆘 **Heimdall AI Assistant Help**

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

Try any command to see how I work!""",
                'intent': {
                    'type': 'help',
                    'action': 'show_help',
                    'confidence': 1.0
                }
            }
        
        # Status/greeting intents
        elif any(word in text_lower for word in ['hello', 'hi', 'hey', 'status', 'ready']):
            return {
                'reply': f"""👋 Hello! I'm Heimdall, your AI assistant.

🟢 **Status:** All systems operational
⏰ **Time:** {__import__('datetime').datetime.now().strftime('%H:%M:%S')}
🎯 **Ready for:** Screen control, voice commands, automation

What would you like me to help you with?""",
                'intent': {
                    'type': 'greeting',
                    'action': 'greet_user',
                    'confidence': 0.9
                }
            }
        
        # Default/unknown intent
        else:
            return {
                'reply': f"""🤖 I understand you said: "{text}"

I'm ready to help! Here are some things you can try:
• "Read my screen" - Analyze what's on your screen
• "Click the submit button" - Interact with UI elements
• "Help" - See all available commands

What would you like me to do?""",
                'intent': {
                    'type': 'chat',
                    'action': 'general_response',
                    'user_input': text,
                    'confidence': 0.5
                }
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