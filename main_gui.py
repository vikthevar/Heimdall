#!/usr/bin/env python3
"""
Heimdall GUI Application Entry Point
Modern desktop interface for the AI voice assistant
"""
import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.ui.gui_main import main

if __name__ == "__main__":
    # Ensure data directories exist
    os.makedirs("./data/logs", exist_ok=True)
    os.makedirs("./data/screenshots", exist_ok=True)
    
    # Run GUI application
    sys.exit(main())