
from PIL import Image
import io
import base64
import os

def update_icon_from_file():
    # Target Image Path
    image_path = r"C:/Users/HP/.gemini/antigravity/brain/a2566c48-a432-4027-96d0-7c2afc3a135f/uploaded_image_0_1766762315198.png"
    
    if not os.path.exists(image_path):
        print(f"Error: File not found at {image_path}")
        return

    try:
        img = Image.open(image_path)
        
        # Convert to RGB (remove alpha capabilities if jpg, but keep for icon transparency)
        # Actually for PWA icon, transparency is fine.
        img = img.convert("RGBA")
        
        # Resize to square 192x192 (contain aspect ratio)
        target_size = (192, 192)
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Create a new square background (white)
        # new_img = Image.new("RGBA", target_size, (255, 255, 255, 255))
        # Or transparent? White is safer for Home Screen icons on iOS usually to avoid black artifacts
        new_img = Image.new("RGB", target_size, (255, 255, 255))
        
        # Center the image
        left = (target_size[0] - img.width) // 2
        top = (target_size[1] - img.height) // 2
        new_img.paste(img, (left, top), img)
        
        # Save to buffer
        buffered = io.BytesIO()
        new_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Write to icon_data.py
        with open("icon_data.py", "w", encoding="utf-8") as f:
            f.write(f'ICON_BASE64 = "{img_str}"\n')
            
        print("Success: icon_data.py updated with new image.")
        
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    update_icon_from_file()
