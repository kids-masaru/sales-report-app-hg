
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def generate_base64_icon():
    # Square Canvas for Icon
    W, H = 192, 192
    
    # White background for icon (better for home screen)
    img = Image.new('RGB', (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Scale factors
    scale = 1.6
    offset_x = 20
    offset_y = 20

    # --- Draw Icon (Centered) ---
    # Document (Blue)
    # Original: x=10, y=10, w=80, h=100
    doc_x, doc_y = 10 * scale + offset_x, 10 * scale + offset_y
    doc_w, doc_h = 80 * scale, 100 * scale
    doc_color = (79, 172, 254) # #4facfe
    
    draw.rounded_rectangle([doc_x, doc_y, doc_x + doc_w, doc_y + doc_h], radius=15, fill=doc_color)
    
    # White lines on doc
    line_color = (255, 255, 255, 230)
    for y in [35, 55, 75]:
        ly = y * scale + offset_y
        draw.rectangle([doc_x + 15*scale, ly, doc_x + 65*scale, ly + 6*scale], fill=line_color)

    # Chat Bubble (Orange)
    # Original: x=60, y=60
    bubble_x, bubble_y = 60 * scale + offset_x, 60 * scale + offset_y
    bubble_w, bubble_h = 60 * scale, 40 * scale
    bubble_color = (255, 159, 28) # #FF9F1C
    
    # Draw tail
    # Original: (68, 95), (88, 95), (68, 115)
    # Scaled relative to bubble pos
    tail_pts = [
        (bubble_x + 8*scale, bubble_y + 35*scale),
        (bubble_x + 28*scale, bubble_y + 35*scale),
        (bubble_x + 8*scale, bubble_y + 55*scale)
    ]
    draw.polygon(tail_pts, fill=bubble_color)
    
    # Draw body
    draw.rounded_rectangle([bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h], radius=15, fill=bubble_color, outline=(255,255,255), width=3)
    
    # Question mark
    # text '?' centered in bubble
    try:
        font_q = ImageFont.truetype("arial.ttf", int(30 * scale))
    except:
        font_q = ImageFont.load_default()
        
    draw.text((bubble_x + bubble_w/2, bubble_y + bubble_h/2), "?", font=font_q, fill="white", anchor="mm")

    with open("icon_data.py", "w", encoding="utf-8") as f:
        f.write(f'ICON_BASE64 = "{img_str}"\n')
    print("icon_data.py created")

if __name__ == "__main__":
    generate_base64_icon()
