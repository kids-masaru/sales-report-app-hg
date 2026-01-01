
from PIL import Image
import io
import base64
import os

def update_icon_from_image():
    src_path = "src_icon.png"
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found.")
        return

    try:
        # Open source image
        img = Image.open(src_path)
        
        # 1. Standard Icon (favicon/app icon) - 192x192
        # Use high quality resampling
        img_std = img.resize((192, 192), Image.Resampling.LANCZOS)
        
        # Convert to PNG bytes
        buffer_std = io.BytesIO()
        img_std.save(buffer_std, format="PNG")
        icon_base64 = base64.b64encode(buffer_std.getvalue()).decode("utf-8")

        # 2. iOS Icon (Apple Touch Icon) - 180x180 (Standard for iPhone)
        # iOS adds its own rounded corners, so we usually provide a square image.
        # However, to be safe and ensure it looks good, we can just use the same image
        # or resize specifically to 180x180.
        img_ios = img.resize((180, 180), Image.Resampling.LANCZOS)
        
        # Convert to PNG bytes
        buffer_ios = io.BytesIO()
        img_ios.save(buffer_ios, format="PNG")
        ios_icon_base64 = base64.b64encode(buffer_ios.getvalue()).decode("utf-8")

        # Write to icon_data.py
        with open("icon_data.py", "w", encoding="utf-8") as f:
            f.write(f'ICON_BASE64 = "{icon_base64}"\n')
            f.write(f'IOS_ICON_BASE64 = "{ios_icon_base64}"\n')
            
        print("Success: icon_data.py updated with new image data.")
        
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    update_icon_from_image()
