"""
Screenshot capture functionality
"""
import asyncio
from PIL import Image, ImageGrab
import os
from datetime import datetime
from loguru import logger
from typing import Optional, Tuple
import numpy as np


class ScreenshotCapturer:
    def __init__(self, screenshots_path: str = "./data/screenshots"):
        """Initialize screenshot capturer"""
        self.screenshots_path = screenshots_path
        self.ensure_directory()
    
    def ensure_directory(self):
        """Create screenshots directory if it doesn't exist"""
        os.makedirs(self.screenshots_path, exist_ok=True)
    
    async def capture_screen(self, save_to_disk: bool = True) -> Tuple[Image.Image, Optional[str]]:
        """Capture current screen"""
        try:
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            filepath = None
            if save_to_disk:
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                filepath = os.path.join(self.screenshots_path, filename)
                
                # Save screenshot
                screenshot.save(filepath, "PNG", optimize=True)
                logger.info(f"Screenshot saved: {filepath}")
            
            return screenshot, filepath
            
        except Exception as e:
            logger.error(f"Screenshot capture error: {e}")
            raise
    
    async def capture_region(self, x: int, y: int, width: int, height: int, 
                           save_to_disk: bool = False) -> Tuple[Image.Image, Optional[str]]:
        """Capture specific screen region"""
        try:
            # Capture region
            bbox = (x, y, x + width, y + height)
            screenshot = ImageGrab.grab(bbox=bbox)
            
            filepath = None
            if save_to_disk:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"region_{timestamp}.png"
                filepath = os.path.join(self.screenshots_path, filename)
                screenshot.save(filepath, "PNG", optimize=True)
                logger.info(f"Region screenshot saved: {filepath}")
            
            return screenshot, filepath
            
        except Exception as e:
            logger.error(f"Region capture error: {e}")
            raise
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get current screen dimensions"""
        try:
            screenshot = ImageGrab.grab()
            return screenshot.size
        except Exception as e:
            logger.error(f"Error getting screen size: {e}")
            return (1920, 1080)  # Default fallback
    
    async def cleanup_old_screenshots(self, max_age_hours: int = 24):
        """Remove old screenshots to save disk space"""
        try:
            current_time = datetime.now()
            removed_count = 0
            
            for filename in os.listdir(self.screenshots_path):
                if filename.endswith('.png'):
                    filepath = os.path.join(self.screenshots_path, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    
                    age_hours = (current_time - file_time).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        os.remove(filepath)
                        removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old screenshots")
                
        except Exception as e:
            logger.error(f"Screenshot cleanup error: {e}")
    
    def image_to_numpy(self, image: Image.Image) -> np.ndarray:
        """Convert PIL Image to numpy array"""
        return np.array(image)
    
    def numpy_to_image(self, array: np.ndarray) -> Image.Image:
        """Convert numpy array to PIL Image"""
        return Image.fromarray(array)