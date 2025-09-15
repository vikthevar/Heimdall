"""
GUI Integration for Heimdall AI Assistant
Connects the UI with the core AI functionality
"""
import asyncio
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon

from .main_window import HeimdallMainWindow
from .components import NotificationToast, LoadingSpinner
from ..core.voice_handler import VoiceHandler
from ..core.voice_output import VoiceOutput
from ..core.intent_parser import IntentParser
from ..core.screenshot_capturer import ScreenshotCapturer
from ..core.screen_analyzer import ScreenAnalyzer
from ..core.screen_controller import ScreenController
from ..storage.database import LocalDatabase
from ..utils.config import get_config


class AIWorkerThread(QThread):
    """Background thread for AI processing"""
    
    # Signals
    message_processed = pyqtSignal(str, bool)  # response, success
    status_changed = pyqtSignal(str)  # status
    voice_command_received = pyqtSignal(str)  # command text
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.is_running = False
        self.current_task = None
        
        # Initialize AI components
        self.voice_handler = None
        self.voice_output = None
        self.intent_parser = None
        self.screenshot_capturer = None
        self.screen_analyzer = None
        self.screen_controller = None
        self.database = None
    
    async def initialize_components(self):
        """Initialize all AI components"""
        try:
            self.status_changed.emit("Initializing AI components...")
            
            # Initialize components
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
            
            # Initialize async components
            await self.database.initialize()
            await self.voice_handler.initialize()
            self.voice_output.initialize()
            await self.intent_parser.initialize()
            
            self.status_changed.emit("Ready")
            return True
            
        except Exception as e:
            self.status_changed.emit(f"Initialization failed: {str(e)}")
            return False
    
    def run(self):
        """Main thread loop"""
        self.is_running = True
        
        # Create event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Initialize components
            success = loop.run_until_complete(self.initialize_components())
            
            if not success:
                return
            
            # Main processing loop
            while self.is_running:
                if self.current_task:
                    loop.run_until_complete(self.process_task())
                    self.current_task = None
                
                # Small delay to prevent busy waiting
                loop.run_until_complete(asyncio.sleep(0.1))
                
        except Exception as e:
            self.status_changed.emit(f"Error: {str(e)}")
        finally:
            loop.close()
    
    async def process_task(self):
        """Process the current task"""
        if not self.current_task:
            return
        
        task_type = self.current_task.get('type')
        
        try:
            if task_type == 'text_message':
                await self.process_text_message(self.current_task['message'])
            elif task_type == 'voice_command':
                await self.process_voice_command()
            elif task_type == 'screen_analysis':
                await self.process_screen_analysis()
                
        except Exception as e:
            self.message_processed.emit(f"Error processing task: {str(e)}", False)
    
    async def process_text_message(self, message):
        """Process a text message from the user"""
        try:
            self.status_changed.emit("processing")
            
            # Log the command
            command_id = await self.database.log_command(message)
            
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
            parsed_intent = await self.intent_parser.parse_command(message, screen_context)
            
            # Execute action
            success, response = await self.execute_action(parsed_intent, screen_analysis)
            
            # Update command log
            await self.database.log_command(
                message, parsed_intent.dict(), 
                parsed_intent.action, success, response, screen_context
            )
            
            # Provide voice feedback
            await self.voice_output.speak(response)
            
            self.message_processed.emit(response, success)
            self.status_changed.emit("idle")
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.message_processed.emit(error_msg, False)
            self.status_changed.emit("idle")
    
    async def process_voice_command(self):
        """Process voice input"""
        try:
            self.status_changed.emit("listening")
            
            # Listen for voice command
            user_input = await self.voice_handler.listen_for_command(duration=5)
            
            if user_input:
                self.voice_command_received.emit(user_input)
                
                # Check for exit command
                if any(phrase in user_input.lower() for phrase in ["stop heimdall", "exit", "quit"]):
                    await self.voice_output.speak("Goodbye!")
                    self.is_running = False
                    return
                
                # Process as text message
                self.current_task = {'type': 'text_message', 'message': user_input}
                await self.process_task()
            else:
                self.status_changed.emit("idle")
                
        except Exception as e:
            error_msg = f"Voice processing error: {str(e)}"
            self.message_processed.emit(error_msg, False)
            self.status_changed.emit("idle")
    
    async def execute_action(self, intent, screen_analysis):
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
            return False, f"Error executing action: {str(e)}"
    
    async def handle_click(self, intent, screen_analysis):
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
    
    async def handle_scroll(self, intent):
        """Handle scroll actions"""
        direction = intent.parameters.get("direction", "down")
        clicks = intent.parameters.get("clicks", 3)
        
        success = await self.screen_controller.scroll(direction, clicks)
        
        if success:
            return True, f"I scrolled {direction}"
        else:
            return False, "I had trouble scrolling."
    
    async def handle_type(self, intent):
        """Handle typing actions"""
        text = intent.target or intent.parameters.get("text", "")
        
        if not text:
            return False, "I need to know what to type."
        
        success = await self.screen_controller.type_text(text)
        
        if success:
            return True, f"I typed '{text}'"
        else:
            return False, "I had trouble typing that text."
    
    async def handle_read(self, screen_analysis):
        """Handle read actions"""
        full_text = screen_analysis.get("full_text", "")
        
        if full_text:
            # Limit text length for voice output
            if len(full_text) > 500:
                full_text = full_text[:500] + "... and more"
            
            return True, f"Here's what I see on the screen: {full_text}"
        else:
            return True, "I don't see any readable text on the screen."
    
    async def handle_navigate(self, intent):
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
    
    def add_task(self, task):
        """Add a task to be processed"""
        self.current_task = task
    
    def stop_processing(self):
        """Stop the processing thread"""
        self.is_running = False


class HeimdallGUI:
    """Main GUI application controller"""
    
    def __init__(self):
        self.app = None
        self.window = None
        self.ai_worker = None
        self.notification_timer = QTimer()
        
    def initialize(self):
        """Initialize the GUI application"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Heimdall AI Assistant")
        self.app.setQuitOnLastWindowClosed(False)
        
        # Set application icon (you'll need to add this file)
        # self.app.setWindowIcon(QIcon("assets/heimdall_icon.png"))
        
        # Create main window
        self.window = HeimdallMainWindow()
        
        # Create AI worker thread
        self.ai_worker = AIWorkerThread()
        
        # Connect signals
        self.setup_connections()
        
        # Start AI worker
        self.ai_worker.start()
        
        return True
    
    def setup_connections(self):
        """Setup signal connections between UI and AI"""
        # UI to AI signals
        self.window.message_sent.connect(self.handle_text_message)
        
        # AI to UI signals
        self.ai_worker.message_processed.connect(self.handle_ai_response)
        self.ai_worker.status_changed.connect(self.handle_status_change)
        self.ai_worker.voice_command_received.connect(self.handle_voice_command)
    
    def handle_text_message(self, message):
        """Handle text message from UI"""
        task = {'type': 'text_message', 'message': message}
        self.ai_worker.add_task(task)
    
    def handle_ai_response(self, response, success):
        """Handle AI response"""
        # Add AI response to chat
        self.window.add_message(response, False)
        
        # Show notification if window is not active
        if not self.window.isActiveWindow():
            self.show_notification(response, "info" if success else "error")
    
    def handle_status_change(self, status):
        """Handle AI status change"""
        self.window.status_indicator.update_status(status)
    
    def handle_voice_command(self, command):
        """Handle voice command received"""
        # Add user message to chat
        self.window.add_message(command, True)
    
    def show_notification(self, message, notification_type="info"):
        """Show system notification"""
        notification = NotificationToast(message, notification_type)
        
        # Position notification in top-right corner
        screen = self.app.primaryScreen().geometry()
        notification.move(
            screen.width() - notification.width() - 20,
            20
        )
        
        notification.show_notification()
    
    def start_voice_listening(self):
        """Start voice listening"""
        task = {'type': 'voice_command'}
        self.ai_worker.add_task(task)
    
    def run(self):
        """Run the GUI application"""
        if not self.initialize():
            return 1
        
        # Show main window
        self.window.show()
        
        # Connect voice button
        # Note: You'll need to connect this in the main window
        # self.window.voice_btn.clicked.connect(self.start_voice_listening)
        
        # Run application
        try:
            return self.app.exec()
        finally:
            # Cleanup
            if self.ai_worker:
                self.ai_worker.stop_processing()
                self.ai_worker.wait()


def main():
    """Main entry point for GUI application"""
    gui = HeimdallGUI()
    return gui.run()


if __name__ == "__main__":
    sys.exit(main())