#!/usr/bin/env python3
"""
Create placeholder icons for Heimdall UI
Run this script to generate basic icons if you don't have custom ones
"""
from PIL import Image, ImageDraw, ImageFont
import os
import math


def create_gradient_background(size, color1, color2):
    """Create a gradient background"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    for i in range(size[1]):
        # Calculate gradient color
        ratio = i / size[1]
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        
        draw.line([(0, i), (size[0], i)], fill=(r, g, b, 255))
    
    return img, draw


def create_main_icon():
    """Create the main Heimdall application icon"""
    size = (256, 256)
    
    # Create gradient background
    img, draw = create_gradient_background(size, (102, 126, 234), (118, 75, 162))
    
    # Add circular border
    center = (128, 128)
    radius = 110
    
    # Draw outer circle (border)
    draw.ellipse([center[0] - radius, center[1] - radius, 
                  center[0] + radius, center[1] + radius], 
                 outline="white", width=8)
    
    # Draw inner circle
    inner_radius = 90
    draw.ellipse([center[0] - inner_radius, center[1] - inner_radius,
                  center[0] + inner_radius, center[1] + inner_radius],
                 fill=(255, 255, 255, 50))
    
    # Draw "H" letter
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 100)
        except:
            font = ImageFont.load_default()
    
    # Draw letter with shadow
    draw.text((130, 130), "H", font=font, fill=(0, 0, 0, 100), anchor="mm")  # Shadow
    draw.text((128, 128), "H", font=font, fill="white", anchor="mm")  # Main text
    
    return img


def create_avatar_icon():
    """Create AI avatar icon"""
    size = (40, 40)
    
    # Create gradient background
    img, draw = create_gradient_background(size, (102, 126, 234), (118, 75, 162))
    
    # Make it circular
    mask = Image.new('L', size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([0, 0, size[0], size[1]], fill=255)
    
    # Apply circular mask
    img.putalpha(mask)
    
    # Draw "H" letter
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
    
    draw.text((20, 20), "H", font=font, fill="white", anchor="mm")
    
    return img


def create_microphone_icon():
    """Create microphone icon"""
    size = (24, 24)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw microphone shape
    # Microphone body
    draw.ellipse([8, 4, 16, 14], fill=(102, 126, 234), outline="white", width=1)
    
    # Microphone stand
    draw.line([12, 14, 12, 18], fill=(102, 126, 234), width=2)
    draw.line([9, 18, 15, 18], fill=(102, 126, 234), width=2)
    
    # Sound waves
    draw.arc([4, 8, 8, 12], 270, 90, fill=(102, 126, 234), width=1)
    draw.arc([16, 8, 20, 12], 90, 270, fill=(102, 126, 234), width=1)
    
    return img


def create_settings_icon():
    """Create settings gear icon"""
    size = (24, 24)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center = (12, 12)
    
    # Draw gear teeth
    for i in range(8):
        angle = i * 45
        x1 = center[0] + 8 * math.cos(math.radians(angle))
        y1 = center[1] + 8 * math.sin(math.radians(angle))
        x2 = center[0] + 10 * math.cos(math.radians(angle))
        y2 = center[1] + 10 * math.sin(math.radians(angle))
        draw.line([x1, y1, x2, y2], fill=(102, 126, 234), width=2)
    
    # Draw center circle
    draw.ellipse([8, 8, 16, 16], fill=(102, 126, 234))
    draw.ellipse([10, 10, 14, 14], fill="white")
    
    return img


def create_theme_icon():
    """Create theme toggle icon (sun/moon)"""
    size = (24, 24)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw moon shape
    draw.ellipse([6, 6, 18, 18], fill=(102, 126, 234))
    draw.ellipse([8, 4, 18, 16], fill=(0, 0, 0, 0))  # Create crescent
    
    return img


def main():
    """Create all placeholder icons"""
    # Create assets directory
    os.makedirs("assets", exist_ok=True)
    
    print("Creating Heimdall UI icons...")
    
    # Create main application icon
    main_icon = create_main_icon()
    main_icon.save("assets/heimdall_icon.png")
    print("✅ Created heimdall_icon.png")
    
    # Create avatar icon
    avatar_icon = create_avatar_icon()
    avatar_icon.save("assets/avatar_ai.png")
    print("✅ Created avatar_ai.png")
    
    # Create UI icons
    mic_icon = create_microphone_icon()
    mic_icon.save("assets/microphone_icon.png")
    print("✅ Created microphone_icon.png")
    
    settings_icon = create_settings_icon()
    settings_icon.save("assets/settings_icon.png")
    print("✅ Created settings_icon.png")
    
    theme_icon = create_theme_icon()
    theme_icon.save("assets/theme_icon.png")
    print("✅ Created theme_icon.png")
    
    print("\n🎉 All icons created successfully!")
    print("📁 Icons saved in ./assets/ directory")
    print("💡 You can replace these with custom designs later")


if __name__ == "__main__":
    main()