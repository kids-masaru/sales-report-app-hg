import streamlit as st
import base64
import io
from PIL import Image

# Page Configuration Setup using Custom Icon
try:
    from icon_data import ICON_BASE64
    # Convert Base64 back to PIL Image for st.set_page_config
    icon_bytes = base64.b64decode(ICON_BASE64)
    icon_image = Image.open(io.BytesIO(icon_bytes))
    page_icon_config = icon_image
except:
    page_icon_config = "📝"

st.set_page_config(
    page_title="活動記録作成",
    page_icon=page_icon_config,
    layout="centered"
)

# PWA & Icon Setup
try:
    from icon_data import ICON_BASE64, IOS_ICON_BASE64
    import os
    
    # Ensure static directory exists and save icon
    if not os.path.exists("static"):
        os.makedirs("static")
    
    icon_path = "static/icon.png"
    ios_icon_path = "static/apple-touch-icon.png"
    
    # Always overwrite to ensure latest icon
    with open(icon_path, "wb") as f:
        f.write(base64.b64decode(ICON_BASE64))
        
    # Save iOS icon
    with open(ios_icon_path, "wb") as f:
        f.write(base64.b64decode(IOS_ICON_BASE64))
            
    def setup_pwa():
        # GitHub Raw URL Strategy
        # Since the repo is public, we can link directly to the image files on GitHub.
        # This bypasses any server-side path issues on Render.
        
        REPO_ROOT = "https://raw.githubusercontent.com/kids-masaru/sales-report-app-hg/main"
        
        # Add versioning to force cache refresh
        icon_url = f"{REPO_ROOT}/static/icon.png?v=7"
        
        # Ideally we use the raw url for apple-touch-icon too
        ios_icon_url = f"{REPO_ROOT}/static/apple-touch-icon.png?v=7"
        
        manifest_url = "/app/static/manifest.json?v=7"
        
        st.markdown(
            f"""
            <link rel="manifest" href="{manifest_url}">
            <link rel="icon" type="image/png" href="{icon_url}">
            <link rel="apple-touch-icon" sizes="180x180" href="{ios_icon_url}">
            <link rel="apple-touch-icon-precomposed" href="{ios_icon_url}">
            <meta name="apple-mobile-web-app-capable" content="yes">
            <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
            <meta name="apple-mobile-web-app-title" content="活動記録">
            <style>
            /* Hide Streamlit elements */
            #MainMenu {{visibility: hidden;}}
            header {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            /* Header adjustments: Hide default title from st.Page if possible, otherwise just hide stAppHeader */
            .stAppHeader {{display: none;}}
            
            /* Custom styling for SVG headers */
            .custom-svg-header {{
                display: flex;
                align_items: center;
                gap: 10px;
                padding-bottom: 20px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    setup_pwa()
except Exception as e:
    pass

# User requested removal of redundant titles (st.header was here)# Common CSS (Global)
st.markdown("""
<style>
    /* CSS for compact UI and consistent headers */
    h1 { font-size: 1.5rem !important; margin-bottom: 0.5rem !important; }
    h2 { font-size: 1.2rem !important; margin-top: 1rem !important; margin-bottom: 0.5rem !important; }
    h3 { font-size: 1.0rem !important; margin-top: 0.5rem !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    /* Button styles */
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    
    /* Expander styling: Remove arrow, border, and make it subtle */
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
        margin-top: 0 !important;
    }
    div[data-testid="stExpander"] details > summary {
        list-style: none !important; /* Hide list marker */
        padding-left: 0 !important;
    }
    div[data-testid="stExpander"] details > summary::-webkit-details-marker {
        display: none !important; /* Hide webkit marker */
    }
    div[data-testid="stExpander"] details > summary > svg {
        display: none !important; /* Hide SVG arrow */
    }
    div[data-testid="stExpander"] details summary p { 
        font-size: 0.8rem !important; 
        color: #888; 
        font-weight: normal !important;
        text-decoration: underline;
        cursor: pointer;
    }
    div[data-testid="stExpander"] details summary:hover p {
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Simple Authentication Logic for Public Deployment (Render)
# ---------------------------------------------------------
import os

# 1. Get password from env (Set this in Render Environment Variables)
APP_PASSWORD = os.environ.get("APP_PASSWORD")

# 2. Check auth
def check_password():
    """Returns `True` if the user had the correct password."""

    # Bypass if no password is set
    if not APP_PASSWORD:
        return True

    # DEBUG: Show icon to verify file existence (visible on login screen)
    # st.image("static/apple-touch-icon.png", width=50, caption="Icon Check")
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == APP_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input
        st.text_input(
            "パスワードを入力してください", type="password", on_change=password_entered, key="password"
        )
        return False
    
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input again
        st.text_input(
            "パスワードを入力してください", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 パスワードが違います")
        return False
    
    else:
        # Password correct
        return True

if not check_password():
    st.stop()
# ---------------------------------------------------------

# Logo (Sidebar top)
# st.logo removed

# Navigation
pages = {
    "メニュー": [
        st.Page("views/activity.py", title="活動記録"),
        st.Page("views/qa.py", title="質疑応答抽出"),
    ]
}

pg = st.navigation(pages)
pg.run()
