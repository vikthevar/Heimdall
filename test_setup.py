#!/usr/bin/env python3
"""
Test script to verify Heimdall setup with free APIs
"""
import asyncio
import sys
from loguru import logger


async def test_whisper():
    """Test local Whisper"""
    try:
        import whisper
        model = whisper.load_model("tiny")  # Use tiny for quick test
        logger.info("✅ Whisper model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Whisper test failed: {e}")
        return False


async def test_tts():
    """Test pyttsx3 TTS"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        logger.info(f"✅ TTS initialized with {len(voices)} voices")
        
        # Test speaking (comment out if you don't want audio)
        # engine.say("Heimdall TTS test successful")
        # engine.runAndWait()
        
        return True
    except Exception as e:
        logger.error(f"❌ TTS test failed: {e}")
        return False


async def test_ollama():
    """Test Ollama connection"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            logger.info(f"✅ Ollama connected. Available models: {model_names}")
            
            if "llama3.2:3b" in model_names:
                logger.info("✅ Llama 3.2 model is available")
            else:
                logger.warning("⚠️  Llama 3.2 model not found. Run: ollama pull llama3.2:3b")
            
            return True
        else:
            logger.error("❌ Ollama server not responding")
            return False
    except Exception as e:
        logger.error(f"❌ Ollama test failed: {e}")
        logger.info("💡 Make sure Ollama is running: ollama serve")
        return False


async def test_ocr():
    """Test Tesseract OCR"""
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Create a simple test image with text
        img_array = np.ones((100, 300, 3), dtype=np.uint8) * 255
        test_image = Image.fromarray(img_array)
        
        # Test OCR (this might not extract text from blank image, but tests if OCR works)
        pytesseract.image_to_string(test_image)
        logger.info("✅ Tesseract OCR is working")
        return True
    except Exception as e:
        logger.error(f"❌ OCR test failed: {e}")
        return False


async def test_screen_capture():
    """Test screenshot capture"""
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        logger.info(f"✅ Screenshot captured: {screenshot.size}")
        return True
    except Exception as e:
        logger.error(f"❌ Screenshot test failed: {e}")
        return False


async def test_database():
    """Test SQLite database"""
    try:
        import aiosqlite
        import os
        
        # Create test database
        os.makedirs("./data", exist_ok=True)
        
        async with aiosqlite.connect("./data/test.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
            await db.execute("INSERT INTO test (id) VALUES (1)")
            await db.commit()
            
            async with db.execute("SELECT COUNT(*) FROM test") as cursor:
                count = (await cursor.fetchone())[0]
                
        logger.info(f"✅ Database test successful: {count} record(s)")
        
        # Clean up
        os.remove("./data/test.db")
        return True
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False


async def test_automation():
    """Test PyAutoGUI"""
    try:
        import pyautogui
        
        # Test basic functions without actually moving mouse
        screen_size = pyautogui.size()
        mouse_pos = pyautogui.position()
        
        logger.info(f"✅ Screen automation ready. Screen: {screen_size}, Mouse: {mouse_pos}")
        return True
    except Exception as e:
        logger.error(f"❌ Automation test failed: {e}")
        return False


async def main():
    """Run all tests"""
    logger.info("🧪 Testing Heimdall Free Setup")
    logger.info("=" * 40)
    
    tests = [
        ("Whisper (Speech Recognition)", test_whisper),
        ("pyttsx3 (Text-to-Speech)", test_tts),
        ("Ollama (Local LLM)", test_ollama),
        ("Tesseract (OCR)", test_ocr),
        ("Screenshot Capture", test_screen_capture),
        ("SQLite Database", test_database),
        ("PyAutoGUI (Automation)", test_automation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 40)
    logger.info("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Heimdall is ready to use.")
        logger.info("💡 Run 'python main.py' to start Heimdall")
    else:
        logger.info("⚠️  Some tests failed. Check the setup instructions.")
        
        if not any(name == "Ollama (Local LLM)" and result for name, result in results):
            logger.info("💡 To fix Ollama issues:")
            logger.info("   1. Install: https://ollama.ai/")
            logger.info("   2. Start: ollama serve")
            logger.info("   3. Pull model: ollama pull llama3.2:3b")


if __name__ == "__main__":
    asyncio.run(main())