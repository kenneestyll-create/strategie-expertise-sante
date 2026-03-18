"""
Test script: Generate a realistic test image of a white document on a wood-like background,
then verify the scanner worker can process it via a headless browser test.
"""
from PIL import Image, ImageDraw, ImageFont
import random
import os

def create_test_image(path, width=1920, height=1440):
    """Create a realistic photo: white document on textured colored background."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Wood-like background with color variation
    for y in range(height):
        for x in range(0, width, 4):
            r = 140 + random.randint(-20, 20) + (y % 30)
            g = 100 + random.randint(-15, 15) + (y % 25)
            b = 60 + random.randint(-10, 10) + (y % 20)
            for dx in range(4):
                if x + dx < width:
                    img.putpixel((x + dx, y), (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))))
    
    # White document (slightly rotated trapezoid to simulate perspective)
    doc_points = [
        (350, 200),   # top-left
        (1550, 180),  # top-right  
        (1600, 1250), # bottom-right
        (300, 1280),  # bottom-left
    ]
    draw.polygon(doc_points, fill=(252, 252, 250))
    
    # Add some text lines on the document
    for i in range(15):
        y = 280 + i * 60
        x_start = 420 + i * 2
        line_w = random.randint(500, 900)
        draw.rectangle([x_start, y, x_start + line_w, y + 8], fill=(40, 40, 40))
    
    # Add shadow under document
    shadow_points = [(p[0]+8, p[1]+8) for p in doc_points]
    # Draw shadow first then document
    temp = Image.new('RGB', (width, height))
    temp_draw = ImageDraw.Draw(temp)
    temp_draw.polygon(shadow_points, fill=(80, 60, 40))
    temp_draw.polygon(doc_points, fill=(252, 252, 250))
    for i in range(15):
        y = 280 + i * 60
        x_start = 420 + i * 2
        line_w = random.randint(500, 900)
        temp_draw.rectangle([x_start, y, x_start + line_w, y + 8], fill=(40, 40, 40))
    
    # Composite: background + document with shadow
    # Reuse the wood background, paste document area
    for y in range(height):
        for x in range(width):
            tp = temp.getpixel((x, y))
            if tp != (0, 0, 0):
                img.putpixel((x, y), tp)
    
    img.save(path, 'JPEG', quality=90)
    print(f"Test image saved: {path} ({width}x{height})")

if __name__ == '__main__':
    os.makedirs('/app/frontend/public/test', exist_ok=True)
    create_test_image('/app/frontend/public/test/doc_on_wood.jpg')
    print("Done!")
