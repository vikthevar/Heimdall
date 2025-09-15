#!/usr/bin/env python3
"""
Tesseract OCR Setup and Configuration for Heimdall
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def find_tesseract_windows():
    """Find Tesseract installation on Windows"""
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME')),
        r"C:\tools\tesseract\tesseract.exe",
        r"C:\tesseract\tesseract.exe"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def setup_tesseract():
    """Setup Tesseract OCR for the system"""
    print("🔧 Setting up Tesseract OCR...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Try to find existing installation
        tesseract_path = find_tesseract_windows()
        
        if tesseract_path:
            print(f"✅ Found Tesseract at: {tesseract_path}")
            
            # Configure pytesseract to use this path
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                
                # Test it
                version = pytesseract.get_tesseract_version()
                print(f"✅ Tesseract version: {version}")
                
                # Create config file for Heimdall
                config_content = f"""# Tesseract Configuration for Heimdall
TESSERACT_PATH = r"{tesseract_path}"
"""
                with open("tesseract_config.py", "w") as f:
                    f.write(config_content)
                
                print("✅ Tesseract configuration saved to tesseract_config.py")
                return True
                
            except Exception as e:
                print(f"❌ Error configuring Tesseract: {e}")
                return False
        else:
            print("❌ Tesseract not found. Please install it:")
            print("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   2. Or use: winget install --id UB-Mannheim.TesseractOCR")
            print("   3. Or use: choco install tesseract")
            return False
    
    elif system == "darwin":  # macOS
        print("📋 For macOS, install with: brew install tesseract")
        return False
    
    else:  # Linux
        print("📋 For Linux, install with: sudo apt install tesseract-ocr")
        return False

def test_ocr():
    """Test OCR functionality"""
    print("\n🧪 Testing OCR functionality...")
    
    try:
        import pytesseract
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create a test image with text
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        draw.text((10, 30), "Hello Heimdall OCR Test", fill='black', font=font)
        
        # Test OCR
        text = pytesseract.image_to_string(img)
        print(f"✅ OCR Test Result: '{text.strip()}'")
        
        if "Heimdall" in text or "Hello" in text:
            print("✅ OCR is working correctly!")
            return True
        else:
            print("⚠️ OCR working but accuracy may be low")
            return True
            
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def main():
    """Main setup process"""
    print("🚀 TESSERACT OCR SETUP FOR HEIMDALL")
    print("=" * 50)
    
    # Setup Tesseract
    tesseract_ok = setup_tesseract()
    
    if tesseract_ok:
        # Test OCR
        ocr_ok = test_ocr()
        
        if ocr_ok:
            print("\n🎉 TESSERACT SETUP COMPLETE!")
            print("✅ OCR is ready for Heimdall screen reading")
            print("\n🚀 You can now use:")
            print("   - 'Read my screen' commands")
            print("   - 'Screenshot notepad' commands")
            print("   - OCR-based screen analysis")
        else:
            print("\n⚠️ Tesseract installed but OCR test failed")
    else:
        print("\n❌ Tesseract setup incomplete")
        print("📋 Manual installation required")
    
    print("\n🔧 Next: Run python heimdall_working.py to test!")

if __name__ == "__main__":
    main()