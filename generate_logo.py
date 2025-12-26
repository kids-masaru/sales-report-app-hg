
from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    # Canvas
    W, H = 450, 120
    # Transparent background
    img = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # --- Draw Icon (Left) ---
    # Document (Blue)
    # x=10, y=10, w=80, h=100
    doc_color = (79, 172, 254) # #4facfe
    # PIL doesn't have native drop shadow easily, skip shadow for simplicity or fake it
    # Fake shadow
    shadow_color = (0, 0, 0, 50)
    draw.rounded_rectangle([12, 12, 92, 112], radius=10, fill=shadow_color)
    draw.rounded_rectangle([10, 10, 90, 110], radius=10, fill=doc_color)
    
    # White lines on doc
    line_color = (255, 255, 255, 230)
    for y in [35, 55, 75]:
        draw.rectangle([25, y, 75, y+6], fill=line_color)

    # Chat Bubble (Orange)
    # x=60, y=60
    bubble_color = (255, 159, 28) # #FF9F1C
    bubble_bg = [60, 60, 120, 100] # Rect part
    
    # Draw shadow first
    draw.rounded_rectangle([62, 62, 122, 102], radius=10, fill=shadow_color)
    # Tail shadow
    draw.polygon([(70, 100), (90, 100), (70, 117)], fill=shadow_color)

    # Draw tail
    draw.polygon([(68, 95), (88, 95), (68, 115)], fill=bubble_color)
    # Draw body
    draw.rounded_rectangle([60, 60, 120, 100], radius=10, fill=bubble_color, outline=(255,255,255), width=2)
    
    # Question mark
    # text '?' centered in bubble (90, 80)
    try:
        # Use arial for symbol? or same japon font
        font_q = ImageFont.truetype("arial.ttf", 30)
    except:
        font_q = ImageFont.load_default()
        
    draw.text((90, 80), "?", font=font_q, fill="white", anchor="mm")

    # --- Draw Text (Right) ---
    text = "営業報告アプリ"
    font_path = "C:/Windows/Fonts/meiryo.ttc" # Try Meiryo first
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/msgothic.ttc"
    
    try:
        font = ImageFont.truetype(font_path, 40)
        draw.text((140, 60), text, font=font, fill="#333333", anchor="lm") # Left Middle
    except Exception as e:
        print(f"Font error: {e}")
        # Fallback to default (ugly but works)
        draw.text((140, 60), text, fill="#333333", anchor="lm")

    # Save
    if not os.path.exists('assets'):
        os.makedirs('assets')
    img.save('assets/logo.png')
    print("Logo generated at assets/logo.png")

if __name__ == "__main__":
    create_logo()
