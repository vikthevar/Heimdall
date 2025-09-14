"""
Free intent parsing using local Ollama LLM
"""
import asyncio
import json
import requests
from loguru import logger
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ParsedIntent(BaseModel):
    action: str
    target: Optional[str] = None
    parameters: Dict[str, Any] = {}
    confidence: float = 0.0


class IntentParser:
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        """Initialize with local Ollama"""
        self.ollama_host = ollama_host
        self.model = model
        self.session = requests.Session()
        
    async def initialize(self):
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = self.session.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code != 200:
                raise Exception("Ollama server not responding")
            
            # Check if model is available
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            if self.model not in model_names:
                logger.warning(f"Model {self.model} not found. Available models: {model_names}")
                logger.info(f"Pulling model {self.model}...")
                await self._pull_model()
            
            logger.info(f"Ollama initialized with model: {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            logger.info("Please install and start Ollama: https://ollama.ai/")
            raise
    
    async def _pull_model(self):
        """Pull the model if not available"""
        try:
            response = self.session.post(
                f"{self.ollama_host}/api/pull",
                json={"name": self.model},
                timeout=300  # 5 minutes for model download
            )
            if response.status_code == 200:
                logger.info(f"Model {self.model} pulled successfully")
            else:
                raise Exception(f"Failed to pull model: {response.text}")
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            raise
    
    async def parse_command(self, user_input: str, screen_context: str = "") -> ParsedIntent:
        """Parse user command into structured intent"""
        try:
            prompt = self._build_prompt(user_input, screen_context)
            
            response = await self._call_ollama(prompt)
            
            # Parse the JSON response
            try:
                result = json.loads(response)
                return ParsedIntent(**result)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                return self._fallback_parse(user_input)
                
        except Exception as e:
            logger.error(f"Intent parsing error: {e}")
            return self._fallback_parse(user_input)
    
    def _build_prompt(self, user_input: str, screen_context: str) -> str:
        """Build the prompt for intent parsing"""
        return f"""You are an AI assistant that parses voice commands for screen automation.

Parse this user command into a JSON object with these fields:
- action: The main action (click, scroll, type, read, navigate, etc.)
- target: What to interact with (button text, element description, etc.)
- parameters: Additional parameters like direction, text to type, etc.
- confidence: Your confidence in the parsing (0.0 to 1.0)

Screen context: {screen_context[:500] if screen_context else "No screen context available"}

User command: "{user_input}"

Respond ONLY with valid JSON:"""
    
    async def _call_ollama(self, prompt: str) -> str:
        """Make async call to Ollama"""
        try:
            loop = asyncio.get_event_loop()
            
            def _make_request():
                response = self.session.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "max_tokens": 200
                        }
                    },
                    timeout=30
                )
                return response.json()["response"]
            
            return await loop.run_in_executor(None, _make_request)
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def _fallback_parse(self, user_input: str) -> ParsedIntent:
        """Simple fallback parsing when LLM fails"""
        user_input = user_input.lower().strip()
        
        # Simple keyword matching
        if any(word in user_input for word in ["click", "press", "tap"]):
            return ParsedIntent(
                action="click",
                target=user_input.replace("click", "").replace("press", "").replace("tap", "").strip(),
                confidence=0.5
            )
        elif any(word in user_input for word in ["scroll", "move"]):
            direction = "down"
            if "up" in user_input:
                direction = "up"
            return ParsedIntent(
                action="scroll",
                parameters={"direction": direction},
                confidence=0.5
            )
        elif any(word in user_input for word in ["read", "what", "tell"]):
            return ParsedIntent(
                action="read",
                confidence=0.5
            )
        elif any(word in user_input for word in ["type", "write", "enter"]):
            return ParsedIntent(
                action="type",
                target=user_input,
                confidence=0.5
            )
        else:
            return ParsedIntent(
                action="unknown",
                target=user_input,
                confidence=0.1
            )