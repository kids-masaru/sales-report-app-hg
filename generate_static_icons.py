
import base64
import os
from icon_data import ICON_BASE64, IOS_ICON_BASE64

if not os.path.exists("static"):
    os.makedirs("static")

with open("static/icon.png", "wb") as f:
    f.write(base64.b64decode(ICON_BASE64))
    
with open("static/apple-touch-icon.png", "wb") as f:
    f.write(base64.b64decode(IOS_ICON_BASE64))

print("Icons generated in static/")
