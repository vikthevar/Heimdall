#!/usr/bin/env python3
"""
Heimdall - Free AI Voice Assistant for Screen Control
"""
import asyncio
import os
from loguru import logger
from dotenv import load_dotenv

# Import core components
from src.core.voice_handler import VoiceHandler
from src.core.voice_output import VoiceOutput
from src.core.intent_parser import IntentParser
from src.core.screenshot_capturer import ScreenshotCapturer
from src.core.screen_analyzer import ScreenAnalyzer
from src.core.screen_controller import ScreenController
from src.storage.database import LocalDatabase
from src.utils.config import get_config, validate_environment


class Heimdall:
    def __init__(self):
        """Initialize Heimdall with free components"""
        # Load environment variables and validate setup
        load_dotenv()
        validate_environment()
        
        # Get configuration
        self.config = get_config()
        
        # Initialize components using config
        self.voice_handler = VoiceHandler(
            model_size=self.config.local_ai.whisper_model
        )
        
        self.voice_output = VoiceOutput(
            voice_index=self.config.local_tts.voice_index,
            rate=self.config.local_tts.rate,
            volume=self.config.local_tts.volume
        )
        
        self.intent_parser = IntentParser(
            ollama_host=self.config.local_ai.ollama_host,
            model=self.config.local_ai.ollama_model
        )
        
        self.screenshot_capturer = ScreenshotCapturer(
            screenshots_path=self.config.local_storage.screenshots_path
        )
        
        self.screen_analyzer = ScreenAnalyzer(
            ocr_confidence_threshold=self.config.screen_analysis.ocr_confidence_threshold
        )
        
        self.screen_controller = ScreenController()
        
        self.database = LocalDatabase(
            db_path=self.config.local_storage.database_path
        )
        
        self.is_running = False
    
    async def initialize(self):
        """Initialize all components"""
        try:
            logger.info("Initializing Heimdall...")
            
            # Initialize database
            await self.database.initialize()
            
            # Initialize voice components
            await self.voice_handler.initialize()
            self.voice_output.initialize()
            
            # Initialize AI components
            await self.intent_parser.initialize()
            
            logger.info("Heimdall initialized successfully!")
            await self.voice_output.speak("Heimdall is ready. How can I help you?")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
    
    async def process_command(self, user_input: str) -> bool:
        """Process a single voice command"""
        try:
            logger.info(f"Processing command: {user_input}")
            
            # Log command start
            command_id = await self.database.log_command(user_input)
            
            # Capture and analyze screen
            screenshot, screenshot_path = await self.screenshot_capturer.capture_screen()
            screen_analysis = await self.screen_analyzer.analyze_screen(screenshot)
            
            # Log screenshot
            if screenshot_path:
                await self.database.log_screenshot(
                    screenshot_path, screen_analysis, command_id
                )
            
            # Parse intent
            screen_context = screen_analysis.get("full_text", "")
            parsed_intent = await self.intent_parser.parse_command(user_input, screen_context)
            
            logger.info(f"Parsed intent: {parsed_intent}")
            
            # Execute action
            success, response = await self.execute_action(parsed_intent, screen_analysis)
            
            # Update command log
            await self.database.log_command(
                user_input, parsed_intent.dict(), 
                parsed_intent.action, success, response, screen_context
            )
            
            # Provide voice feedback
            await self.voice_output.speak(response)
            
            return success
            
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            await self.voice_output.speak("Sorry, I encountered an error processing that command.")
            return False
    
    async def execute_action(self, intent, screen_analysis) -> tuple[bool, str]:
        """Execute the parsed action"""
        try:
            action = intent.action.lower()
            
            if action == "click":
                return await self.handle_click(intent, screen_analysis)
            elif action == "scroll":
                return await self.handle_scroll(intent)
            elif action == "type":
                return await self.handle_type(intent)
            elif action == "read":
                return await self.handle_read(screen_analysis)
            elif action == "navigate":
                return await self.handle_navigate(intent)
            else:
                return False, f"I don't know how to {action}. Try clicking, scrolling, typing, or reading."
                
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return False, "I had trouble executing that action."
    
    async def handle_click(self, intent, screen_analysis) -> tuple[bool, str]:
        """Handle click actions"""
        target = intent.target
        if not target:
            return False, "I need to know what to click on."
        
        # Find element by text
        element = await self.screen_analyzer.find_element_by_text(screen_analysis, target)
        
        if element:
            center_x, center_y = self.screen_analyzer.get_element_center(element)
            success = await self.screen_controller.click(center_x, center_y)
            
            if success:
                return True, f"I clicked on '{element.text}'"
            else:
                return False, "I had trouble clicking that element."
        else:
            return False, f"I couldn't find '{target}' on the screen."
    
    async def handle_scroll(self, intent) -> tuple[bool, str]:
        """Handle scroll actions"""
        direction = intent.parameters.get("direction", "down")
        clicks = intent.parameters.get("clicks", 3)
        
        success = await self.screen_controller.scroll(direction, clicks)
        
        if success:
            return True, f"I scrolled {direction}"
        else:
            return False, "I had trouble scrolling."
    
    async def handle_type(self, intent) -> tuple[bool, str]:
        """Handle typing actions"""
        text = intent.target or intent.parameters.get("text", "")
        
        if not text:
            return False, "I need to know what to type."
        
        success = await self.screen_controller.type_text(text)
        
        if success:
            return True, f"I typed '{text}'"
        else:
            return False, "I had trouble typing that text."
    
    async def handle_read(self, screen_analysis) -> tuple[bool, str]:
        """Handle read actions"""
        full_text = screen_analysis.get("full_text", "")
        
        if full_text:
            # Limit text length for voice output
            if len(full_text) > 500:
                full_text = full_text[:500] + "... and more"
            
            return True, f"Here's what I see on the screen: {full_text}"
        else:
            return True, "I don't see any readable text on the screen."
    
    async def handle_navigate(self, intent) -> tuple[bool, str]:
        """Handle navigation actions"""
        target = intent.target
        
        # Simple navigation commands
        if "back" in target.lower():
            success = await self.screen_controller.key_combination("alt", "left")
            return success, "I went back" if success else "I couldn't go back"
        elif "forward" in target.lower():
            success = await self.screen_controller.key_combination("alt", "right")
            return success, "I went forward" if success else "I couldn't go forward"
        else:
            return False, f"I don't know how to navigate to '{target}'"
    
    async def run(self):
        """Main application loop"""
        self.is_running = True
        
        try:
            await self.initialize()
            
            logger.info("Starting main loop. Say 'stop heimdall' to exit.")
            
            while self.is_running:
                try:
                    # Listen for voice command
                    user_input = await self.voice_handler.listen_for_command(duration=5)
                    
                    if user_input:
                        # Check for exit command
                        if any(phrase in user_input.lower() for phrase in ["stop heimdall", "exit", "quit"]):
                            await self.voice_output.speak("Goodbye!")
                            break
                        
                        # Process the command
                        await self.process_command(user_input)
                    
                    # Small delay between listening cycles
                    await asyncio.sleep(0.5)
                    
                except KeyboardInterrupt:
                    logger.info("Received keyboard interrupt")
                    break
                except Exception as e:
                    logger.error(f"Main loop error: {e}")
                    await self.voice_output.speak("I encountered an error. Let me try again.")
                    await asyncio.sleep(1)
        
        finally:
            self.is_running = False
            logger.info("Heimdall stopped")


async def main():
    """Entry point"""
    # Ensure data directories exist
    os.makedirs("./data/logs", exist_ok=True)
    
    # Configure logging
    logger.add("./data/logs/heimdall.log", rotation="1 day", retention="7 days")
    
    heimdall = Heimdall()
    
    try:
        await heimdall.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())