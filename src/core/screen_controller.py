"""
Screen control using PyAutoGUI
"""
import asyncio
import pyautogui
from loguru import logger
from typing import Tuple, Optional
import time


class ScreenController:
    def __init__(self):
        """Initialize screen controller"""
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1  # Small pause between actions
        
    async def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> bool:
        """Click at specific coordinates"""
        try:
            logger.info(f"Clicking at ({x}, {y}) with {button} button")
            
            # Run in executor to make it async
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                lambda: pyautogui.click(x, y, clicks=clicks, button=button)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Click error: {e}")
            return False
    
    async def double_click(self, x: int, y: int) -> bool:
        """Double click at coordinates"""
        return await self.click(x, y, clicks=2)
    
    async def right_click(self, x: int, y: int) -> bool:
        """Right click at coordinates"""
        return await self.click(x, y, button="right")
    
    async def scroll(self, direction: str = "down", clicks: int = 3) -> bool:
        """Scroll in specified direction"""
        try:
            scroll_amount = clicks if direction == "down" else -clicks
            
            logger.info(f"Scrolling {direction} by {abs(scroll_amount)} clicks")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: pyautogui.scroll(scroll_amount)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Scroll error: {e}")
            return False
    
    async def type_text(self, text: str, interval: float = 0.01) -> bool:
        """Type text with specified interval between characters"""
        try:
            logger.info(f"Typing text: {text}")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: pyautogui.typewrite(text, interval=interval)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Type text error: {e}")
            return False
    
    async def press_key(self, key: str) -> bool:
        """Press a specific key"""
        try:
            logger.info(f"Pressing key: {key}")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: pyautogui.press(key)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Key press error: {e}")
            return False
    
    async def key_combination(self, *keys) -> bool:
        """Press key combination (e.g., ctrl+c)"""
        try:
            logger.info(f"Pressing key combination: {'+'.join(keys)}")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: pyautogui.hotkey(*keys)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Key combination error: {e}")
            return False
    
    async def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Move mouse to coordinates"""
        try:
            logger.info(f"Moving mouse to ({x}, {y})")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: pyautogui.moveTo(x, y, duration=duration)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Mouse move error: {e}")
            return False
    
    async def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                  duration: float = 1.0, button: str = "left") -> bool:
        """Drag from start to end coordinates"""
        try:
            logger.info(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: pyautogui.drag(end_x - start_x, end_y - start_y, 
                                     duration=duration, button=button)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Drag error: {e}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return pyautogui.position()
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        return pyautogui.size()
    
    async def wait_for_element(self, image_path: str, timeout: int = 10) -> Optional[Tuple[int, int]]:
        """Wait for an element to appear on screen (using image matching)"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                    if location:
                        center = pyautogui.center(location)
                        logger.info(f"Element found at {center}")
                        return center
                except pyautogui.ImageNotFoundException:
                    pass
                
                await asyncio.sleep(0.5)
            
            logger.warning(f"Element not found within {timeout} seconds")
            return None
            
        except Exception as e:
            logger.error(f"Wait for element error: {e}")
            return None