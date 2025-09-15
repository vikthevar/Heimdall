#!/usr/bin/env python3
"""
Heimdall Brain - Central AI Coordinator
Connects all AI components into one unified system
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import real helpers with robust error handling
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.core.llm_wrapper import intent_and_reply
except ImportError as e:
    logger.error(f"Failed to import llm_wrapper: {e}")
    def intent_and_reply(text):
        return {
            'reply': f"❌ LLM component missing: {str(e)}. Please check llm_wrapper module.",
            'intent': {'type': 'error', 'message': 'LLM not available'}
        }

try:
    from src.core.screen_analyzer import capture_fullscreen_and_ocr
except ImportError as e:
    logger.error(f"Failed to import screen_analyzer: {e}")
    def capture_fullscreen_and_ocr():
        return f"❌ Screen analyzer missing: {str(e)}. Please check screen_analyzer module."

try:
    from src.core.screen_controller import execute_intent, render_plan
except ImportError as e:
    logger.error(f"Failed to import screen_controller: {e}")
    def execute_intent(intent):
        return f"❌ Screen controller missing: {str(e)}. Please check screen_controller module."
    def render_plan(intent):
        return f"❌ Plan renderer missing: {str(e)}. Please check screen_controller module."

try:
    from src.core.voice_handler import record_and_transcribe
except ImportError as e:
    logger.error(f"Failed to import voice_handler: {e}")
    def record_and_transcribe():
        return f"❌ Voice handler missing: {str(e)}. Please check voice_handler module."

try:
    from src.storage.db import save_message, load_recent_messages
except ImportError as e:
    logger.error(f"Failed to import database: {e}")
    def save_message(user_msg, assistant_msg, intent=None):
        logger.warning(f"Database not available, message not saved: {user_msg}")
        return None
    def load_recent_messages(limit=10):
        logger.warning("Database not available, returning empty message history")
        return []

class HeimdallBrain:
    """Central coordinator for all AI components"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize all AI components"""
        try:
            logger.info("🧠 Initializing Heimdall Brain...")
            
            # Test component availability
            try:
                test_result = intent_and_reply("test")
                if "❌" in str(test_result):
                    logger.warning("Some components may not be fully available")
            except Exception as test_error:
                logger.warning(f"Component test failed: {test_error}")
            
            self.initialized = True
            logger.info("✅ Heimdall Brain initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Heimdall Brain: {e}")
            return False
    
    async def process_message(self, text: str, simulate_actions: bool = True) -> Dict[str, Any]:
        """
        Process user message and return AI response with execution details
        
        Args:
            text: User input message
            simulate_actions: If True, only simulate automation actions; if False, execute them
            
        Returns:
            Dict containing:
            - reply: Assistant response text
            - intent: Parsed intent information
            - executed: Whether automation was actually executed
            - execution_result: Result of execution if performed
        """
        if not self.initialized:
            return {
                'reply': "❌ AI system not initialized. Please restart the application.",
                'intent': {'type': 'error'},
                'executed': False,
                'execution_result': None
            }
        
        try:
            logger.info(f"🧠 Processing message: {text}")
            
            # Step 1: Get intent and reply from LLM
            llm_result = intent_and_reply(text)
            reply = llm_result.get('reply', 'No response generated')
            intent = llm_result.get('intent', {'type': 'unknown'})
            
            # Ensure reply is never None
            if reply is None:
                reply = 'No response generated'
            
            # Step 2: Save messages to database
            try:
                save_message(text, reply, intent)
                logger.debug("Messages saved to database")
            except Exception as db_error:
                logger.warning(f"Failed to save to database: {db_error}")
            
            # Step 3: Handle special intents
            executed = False
            execution_result = None
            
            if intent.get('type') == 'screen_read':
                # Handle screen reading with optional window specification
                try:
                    window_title = intent.get('window')
                    screen_content = await self.get_screen_content(window_title)
                    reply += f"\n\n{screen_content}"
                except Exception as screen_error:
                    reply += f"\n\n❌ **Screen Reading Error:** {str(screen_error)}"
            
            elif intent.get('type') == 'automation':
                if simulate_actions:
                    # Simulation mode: show plan but don't execute
                    plan = render_plan(intent)
                    reply += f"\n\n📋 **Execution Plan:**\n{plan}\n\n⚠️ *Simulation mode - actions not executed*"
                    executed = False
                else:
                    # Execution mode: actually perform the actions
                    try:
                        execution_result = execute_intent(intent)
                        
                        # Check if this was a special Heimdall action
                        if "triggering screen reading" in execution_result:
                            # Actually perform screen reading
                            try:
                                window_title = intent.get('window')
                                screen_content = await self.get_screen_content(window_title)
                                reply += f"\n\n✅ **Screen Button Clicked:** {execution_result}\n\n{screen_content}"
                            except Exception as screen_error:
                                reply += f"\n\n✅ **Screen Button Clicked:** {execution_result}\n\n❌ **Screen Reading Error:** {str(screen_error)}"
                        elif "triggering voice recording" in execution_result:
                            # Actually perform voice recording
                            reply += f"\n\n✅ **Voice Button Clicked:** {execution_result}\n\n🎤 **Voice recording would be activated** (use the microphone button in the GUI for actual voice input)"
                        else:
                            reply += f"\n\n✅ **Executed:** {execution_result}"
                        
                        executed = True
                    except Exception as exec_error:
                        execution_result = f"Execution failed: {str(exec_error)}"
                        reply += f"\n\n❌ **Execution Error:** {execution_result}"
                        executed = False
            
            return {
                'reply': reply,
                'intent': intent,
                'executed': executed,
                'execution_result': execution_result
            }
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return {
                'reply': f"❌ Sorry, I encountered an error: {str(e)}",
                'intent': {'type': 'error', 'error': str(e)},
                'executed': False,
                'execution_result': None
            }
    
    async def get_screen_content(self, window_title: str = None) -> str:
        """Capture and analyze screen content"""
        try:
            return capture_fullscreen_and_ocr(window_title)
        except Exception as e:
            logger.error(f"Screen capture error: {e}")
            return f"❌ Failed to capture screen: {str(e)}"
    
    async def record_voice_command(self) -> str:
        """Record and transcribe voice input"""
        try:
            return record_and_transcribe()
        except Exception as e:
            logger.error(f"Voice recording error: {e}")
            return f"❌ Failed to record voice: {str(e)}"
    
    def get_recent_messages(self, limit: int = 10) -> list:
        """Get recent conversation history"""
        try:
            return load_recent_messages(limit)
        except Exception as e:
            logger.warning(f"Failed to load message history: {e}")
            return []
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("🧠 Heimdall Brain cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Global instance
heimdall_brain = HeimdallBrain()

# Minimal unit-test style assertions
if __name__ == "__main__":
    import asyncio
    
    async def test_process_message():
        """Test the process_message function with sample input"""
        brain = HeimdallBrain()
        
        # Initialize
        init_success = await brain.initialize()
        assert init_success, "Brain initialization should succeed"
        
        # Test basic message processing
        result = await brain.process_message("Hello, can you help me?")
        
        # Assertions
        assert isinstance(result, dict), "Result should be a dictionary"
        assert 'reply' in result, "Result should contain 'reply' key"
        assert 'intent' in result, "Result should contain 'intent' key"
        assert 'executed' in result, "Result should contain 'executed' key"
        assert 'execution_result' in result, "Result should contain 'execution_result' key"
        
        assert isinstance(result['reply'], str), "Reply should be a string"
        assert len(result['reply']) > 0, "Reply should not be empty"
        
        print("✅ Basic message test passed")
        print(f"Reply: {result['reply'][:100]}...")
        
        # Test automation intent simulation
        automation_result = await brain.process_message("Click the submit button", simulate_actions=True)
        assert automation_result['executed'] == False, "Simulation should not execute actions"
        
        print("✅ Automation simulation test passed")
        
        # Test screen content
        screen_content = await brain.get_screen_content()
        assert isinstance(screen_content, str), "Screen content should be a string"
        
        print("✅ Screen content test passed")
        
        print("🎉 All tests passed!")
    
    # Run tests
    asyncio.run(test_process_message())