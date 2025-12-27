
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
        
        # Save main icon (192px for Manifest/Android)
        buffered = io.BytesIO()
        new_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Also create 180x180 for iOS Apple Touch Icon
        img_ios = img.convert("RGB") # Remove alpha for iOS safety (prevent black background)
        img_ios = img_ios.resize((180, 180), Image.Resampling.LANCZOS)
        
        buffered_ios = io.BytesIO()
        img_ios.save(buffered_ios, format="PNG")
        img_str_ios = base64.b64encode(buffered_ios.getvalue()).decode()
        
        # Write to icon_data.py (Storing both is heavy, let's just use file generation in app.py logic... 
        # Actually, let's just save the file directly since we are in local env workflow? 
        # No, better to keep the single source of truth in icon_data.py for simplicity in app.py logic, 
        # OR just update update_icon.py to NOT use icon_data.py but just save files if we were local.
        # But for HF deployment, we relies on code generation.
        # Let's simple add IOS_ICON_BASE64 to icon_data.py
        
        with open("icon_data.py", "w", encoding="utf-8") as f:
            f.write(f'ICON_BASE64 = "{img_str}"\n')
            f.write(f'IOS_ICON_BASE64 = "{img_str_ios}"\n')
            
        print("Success: icon_data.py updated with new image (incl. iOS version).")
        
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    update_icon_from_file()
