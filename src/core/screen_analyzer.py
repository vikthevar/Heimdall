"""
Screen analysis using free OCR and computer vision
"""
import asyncio
from PIL import Image
import pytesseract
import cv2
import numpy as np
from loguru import logger
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import pyautogui

# macOS window enumeration (optional)
try:
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
    )
    QUARTZ_AVAILABLE = True
except Exception:
    QUARTZ_AVAILABLE = False


@dataclass
class ScreenElement:
    text: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    element_type: str  # text, button, input, etc.


class ScreenAnalyzer:
    def __init__(self, ocr_confidence_threshold: float = 0.7):
        """Initialize screen analyzer with free tools"""
        self.ocr_confidence_threshold = ocr_confidence_threshold
        
    async def analyze_screen(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze screen content using OCR and CV"""
        try:
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Extract text with OCR
            text_elements = await self._extract_text(image)
            
            # Detect UI elements
            ui_elements = await self._detect_ui_elements(cv_image)
            
            # Combine results
            analysis = {
                "text_elements": text_elements,
                "ui_elements": ui_elements,
                "full_text": " ".join([elem.text for elem in text_elements]),
                "screen_size": image.size
            }
            
            logger.info(f"Screen analysis complete: {len(text_elements)} text elements, {len(ui_elements)} UI elements")
            return analysis
            
        except Exception as e:
            logger.error(f"Screen analysis error: {e}")
            return {"text_elements": [], "ui_elements": [], "full_text": "", "screen_size": image.size}
    
    async def _extract_text(self, image: Image.Image) -> List[ScreenElement]:
        """Extract text using Tesseract OCR"""
        try:
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            text_elements = []
            n_boxes = len(ocr_data['text'])
            
            for i in range(n_boxes):
                confidence = float(ocr_data['conf'][i])
                text = ocr_data['text'][i].strip()
                
                if confidence > self.ocr_confidence_threshold and text:
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    
                    element = ScreenElement(
                        text=text,
                        bbox=(x, y, w, h),
                        confidence=confidence / 100.0,
                        element_type="text"
                    )
                    text_elements.append(element)
            
            return text_elements
            
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return []
    
    async def _detect_ui_elements(self, cv_image: np.ndarray) -> List[ScreenElement]:
        """Detect UI elements using OpenCV"""
        try:
            ui_elements = []
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Detect buttons using contour detection
            buttons = await self._detect_buttons(gray)
            ui_elements.extend(buttons)
            
            # Detect input fields
            inputs = await self._detect_input_fields(gray)
            ui_elements.extend(inputs)
            
            return ui_elements
            
        except Exception as e:
            logger.error(f"UI element detection error: {e}")
            return []
    
    async def _detect_buttons(self, gray_image: np.ndarray) -> List[ScreenElement]:
        """Detect button-like elements"""
        try:
            buttons = []
            
            # Apply edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter by area and aspect ratio
                area = cv2.contourArea(contour)
                if 500 < area < 50000:  # Reasonable button size
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    # Buttons typically have certain aspect ratios
                    if 0.3 < aspect_ratio < 5.0:
                        button = ScreenElement(
                            text="",  # Will be filled by OCR if text is found
                            bbox=(x, y, w, h),
                            confidence=0.6,
                            element_type="button"
                        )
                        buttons.append(button)
            
            return buttons[:20]  # Limit to prevent too many false positives
            
        except Exception as e:
            logger.error(f"Button detection error: {e}")
            return []
    
    async def _detect_input_fields(self, gray_image: np.ndarray) -> List[ScreenElement]:
        """Detect input field elements"""
        try:
            inputs = []
            
            # Use template matching for common input field patterns
            # This is a simplified approach - could be enhanced with ML models
            
            # Detect rectangular regions that might be input fields
            edges = cv2.Canny(gray_image, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 20000:  # Input field size range
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    # Input fields are typically wider than tall
                    if aspect_ratio > 2.0:
                        input_field = ScreenElement(
                            text="",
                            bbox=(x, y, w, h),
                            confidence=0.5,
                            element_type="input"
                        )
                        inputs.append(input_field)
            
            return inputs[:10]  # Limit results
            
        except Exception as e:
            logger.error(f"Input field detection error: {e}")
            return []
    
    async def find_element_by_text(self, analysis: Dict[str, Any], search_text: str) -> Optional[ScreenElement]:
        """Find screen element containing specific text"""
        search_text = search_text.lower().strip()
        
        for element in analysis.get("text_elements", []):
            if search_text in element.text.lower():
                return element
        
        return None
    
    async def find_elements_by_type(self, analysis: Dict[str, Any], element_type: str) -> List[ScreenElement]:
        """Find all elements of a specific type"""
        elements = []
        
        # Check text elements
        for element in analysis.get("text_elements", []):
            if element.element_type == element_type:
                elements.append(element)
        
        # Check UI elements
        for element in analysis.get("ui_elements", []):
            if element.element_type == element_type:
                elements.append(element)
        
        return elements
    
    def get_element_center(self, element: ScreenElement) -> Tuple[int, int]:
        """Get center coordinates of an element"""
        x, y, w, h = element.bbox
        return (x + w // 2, y + h // 2)

def capture_fullscreen_and_ocr(window_title: str = None) -> str:
    """
    Capture screenshot and extract text using OCR
    
    Args:
        window_title: Optional window title to capture specific window
    
    Returns:
        Extracted text content from the screen
    """
    try:
        # Import window capture function
        from core.screen_controller import capture_window_screenshot
        
        # Capture screenshot (window-specific or fullscreen)
        if window_title:
            screenshot = capture_window_screenshot(window_title)
            source_info = f"Window: {window_title}"
        else:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            source_info = "Full Screen"
        
        if not screenshot:
            return "❌ Failed to capture screenshot"
        
        # Convert to numpy array for processing
        img_array = np.array(screenshot)
        
        # Convert RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale for better OCR
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Apply preprocessing to improve OCR
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.medianBlur(enhanced, 3)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(denoised, config='--psm 6')
        
        # Also detect UI elements
        ui_elements = detect_ui_elements(img_bgr)
        
        # Clean up the text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        # Format result
        result = f"📖 **Screen Analysis ({source_info}):**\n\n"
        
        if cleaned_text:
            result += f"**Text Content:**\n{cleaned_text}\n\n"
        
        if ui_elements:
            result += f"**UI Elements Detected:**\n"
            for element in ui_elements[:10]:  # Limit to first 10
                result += f"• {element['type']}: {element['description']}\n"
        
        if not cleaned_text and not ui_elements:
            result += "No readable text or UI elements found. The screen may contain mostly images or graphics."
        
        return result
    
    except Exception as e:
        logger.error(f"Screen capture and OCR failed: {e}")
        return f"❌ Failed to capture and analyze screen: {str(e)}"

def detect_ui_elements(img_bgr: np.ndarray) -> List[Dict[str, Any]]:
    """
    Detect UI elements in the image
    
    Args:
        img_bgr: OpenCV image in BGR format
        
    Returns:
        List of detected UI elements
    """
    elements = []
    
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Detect buttons using edge detection
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 50000:  # Reasonable button size
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Classify based on aspect ratio and size
                if 0.3 < aspect_ratio < 5.0:
                    if aspect_ratio > 2.0:
                        element_type = "input_field"
                    else:
                        element_type = "button"
                    
                    elements.append({
                        'type': element_type,
                        'description': f"{element_type} at ({x+w//2}, {y+h//2})",
                        'bbox': (x, y, w, h),
                        'center': (x + w//2, y + h//2)
                    })
        
        # Detect window controls (close, minimize, maximize buttons)
        height, width = gray.shape
        
        # Look for close button in top-right
        top_right = gray[0:50, width-100:width]
        if top_right.size > 0:
            # Look for circular or square patterns
            circles = cv2.HoughCircles(top_right, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=5, maxRadius=25)
            if circles is not None:
                elements.append({
                    'type': 'close_button',
                    'description': 'Close button (top-right)',
                    'center': (width - 50, 25)
                })
        
        return elements[:20]  # Limit results
    
    except Exception as e:
        logger.error(f"UI element detection failed: {e}")
        return []


def list_open_windows() -> List[Dict[str, Any]]:
    """
    List open on-screen windows with titles and bounds (macOS only).
    Returns empty list on unsupported platforms or permission issues.
    """
    try:
        if not QUARTZ_AVAILABLE:
            return []
        window_info = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        windows: List[Dict[str, Any]] = []
        for w in window_info:
            title = w.get('kCGWindowName') or ''
            owner = w.get('kCGWindowOwnerName') or ''
            bounds = w.get('kCGWindowBounds') or {}
            number = w.get('kCGWindowNumber')
            if title or owner:
                windows.append({
                    'id': number,
                    'title': title,
                    'owner': owner,
                    'bounds': bounds,
                })
        return windows
    except Exception as e:
        logger.error(f"Window list failed: {e}")
        return []


def capture_window_and_ocr(window_id: int) -> str:
    """
    Capture a specific window by id and extract text using OCR (macOS).
    Falls back to fullscreen if window not found.
    """
    try:
        if not QUARTZ_AVAILABLE:
            return capture_fullscreen_and_ocr()
        windows = list_open_windows()
        match = next((w for w in windows if int(w['id']) == int(window_id)), None)
        if not match:
            return capture_fullscreen_and_ocr()
        b = match['bounds']
        x, y, w, h = int(b.get('X', 0)), int(b.get('Y', 0)), int(b.get('Width', 0)), int(b.get('Height', 0))
        if w <= 0 or h <= 0:
            return capture_fullscreen_and_ocr()
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        img_array = np.array(screenshot)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        denoised = cv2.medianBlur(enhanced, 3)
        text = pytesseract.image_to_string(denoised, config='--psm 6')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        if cleaned_text:
            owner = match.get('owner') or 'Window'
            title = match.get('title') or ''
            header = f"📖 **{owner} — {title}**\n\n" if title else f"📖 **{owner}**\n\n"
            return header + cleaned_text
        else:
            return "📖 Window captured but no readable text found."
    except Exception as e:
        logger.error(f"Window capture and OCR failed: {e}")
        return f"❌ Failed to capture window: {str(e)}"