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
    from icon_data import ICON_BASE64
    def setup_pwa(icon_base64):
        icon_data = f"data:image/png;base64,{icon_base64}"
        st.markdown(
            f"""
            <link rel="apple-touch-icon" href="{icon_data}">
            <link rel="apple-touch-icon-precomposed" href="{icon_data}">
            <link rel="shortcut icon" href="{icon_data}">
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
    setup_pwa(ICON_BASE64)
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
