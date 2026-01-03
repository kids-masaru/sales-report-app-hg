
from PIL import Image
import os
import shutil

# Source path (Artifact)
SOURCE_IMAGE_PATH = r"C:\Users\HP\.gemini\antigravity\brain\bdf098ed-072d-4f4a-801c-4feb0ab7ac6d\uploaded_image_1767404023731.png"

# Destination directory
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

def update_icons():
    try:
        # Open source image
        img = Image.open(SOURCE_IMAGE_PATH)
        
        # 1. Standard Icon (192x192) - useful for Android/Favicon
        icon_size = (192, 192)
        img_icon = img.resize(icon_size, Image.Resampling.LANCZOS)
        img_icon.save(os.path.join(STATIC_DIR, "icon.png"))
        print(f"Saved static/icon.png ({icon_size})")

        # 2. Apple Touch Icon (180x180) - iPhone Home Screen
        ios_size = (180, 180)
        img_ios = img.resize(ios_size, Image.Resampling.LANCZOS)
        img_ios.save(os.path.join(STATIC_DIR, "apple-touch-icon.png"))
        print(f"Saved static/apple-touch-icon.png ({ios_size})")
        
    except Exception as e:
        print(f"Error updating icons: {e}")

if __name__ == "__main__":
    update_icons()
