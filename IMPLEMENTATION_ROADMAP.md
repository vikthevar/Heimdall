# Heimdall Implementation Roadmap
## Step-by-Step Breakdown

## 🎯 **PHASE 1: Core Integration (Priority 1)**

### **Step 1: Connect GUI to AI Backend**
**Goal**: Replace demo responses with actual AI processing

#### **1.1 Create AI Integration Layer**
```python
# File: src/ai/heimdall_brain.py
class HeimdallBrain:
    def __init__(self):
        self.voice_handler = VoiceHandler()
        self.intent_parser = IntentParser()
        self.screen_analyzer = ScreenAnalyzer()
        self.screen_controller = ScreenController()
        self.voice_output = VoiceOutput()
        self.database = LocalDatabase()
    
    async def process_message(self, text: str) -> str:
        # Parse intent
        # Analyze screen if needed
        # Execute command
        # Return response
```

#### **1.2 Modify heimdall_working.py**
**Current code location**: Line ~200 in `send_message()` method
```python
# REPLACE THIS:
ai_html = f"""I understand you want me to: "{text}". This is a demo response..."""

# WITH THIS:
response = await self.ai_brain.process_message(text)
ai_html = f"""<div style='...'>{response}</div>"""
```

#### **1.3 Add Async Support to GUI**
```python
# Add to HeimdallWindow class:
from PyQt6.QtCore import QThread, pyqtSignal
import asyncio

class AIWorkerThread(QThread):
    response_ready = pyqtSignal(str)
    
    def __init__(self, ai_brain, message):
        super().__init__()
        self.ai_brain = ai_brain
        self.message = message
    
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            self.ai_brain.process_message(self.message)
        )
        self.response_ready.emit(response)
```

**Files to modify**:
- `heimdall_working.py` (main GUI)
- Create `src/ai/heimdall_brain.py`
- Update imports in GUI

---

### **Step 2: Implement Voice Integration**
**Goal**: Make the microphone button functional

#### **2.1 Add Voice Recording UI**
```python
# In heimdall_working.py, modify voice button click handler:
def start_voice_recording(self):
    self.voice_btn.setText("🔴")  # Recording indicator
    self.voice_btn.setStyleSheet("background: #e74c3c;")  # Red background
    
    # Start voice worker thread
    self.voice_worker = VoiceWorkerThread(self.ai_brain)
    self.voice_worker.voice_result.connect(self.handle_voice_result)
    self.voice_worker.start()
```

#### **2.2 Create Voice Worker Thread**
```python
class VoiceWorkerThread(QThread):
    voice_result = pyqtSignal(str)
    
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Record audio
        text = loop.run_until_complete(
            self.ai_brain.voice_handler.listen_for_command()
        )
        
        if text:
            self.voice_result.emit(text)
```

#### **2.3 Add Voice Status Indicators**
```python
# Add to GUI:
self.voice_status_label = QLabel("Ready")
# Update status during recording: "Listening...", "Processing...", "Ready"
```

**Files to modify**:
- `heimdall_working.py` (add voice functionality)
- `src/ai/heimdall_brain.py` (integrate voice_handler)

---

### **Step 3: Screen Reading Integration**
**Goal**: Add "Read Screen" functionality

#### **3.1 Add Screen Reading Button**
```python
# In heimdall_working.py header section:
screen_btn = QPushButton("📸 Read Screen")
screen_btn.clicked.connect(self.read_screen)
header_layout.addWidget(screen_btn)
```

#### **3.2 Implement Screen Reading**
```python
def read_screen(self):
    self.screen_worker = ScreenWorkerThread(self.ai_brain)
    self.screen_worker.screen_result.connect(self.handle_screen_result)
    self.screen_worker.start()

class ScreenWorkerThread(QThread):
    screen_result = pyqtSignal(str)
    
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Capture and analyze screen
        screenshot, _ = loop.run_until_complete(
            self.ai_brain.screenshot_capturer.capture_screen()
        )
        analysis = loop.run_until_complete(
            self.ai_brain.screen_analyzer.analyze_screen(screenshot)
        )
        
        text = analysis.get("full_text", "No text found on screen")
        self.screen_result.emit(f"Screen content: {text}")
```

**Files to modify**:
- `heimdall_working.py` (add screen reading button and handler)
- `src/ai/heimdall_brain.py` (integrate screen components)

---

### **Step 4: Command Execution Pipeline**
**Goal**: Process and execute user commands

#### **4.1 Enhance AI Brain with Command Processing**
```python
# In src/ai/heimdall_brain.py:
async def process_message(self, text: str) -> str:
    try:
        # Log command
        command_id = await self.database.log_command(text)
        
        # Capture screen for context
        screenshot, screenshot_path = await self.screenshot_capturer.capture_screen()
        screen_analysis = await self.screen_analyzer.analyze_screen(screenshot)
        
        # Parse intent
        screen_context = screen_analysis.get("full_text", "")
        intent = await self.intent_parser.parse_command(text, screen_context)
        
        # Execute command
        success, response = await self.execute_command(intent, screen_analysis)
        
        # Update database
        await self.database.log_command(
            text, intent.dict(), intent.action, success, response, screen_context
        )
        
        # Speak response
        await self.voice_output.speak(response)
        
        return response
        
    except Exception as e:
        error_msg = f"Error processing command: {str(e)}"
        logger.error(error_msg)
        return error_msg

async def execute_command(self, intent, screen_analysis):
    """Execute parsed command"""
    action = intent.action.lower()
    
    if action == "click":
        return await self.handle_click(intent, screen_analysis)
    elif action == "scroll":
        return await self.handle_scroll(intent)
    elif action == "type":
        return await self.handle_type(intent)
    elif action == "read":
        return await self.handle_read(screen_analysis)
    else:
        return False, f"Unknown command: {action}"
```

#### **4.2 Implement Command Handlers**
```python
async def handle_click(self, intent, screen_analysis):
    """Handle click commands"""
    target = intent.target
    if not target:
        return False, "Please specify what to click"
    
    # Find element
    element = await self.screen_analyzer.find_element_by_text(screen_analysis, target)
    if element:
        center_x, center_y = self.screen_analyzer.get_element_center(element)
        success = await self.screen_controller.click(center_x, center_y)
        return success, f"Clicked on '{element.text}'" if success else "Click failed"
    else:
        return False, f"Could not find '{target}' on screen"

async def handle_scroll(self, intent):
    """Handle scroll commands"""
    direction = intent.parameters.get("direction", "down")
    success = await self.screen_controller.scroll(direction)
    return success, f"Scrolled {direction}" if success else "Scroll failed"

async def handle_type(self, intent):
    """Handle typing commands"""
    text = intent.target or intent.parameters.get("text", "")
    if not text:
        return False, "Please specify what to type"
    
    success = await self.screen_controller.type_text(text)
    return success, f"Typed '{text}'" if success else "Typing failed"

async def handle_read(self, screen_analysis):
    """Handle read screen commands"""
    full_text = screen_analysis.get("full_text", "")
    if full_text:
        # Limit length for voice output
        if len(full_text) > 500:
            full_text = full_text[:500] + "..."
        return True, f"Screen content: {full_text}"
    else:
        return True, "No readable text found on screen"
```

**Files to create/modify**:
- `src/ai/__init__.py`
- `src/ai/heimdall_brain.py` (main AI integration)
- Update `heimdall_working.py` to use AI brain

---

## 🎯 **PHASE 2: Enhanced Integration (Priority 2)**

### **Step 5: Settings Integration**
**Goal**: Make settings panel functional

#### **5.1 Connect Settings to Configuration**
```python
# In heimdall_working.py settings view:
def create_settings_sections(self, layout):
    # Voice settings
    self.voice_volume_slider = QSlider(Qt.Orientation.Horizontal)
    self.voice_volume_slider.valueChanged.connect(self.update_voice_volume)
    
    # AI model selection
    self.model_combo = QComboBox()
    self.model_combo.addItems(["llama3.2:1b", "llama3.2:3b", "llama3.2:7b"])
    self.model_combo.currentTextChanged.connect(self.update_ai_model)

def update_voice_volume(self, value):
    self.ai_brain.voice_output.set_volume(value / 100.0)

def update_ai_model(self, model_name):
    self.ai_brain.intent_parser.model = model_name
```

#### **5.2 Persistent Settings Storage**
```python
# Add to src/ai/heimdall_brain.py:
async def save_settings(self, settings_dict):
    for key, value in settings_dict.items():
        await self.database.set_preference(key, value)

async def load_settings(self):
    settings = {}
    for key in ["voice_volume", "ai_model", "theme"]:
        settings[key] = await self.database.get_preference(key)
    return settings
```

---

### **Step 6: Database Integration**
**Goal**: Persist chat history and preferences

#### **6.1 Save Chat Messages**
```python
# In heimdall_working.py send_message():
async def send_message(self):
    text = self.input_field.text().strip()
    if text:
        # Save to database
        await self.ai_brain.database.log_command(text)
        
        # Process message
        response = await self.ai_brain.process_message(text)
        
        # Display in GUI
        self.add_message_to_chat(text, True)
        self.add_message_to_chat(response, False)
```

#### **6.2 Load Chat History on Startup**
```python
async def load_chat_history(self):
    recent_commands = await self.ai_brain.database.get_recent_commands(10)
    for command in recent_commands:
        self.add_message_to_chat(command['user_input'], True)
        if command['response_text']:
            self.add_message_to_chat(command['response_text'], False)
```

---

### **Step 7: Error Handling & User Feedback**
**Goal**: Robust error handling and user notifications

#### **7.1 Add Status Indicators**
```python
# In heimdall_working.py:
def update_connection_status(self, status):
    colors = {
        "connected": "#10b981",
        "disconnected": "#ef4444", 
        "processing": "#f59e0b"
    }
    self.connection_status.setStyleSheet(f"color: {colors[status]};")

def show_error_message(self, error_text):
    # Add error message to chat with red styling
    error_html = f"""
    <div style='color: #ef4444; background: rgba(239, 68, 68, 0.1); 
                padding: 10px; border-radius: 8px; margin: 10px 0;'>
        ⚠️ Error: {error_text}
    </div>
    """
    self.chat.insertHtml(error_html)
```

#### **7.2 Service Health Checks**
```python
# Add to src/ai/heimdall_brain.py:
async def check_services_health(self):
    health = {
        "ollama": await self.check_ollama_connection(),
        "whisper": await self.check_whisper_model(),
        "database": await self.check_database_connection()
    }
    return health

async def check_ollama_connection(self):
    try:
        # Test Ollama connection
        await self.intent_parser.parse_command("test", "")
        return True
    except:
        return False
```

---

## 🎯 **PHASE 3: Polish & Enhancement (Priority 3)**

### **Step 8: Advanced UI Features**

#### **8.1 Add Loading Indicators**
```python
# Spinning loader during AI processing
class LoadingSpinner(QLabel):
    def __init__(self):
        super().__init__()
        self.movie = QMovie("assets/spinner.gif")
        self.setMovie(self.movie)
    
    def start(self):
        self.movie.start()
        self.show()
    
    def stop(self):
        self.movie.stop()
        self.hide()
```

#### **8.2 Add Keyboard Shortcuts**
```python
# In heimdall_working.py:
def keyPressEvent(self, event):
    if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        self.send_message()
    elif event.key() == Qt.Key.Key_R and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        self.read_screen()
```

---

### **Step 9: Performance Optimization**

#### **9.1 Add Caching**
```python
# In src/ai/heimdall_brain.py:
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
async def cached_screen_analysis(self, screenshot_hash):
    # Cache OCR results for identical screenshots
    pass
```

#### **9.2 Optimize Startup Time**
```python
# Lazy load heavy components
async def initialize_components(self):
    # Load only essential components first
    await self.database.initialize()
    
    # Load AI components in background
    asyncio.create_task(self.load_ai_components())
```

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **Phase 1 - Core Integration** ⏱️ 1-2 weeks
- [ ] **Step 1**: Create AI integration layer (`src/ai/heimdall_brain.py`)
- [ ] **Step 1**: Modify GUI to use real AI responses
- [ ] **Step 1**: Add async support to GUI
- [ ] **Step 2**: Implement voice recording functionality
- [ ] **Step 2**: Add voice status indicators
- [ ] **Step 3**: Add screen reading button and functionality
- [ ] **Step 4**: Implement command execution pipeline
- [ ] **Step 4**: Add command handlers (click, scroll, type, read)

### **Phase 2 - Enhanced Integration** ⏱️ 2-3 weeks  
- [ ] **Step 5**: Connect settings panel to actual configuration
- [ ] **Step 5**: Implement persistent settings storage
- [ ] **Step 6**: Save chat messages to database
- [ ] **Step 6**: Load chat history on startup
- [ ] **Step 7**: Add comprehensive error handling
- [ ] **Step 7**: Implement service health checks

### **Phase 3 - Polish & Enhancement** ⏱️ 1-2 weeks
- [ ] **Step 8**: Add loading indicators and animations
- [ ] **Step 8**: Implement keyboard shortcuts
- [ ] **Step 9**: Add caching for performance
- [ ] **Step 9**: Optimize startup time

---

## 🚀 **GETTING STARTED**

### **Immediate Next Steps**:

1. **Create the AI integration layer**:
   ```bash
   mkdir src/ai
   touch src/ai/__init__.py
   # Create src/ai/heimdall_brain.py with the code above
   ```

2. **Test current components individually**:
   ```bash
   python -c "from src.core.voice_handler import VoiceHandler; print('Voice OK')"
   python -c "from src.core.intent_parser import IntentParser; print('Intent OK')"
   ```

3. **Start with Step 1.1** - Create the AI brain integration layer

4. **Test integration incrementally** - Don't try to do everything at once

### **Success Criteria**:
- ✅ GUI shows real AI responses instead of demo text
- ✅ Voice button records and processes speech
- ✅ Screen reading button works and shows actual screen content
- ✅ Basic commands (click, scroll, type) execute successfully

This roadmap provides a clear path from the current beautiful GUI to a fully functional AI assistant. Each step builds on the previous one, ensuring steady progress toward the complete vision.