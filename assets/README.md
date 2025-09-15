# Heimdall Assets

This directory contains visual assets for the Heimdall AI Assistant.

## Required Assets

### Icons
- `heimdall_icon.png` - Main application icon (256x256px)
- `heimdall_icon.ico` - Windows icon format
- `heimdall_icon.icns` - macOS icon format

### UI Elements
- `avatar_ai.png` - AI assistant avatar (40x40px)
- `microphone_icon.svg` - Microphone button icon
- `settings_icon.svg` - Settings button icon
- `theme_icon.svg` - Theme toggle icon

## Creating Icons

You can create these icons using any image editor. Here are the recommended specifications:

### Main Icon (`heimdall_icon.png`)
- Size: 256x256 pixels
- Format: PNG with transparency
- Style: Modern, minimalist design
- Colors: Use the app's primary colors (#667eea, #764ba2)
- Content: Could be an "H" letter, eye symbol, or Norse-inspired design

### Avatar (`avatar_ai.png`)
- Size: 40x40 pixels
- Format: PNG with transparency
- Style: Simple, friendly AI representation
- Could be: Geometric shape, robot face, or stylized "H"

## Placeholder Creation

If you don't have custom icons, you can create simple placeholders:

```python
# Simple icon creation script
from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_icon():
    # Create main icon
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for i in range(256):
        color = (102 + i//4, 126 + i//4, 234, 255)
        draw.rectangle([i, i, 256-i, 256-i], outline=color)
    
    # Draw "H" letter
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()
    
    draw.text((128, 128), "H", font=font, fill="white", anchor="mm")
    
    img.save("assets/heimdall_icon.png")
    print("Created heimdall_icon.png")

if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    create_placeholder_icon()
```

## Usage in Application

The icons are referenced in the GUI code:
- Main window icon: `QIcon("assets/heimdall_icon.png")`
- System tray icon: `QSystemTrayIcon(QIcon("assets/heimdall_icon.png"))`
- Avatar images: Used in chat bubbles and UI elements

## License

All assets should be either:
1. Created by you (original work)
2. Licensed for commercial use
3. Public domain
4. Creative Commons licensed

Make sure to document the source and license of any third-party assets.