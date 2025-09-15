#!/usr/bin/env python3
"""
Test and configure Tesseract for Heimdall
"""
import os
import platform
import pytesseract
from PIL import Image, ImageDraw, ImageFont

def configure_tesseract():
    """Configure Tesseract path"""
    if platform.system() == "Windows":
        # Common Tesseract installation paths on Windows
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\tools\tesseract\tesseract.exe",
            r"C:\tesseract\tesseract.exe"
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Tesseract configured at: {path}")
                return path
        
        print("❌ Tesseract not found in common locations")
        return None
    else:
        print("ℹ️ Non-Windows system, using default Tesseract path")
        return "tesseract"

def test_tesseract():
    """Test Tesseract functionality"""
    try:
        # Configure first
        tesseract_path = configure_tesseract()
        if not tesseract_path:
            return False
        
        # Test version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        
        # Create test image
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 30), "Hello Heimdall OCR Test", fill='black', font=font)
        
        # Test OCR
        text = pytesseract.image_to_string(img)
        print(f"✅ OCR Test Result: '{text.strip()}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Tesseract test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TESSERACT CONFIGURATION TEST")
    print("=" * 40)
    
    success = test_tesseract()
    
    if success:
        print("\n🎉 Tesseract is working!")
        print("✅ OCR functionality ready for Heimdall")
    else:
        print("\n❌ Tesseract configuration failed")
        print("📋 Please check Tesseract installation")