import streamlit as st
import google.generativeai as genai
import json
import time
import base64
import re
from datetime import datetime
import os

# Configure the page
st.set_page_config(
    page_title="Avatar Success Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #8A2BE2 0%, #4A154B 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(74, 21, 75, 0.3);
    }
    
    .avatar-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 2rem;
        background: linear-gradient(135deg, #F8F4FF 0%, #E6E6FA 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.2);
    }
    
    .avatar-video {
        position: relative;
        border-radius: 50%;
        overflow: hidden;
    }
    
    .avatar-status {
        margin-top: 15px;
        padding: 8px 16px;
        background: rgba(138, 43, 226, 0.1);
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        color: #8A2BE2;
        text-align: center;
    }
    
    .avatar {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 5px solid #8A2BE2;
        animation: pulse 2s infinite;
        background: linear-gradient(45deg, #DDA0DD, #9370DB);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(74, 21, 75, 0.3);
        box-shadow: 0 8px 25px rgba(138, 43, 226, 0.4);
    }
    
    @keyframes pulse {
        0% { 
            transform: scale(1); 
            box-shadow: 0 8px 25px rgba(138, 43, 226, 0.4);
        }
        50% { 
            transform: scale(1.05); 
            box-shadow: 0 12px 35px rgba(138, 43, 226, 0.6);
        }
        100% { 
            transform: scale(1); 
            box-shadow: 0 8px 25px rgba(138, 43, 226, 0.4);
        }
    }
    
    .speaking {
        animation: bounce 0.5s infinite alternate;
        border-color: #DA70D6 !important;
        background: linear-gradient(45deg, #DA70D6, #BA55D3) !important;
    }
    
    @keyframes bounce {
        0% { 
            transform: scale(1);
            box-shadow: 0 8px 25px rgba(218, 112, 214, 0.5);
        }
        100% { 
            transform: scale(1.1);
            box-shadow: 0 15px 40px rgba(218, 112, 214, 0.7);
        }
    }
    
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
    /* Custom Purple Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #8A2BE2, #9932CC) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3) !important;
        border: 1px solid rgba(153, 50, 204, 0.4) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #9932CC, #8B008B) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(138, 43, 226, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 10px rgba(138, 43, 226, 0.4) !important;
    }
    
    /* Primary Button (Send Message) - Darker Purple */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4A154B, #6A1B9A) !important;
        box-shadow: 0 4px 15px rgba(74, 21, 75, 0.4) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #6A1B9A, #8B008B) !important;
        box-shadow: 0 6px 20px rgba(74, 21, 75, 0.5) !important;
    }
    
    /* Form Submit Button Styling */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #4A154B, #6A1B9A) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.6rem 2rem !important;
        font-weight: bold !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(74, 21, 75, 0.4) !important;
        width: 100% !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #6A1B9A, #8B008B) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(74, 21, 75, 0.5) !important;
    }
    
    /* Clear Chat Button - Lighter Purple - Fix selector */
    button[data-baseweb="button"]:has-text("Clear Chat") {
        background: linear-gradient(135deg, #DDA0DD, #DA70D6) !important;
        color: #4A154B !important;
        box-shadow: 0 4px 15px rgba(221, 160, 221, 0.4) !important;
    }
    
    /* Alternative selector for Clear Chat button */
    .stButton:nth-of-type(2) > button {
        background: linear-gradient(135deg, #DDA0DD, #DA70D6) !important;
        color: #4A154B !important;
        box-shadow: 0 4px 15px rgba(221, 160, 221, 0.4) !important;
    }
    
    .stButton:nth-of-type(2) > button:hover {
        background: linear-gradient(135deg, #DA70D6, #BA55D3) !important;
        color: white !important;
        box-shadow: 0 6px 20px rgba(221, 160, 221, 0.5) !important;
    }
    
    /* Sidebar Buttons */
    .css-1d391kg .stButton > button {
        background: linear-gradient(135deg, #B19CD9, #9370DB) !important;
        color: white !important;
        border-radius: 20px !important;
        font-size: 14px !important;
    }
    
    .css-1d391kg .stButton > button:hover {
        background: linear-gradient(135deg, #9370DB, #8A2BE2) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Form Elements Purple Theme */
    .stSelectbox > div > div > select {
        border-color: #9370DB !important;
        border-radius: 10px !important;
    }
    
    .stTextInput > div > div > input {
        border-color: #9370DB !important;
        border-radius: 10px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #8A2BE2 !important;
        box-shadow: 0 0 10px rgba(138, 43, 226, 0.3) !important;
    }
    
    .stTextArea > div > div > textarea {
        border-color: #9370DB !important;
        border-radius: 10px !important;
        border-width: 2px !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #8A2BE2 !important;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.3) !important;
    }
    
    /* Slider Purple Theme - Clean and Optimized */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #DDA0DD, #9370DB) !important;
    }
    
    .stSlider > div > div > div > div > div {
        background: #8A2BE2 !important;
    }
    
    /* Slider track */
    .stSlider > div > div > div {
        background: rgba(221, 160, 221, 0.3) !important;
    }
    
    /* Slider labels - FORCE back to default theme colors */
    .stSlider > label,
    .stSlider label,
    .stSlider > div > label,
    div[data-testid="stSlider"] label,
    .stSlider label[data-testid="stWidgetLabel"],
    .css-1d391kg .stSlider label,
    .css-1d391kg .stSlider > label {
        color: inherit !important;
        color: unset !important;
        font-weight: 600 !important;
    }
    
    /* Nuclear option - remove ALL purple from slider labels */
    .css-1d391kg .stSlider label[style*="color"] {
        color: rgba(250, 250, 250, 0.87) !important;
    }
    
    /* Specific selectors for Speaking Speed and Voice Pitch */
    label:contains("Speaking Speed"),
    label:contains("Voice Pitch"),
    .stSlider label:first-child {
        color: rgba(250, 250, 250, 0.87) !important;
    }
    
    /* Exception - keep slider VALUES purple but labels normal */
    .stSlider div[class*="stNumberInput"] {
        color: #8A2BE2 !important;
    }
    
    /* Specifically target "Speaking Speed" and "Voice Pitch" labels */
    .stSlider:has(+ *:contains("Speaking Speed")) label,
    .stSlider:has(+ *:contains("Voice Pitch")) label,
    label:contains("Speaking Speed"),
    label:contains("Voice Pitch") {
        color: rgba(250, 250, 250, 0.6) !important;
    }
    
    /* Ensure section headers remain default color */
    .css-1d391kg h1,
    .css-1d391kg h2, 
    .css-1d391kg h3,
    .css-1d391kg h4 {
        color: rgba(250, 250, 250, 1) !important;
    }
    
    /* Keep only interactive elements purple */
    .stButton,
    .stFormSubmitButton,
    .stCheckbox input:checked {
        /* Purple styling already defined above */
    }
    
    /* Nuclear option - force all non-button text in sidebar to default color */
    .css-1d391kg *:not(button):not(.stButton):not(.stFormSubmitButton) {
        color: rgba(250, 250, 250, 0.6) !important;
    }
    
    /* Make sure headings are brighter */
    .css-1d391kg h1,
    .css-1d391kg h2,
    .css-1d391kg h3 {
        color: rgba(250, 250, 250, 1) !important;
    }
    
    /* Exception for slider numeric values - keep these purple for emphasis */
    .stSlider .st-emotion-cache-1inwz65,
    .stSlider div[data-testid="stMarkdownContainer"]:has-text("0.80"),
    .stSlider div[data-testid="stMarkdownContainer"]:has-text("1.00") {
        color: #8A2BE2 !important;
        font-weight: bold !important;
    }
    
    /* Override any remaining purple text that isn't a button */
    .css-1d391kg div:not(.stButton):not(.stFormSubmitButton) {
        color: rgba(250, 250, 250, 0.6) !important;
    }
    
    .css-1d391kg label:not(.stButton label):not(.stFormSubmitButton label) {
        color: rgba(250, 250, 250, 0.6) !important;
    }
    
    /* Alternative slider selectors for more specificity */
    [data-baseweb="slider"] > div > div {
        background: rgba(221, 160, 221, 0.3) !important;
    }
    
    [data-baseweb="slider"] > div > div > div {
        background: #9370DB !important;
    }
    
    [data-baseweb="slider"] [role="slider"] {
        background: #8A2BE2 !important;
        border: 2px solid #6A1B9A !important;
        box-shadow: 0 2px 10px rgba(138, 43, 226, 0.5) !important;
    }
    
    [data-baseweb="slider"] [role="slider"]:hover {
        background: #9932CC !important;
        transform: scale(1.1) !important;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.6) !important;
    }
    
    /* Slider value numbers - keep purple */
    .stSlider .st-emotion-cache-1inwz65 {
        color: #8A2BE2 !important;
        font-weight: bold !important;
    }
    
    /* Slider value display box */
    .stSlider div[data-testid="stMarkdownContainer"] {
        color: #8A2BE2 !important;
        font-weight: bold !important;
    }
    
    /* Slider min/max labels - keep default color */
    .stSlider div[class*="tickBar"] {
        color: inherit !important;
    }
    
    /* Additional slider styling for all states */
    div[data-testid="stSlider"] > div > div > div > div {
        background: #9370DB !important;
    }
    
    div[data-testid="stSlider"] > div > div > div {
        background: rgba(147, 112, 219, 0.2) !important;
    }
    
    /* Force purple theme on any remaining red elements in sliders */
    .stSlider div[style*="rgb(255, 75, 75)"] {
        background: #9370DB !important;
    }
    
    .stSlider div[style*="rgb(255, 43, 43)"] {
        background: #8A2BE2 !important;
    }
    
    /* Target specific slider components */
    .stSlider [class*="StyledThumb"] {
        background-color: #8A2BE2 !important;
        border-color: #6A1B9A !important;
    }
    
    .stSlider [class*="StyledTrack"] {
        background-color: #9370DB !important;
    }
    
    .stSlider [class*="StyledTrackFill"] {
        background-color: rgba(147, 112, 219, 0.3) !important;
    }
    
    /* Override any remaining red colors globally in sidebar */
    .css-1d391kg div[style*="rgb(255"], 
    .css-1d391kg div[style*="rgb(255, 75, 75)"],
    .css-1d391kg div[style*="#ff4b4b"],
    .css-1d391kg div[style*="red"] {
        background: #9370DB !important;
    }
    
    /* Smooth slider interaction and better UX */
    .stSlider button[role="slider"] {
        background: #8A2BE2 !important;
        border: 3px solid #6A1B9A !important;
        box-shadow: 0 2px 10px rgba(138, 43, 226, 0.5) !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        transition: all 0.2s ease !important;
        cursor: grab !important;
    }
    
    /* Slider thumb hover - easier to grab */
    .stSlider button[role="slider"]:hover {
        background: #9932CC !important;
        transform: scale(1.2) !important;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.6) !important;
        cursor: grab !important;
    }
    
    /* Slider thumb active/dragging state */
    .stSlider button[role="slider"]:active {
        background: #9932CC !important;
        transform: scale(1.3) !important;
        box-shadow: 0 6px 20px rgba(138, 43, 226, 0.8) !important;
        cursor: grabbing !important;
        transition: all 0.1s ease !important;
    }
    
    /* Slider track - make it easier to click */
    .stSlider div[class*="baseweb"] div[class*="Track"] {
        background: rgba(147, 112, 219, 0.3) !important;
        height: 6px !important;
        border-radius: 3px !important;
        cursor: pointer !important;
    }
    
    /* Slider track fill - smooth visual feedback */
    .stSlider div[class*="baseweb"] div[class*="Fill"] {
        background: linear-gradient(90deg, #DDA0DD, #9370DB) !important;
        height: 6px !important;
        border-radius: 3px !important;
        transition: all 0.2s ease !important;
    }
    
    /* Slider container - ensure proper padding for easy interaction */
    .stSlider > div {
        padding: 10px 0 !important;
    }
    
    /* Better touch/click targets */
    [data-baseweb="slider"] {
        padding: 15px 0 !important;
        cursor: pointer !important;
    }
    
    [data-baseweb="slider"] [role="slider"] {
        width: 20px !important;
        height: 20px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    [data-baseweb="slider"] [role="slider"]:hover {
        transform: scale(1.2) !important;
        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    [data-baseweb="slider"] [role="slider"]:active {
        transform: scale(1.3) !important;
        transition: all 0.1s ease !important;
    }
    
    /* Slider track active portion */
    .stSlider div[class*="baseweb"] div[class*="Track"] {
        background: rgba(147, 112, 219, 0.3) !important;
    }
    
    .stSlider div[class*="baseweb"] div[class*="Fill"] {
        background: linear-gradient(90deg, #DDA0DD, #9370DB) !important;
    }
    
    /* Force purple on inline styles - nuclear option */
    .stSlider * {
        color: inherit !important;
    }
    
    .stSlider div[style*="background-color: rgb(255"] {
        background: #9370DB !important;
    }
    
    /* Checkbox Purple Theme */
    .stCheckbox > label > div {
        background-color: #9370DB !important;
        border-color: #8A2BE2 !important;
        border-width: 2px !important;
    }
    
    .stCheckbox > label > div[data-checked="true"] {
        background-color: #8A2BE2 !important;
        border-color: #6A1B9A !important;
    }
    
    .stCheckbox > label > div > svg {
        color: white !important;
    }
    
    /* Alternative checkbox selectors */
    div[data-testid="stCheckbox"] > label > div {
        background: #9370DB !important;
        border: 2px solid #8A2BE2 !important;
        border-radius: 4px !important;
    }
    
    div[data-testid="stCheckbox"] > label > div[data-checked="true"] {
        background: linear-gradient(135deg, #8A2BE2, #6A1B9A) !important;
        border-color: #4A154B !important;
    }
    
    /* Checkbox checkmark */
    div[data-testid="stCheckbox"] svg {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* Checkbox hover effect */
    .stCheckbox > label > div:hover {
        background-color: #8A2BE2 !important;
        border-color: #6A1B9A !important;
        box-shadow: 0 2px 8px rgba(138, 43, 226, 0.3) !important;
    }
    
    /* Checkbox label text */
    .stCheckbox > label {
        color: inherit !important;
    }
    
    /* Multiselect Purple Theme */
    .stMultiSelect > div > div > div {
        border-color: #9370DB !important;
        border-radius: 10px !important;
    }
    
    /* API Test Button - Special styling */
    button[data-testid="test_api_btn"] {
        background: linear-gradient(135deg, #663399, #7B68EE) !important;
        color: white !important;
        border-radius: 15px !important;
        font-size: 12px !important;
    }
    
    /* Expander Header Purple Theme */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #F0E6FF, #E6E6FA) !important;
        color: #4A154B !important;
    }
    
    /* Success/Error Messages with Purple Accent */
    .stSuccess {
        border-left: 5px solid #8A2BE2 !important;
    }
    
    .stError {
        border-left: 5px solid #9370DB !important;
    }
    
    .stInfo {
        border-left: 5px solid #DDA0DD !important;
    }
    
    /* Loading Spinner Purple Theme */
    .stSpinner > div {
        border-color: #8A2BE2 !important;
    }
    
    /* Radio Button Purple Theme */
    .stRadio > div {
        color: #4A154B !important;
    }
    
    .stRadio input:checked ~ label {
        color: #8A2BE2 !important;
    }
    
    .user-message {
        background: linear-gradient(135deg, #E6E6FA, #DDA0DD);
        color: #4A154B;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 8px rgba(221, 160, 221, 0.3);
        border: 1px solid rgba(221, 160, 221, 0.4);
    }
    
    .coach-message {
        background: linear-gradient(135deg, #4A154B, #6A1B9A);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        box-shadow: 0 2px 12px rgba(74, 21, 75, 0.4);
        border: 1px solid rgba(106, 27, 154, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'is_speaking' not in st.session_state:
        st.session_state.is_speaking = False
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}

# Configure APIs
def setup_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        st.error("❌ Please set your Gemini API key in .streamlit/secrets.toml")
        st.info("Get your free API key from: https://makersuite.google.com/app/apikey")
        st.stop()
    
    try:
        genai.configure(api_key=api_key)
        
        # Try current model names in order of preference
        model_names = [
            'gemini-2.0-flash',      # Latest stable model (recommended)
            'gemini-1.5-flash',      # Fallback if 2.0 not available
            'gemini-1.5-pro'         # Final fallback
        ]
        
        model = None
        working_model_name = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # Test the model with a simple request
                test_response = model.generate_content("Say 'API Connected successfully!'")
                if test_response and test_response.text:
                    working_model_name = model_name
                    st.success(f"✅ Using Gemini model: {model_name}")
                    break
            except Exception as model_error:
                continue
        
        if not model:
            st.error("❌ Could not connect to any Gemini model")
            st.error("Please check your API key and try again")
            st.stop()
            
        return model, working_model_name
        
    except Exception as e:
        st.error(f"❌ Gemini API Error: {str(e)}")
        st.info("Possible solutions:\n1. Check your API key\n2. Verify internet connection\n3. Try a different model")
        st.stop()

# HeyGen Avatar Integration
def setup_heygen():
    """Setup HeyGen API for avatar generation"""
    api_key = st.secrets.get("HEYGEN_API_KEY") or os.getenv("HEYGEN_API_KEY")
    if not api_key:
        st.warning("⚠️ HeyGen API key not found. Avatar will use fallback mode.")
        return None
    return api_key

def generate_avatar_video(text, heygen_key, avatar_id="default"):
    """Generate avatar video using HeyGen API"""
    if not heygen_key:
        return None
    
    try:
        import requests
        
        url = "https://api.heygen.com/v2/video/generate"
        headers = {
            "X-API-KEY": heygen_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": text,
                    "voice_id": "1bd001e7e50f421d891986aad5158bc8",  # Natural female voice
                    "speed": 1.0,
                    "emotion": "friendly"
                },
                "background": {
                    "type": "color",
                    "value": "#f0e6ff"  # Light purple background
                }
            }],
            "dimension": {
                "width": 400,
                "height": 400
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("data", {}).get("video_id")
        else:
            st.error(f"HeyGen API Error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Avatar generation error: {str(e)}")
        return None

# Load coaching knowledge base
def load_coaching_knowledge():
    return """
    You are a professional success and wealth coach. Your expertise includes:
    
    CORE PRINCIPLES:
    - Success and wealth require daily disciplined actions and consistent learning
    - True richness encompasses money, time, purpose, and freedom
    - Elevating habits, mindset, and strategy is essential
    - Focus on actionable strategies and practical steps
    
    KEY AREAS OF EXPERTISE:
    1. Mindset Development - Building wealthy thinking patterns
    2. Goal Setting - Creating clear, achievable objectives
    3. Financial Education - Understanding money and investments
    4. Time Management - Maximizing productivity and efficiency
    5. Networking & Mentorship - Building valuable relationships
    6. Smart Saving & Investing - Growing wealth systematically
    7. Multiple Income Streams - Diversifying revenue sources
    8. Entrepreneurship - Starting and scaling businesses
    9. Risk Management - Making calculated decisions
    10. Leadership Development - Inspiring and guiding others
    
    COACHING STYLE:
    - Ask probing questions to understand the client's situation
    - Provide actionable, specific advice
    - Use examples and analogies to illustrate points
    - Encourage accountability and progress tracking
    - Balance encouragement with realistic expectations
    - Focus on both mindset and practical strategies
    
    Always respond as a caring, knowledgeable coach who wants to see clients succeed.
    Keep responses conversational but professional, and always end with a question or call to action.
    """

# Generate coach response
def get_coach_response(user_input, chat_history):
    try:
        model, model_name = setup_gemini()
        
        # Get user profile for personalization
        profile = st.session_state.user_profile
        name = profile.get('name', 'there')
        experience = profile.get('experience', 'Beginner')
        voice_type = profile.get('voice_type', 'caring')
        goals = profile.get('goals', 'general success')
        
        # Simplified prompt to avoid API issues
        context = f"""You are a {voice_type} success and wealth coach. 
        
        Client: {name} (Experience: {experience}, Goals: {goals})
        
        Recent conversation:"""
        
        # Add last 2 messages only to keep it simple
        for msg in chat_history[-2:]:
            role_name = "Coach" if msg['role'] == 'coach' else name
            context += f"\n{role_name}: {msg['content']}"
        
        context += f"\n{name}: {user_input}"
        
        # Simple, direct prompt
        prompt = f"""{context}
        
        Respond as a {voice_type} success coach to {name}. Keep your response under 100 words, be helpful and encouraging, and ask a follow-up question."""
        
        # Generate response with safety settings
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 200,
                'top_p': 0.9,
                'top_k': 40
            }
        )
        
        if response and response.text:
            coach_response = response.text.strip()
            
            # Add emotional context based on user input
            if any(word in user_input.lower() for word in ['sad', 'worried', 'down', 'upset']):
                coach_response = f"I understand you're feeling down, {name}. " + coach_response
            elif any(word in user_input.lower() for word in ['happy', 'excited', 'great']):
                coach_response = f"I love your positive energy, {name}! " + coach_response
            
            return coach_response
        else:
            return f"I'm here to help you, {name}. Could you tell me more about what's on your mind?"
            
    except Exception as e:
        print(f"API Error: {str(e)}")  # For debugging
        
        # Friendly fallback responses
        fallback_responses = {
            'caring': f"I'm here for you, {name}. I may have missed what you said - could you share your thoughts with me again?",
            'professional': f"{name}, I want to ensure I give you the best guidance. Could you please repeat your question?",
            'energetic': f"Hey {name}! I'm still super excited to help you succeed. What's on your mind?",
            'wise': f"{name}, sometimes we need patience. Please share your thoughts with me once more."
        }
        
        name = st.session_state.user_profile.get('name', 'there')
        voice_type = st.session_state.user_profile.get('voice_type', 'caring')
        return fallback_responses.get(voice_type, f"I'm here to help you, {name}. Please tell me what you're thinking about.")

# WhatsApp-style voice note component
def whatsapp_voice_note_component():
    """WhatsApp-style voice recording interface"""
    
    voice_note_html = """
    <div class="voice-note-container">
        <div class="voice-controls">
            <button id="voiceButton" onmousedown="startRecording()" onmouseup="stopRecording()" 
                    ontouchstart="startRecording()" ontouchend="stopRecording()"
                    style="
                        background: linear-gradient(135deg, #8A2BE2, #9370DB);
                        border: none;
                        border-radius: 50%;
                        width: 60px;
                        height: 60px;
                        color: white;
                        font-size: 24px;
                        cursor: pointer;
                        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.4);
                        transition: all 0.2s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    "
                    onmouseover="this.style.transform='scale(1.1)'"
                    onmouseout="this.style.transform='scale(1)'">
                🎤
            </button>
            <div id="recordingStatus" style="margin-left: 15px; color: #8A2BE2; font-weight: bold;">
                Hold to record voice note
            </div>
        </div>
        
        <div id="voiceWaveform" class="voice-waveform" style="display: none;">
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
        </div>
        
        <div id="transcriptionResult" style="
            margin-top: 10px; 
            padding: 10px; 
            background: rgba(138, 43, 226, 0.1); 
            border-radius: 10px; 
            display: none;
        "></div>
    </div>

    <style>
    .voice-note-container {
        padding: 20px;
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        border-radius: 15px;
        margin: 10px 0;
        border: 2px solid rgba(138, 43, 226, 0.2);
    }
    
    .voice-controls {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .voice-waveform {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 3px;
        margin-top: 15px;
    }
    
    .wave-bar {
        width: 4px;
        height: 20px;
        background: linear-gradient(135deg, #8A2BE2, #9370DB);
        border-radius: 2px;
        animation: wave 1.5s ease-in-out infinite;
    }
    
    .wave-bar:nth-child(2) { animation-delay: 0.2s; }
    .wave-bar:nth-child(3) { animation-delay: 0.4s; }
    .wave-bar:nth-child(4) { animation-delay: 0.6s; }
    .wave-bar:nth-child(5) { animation-delay: 0.8s; }
    
    @keyframes wave {
        0%, 100% { height: 20px; }
        50% { height: 40px; }
    }
    
    .recording {
        background: linear-gradient(135deg, #ff4757, #ff3742) !important;
        animation: pulse-record 1s ease-in-out infinite !important;
    }
    
    @keyframes pulse-record {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    </style>

    <script>
    let mediaRecorder;
    let audioChunks = [];
    let recognition;
    let isRecording = false;

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            document.getElementById('recordingStatus').innerHTML = '🎤 Listening... Release to send';
            document.getElementById('voiceWaveform').style.display = 'flex';
        };
        
        recognition.onresult = function(event) {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            document.getElementById('transcriptionResult').innerHTML = transcript;
            document.getElementById('transcriptionResult').style.display = 'block';
            
            // If final result, send to parent component
            if (event.results[event.results.length - 1].isFinal) {
                window.parent.postMessage({
                    type: 'voice_input',
                    text: transcript
                }, '*');
            }
        };
        
        recognition.onerror = function(event) {
            document.getElementById('recordingStatus').innerHTML = 'Error: ' + event.error;
            resetRecording();
        };
        
        recognition.onend = function() {
            resetRecording();
        };
    }

    function startRecording() {
        if (isRecording) return;
        
        isRecording = true;
        document.getElementById('voiceButton').classList.add('recording');
        document.getElementById('transcriptionResult').style.display = 'none';
        
        if (recognition) {
            recognition.start();
        } else {
            alert('Speech recognition not supported in this browser');
            resetRecording();
        }
    }

    function stopRecording() {
        if (!isRecording) return;
        
        isRecording = false;
        if (recognition) {
            recognition.stop();
        }
    }

    function resetRecording() {
        isRecording = false;
        document.getElementById('voiceButton').classList.remove('recording');
        document.getElementById('recordingStatus').innerHTML = 'Hold to record voice note';
        document.getElementById('voiceWaveform').style.display = 'none';
    }
    </script>
    """
    
    return voice_note_html

def clean_text(text):
    """Clean text for speech synthesis"""
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic  
    text = re.sub(r'#{1,6}\s', '', text)          # Headers
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
    
    # Clean up extra spaces and newlines
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Escape quotes for JavaScript
    text = text.replace('"', '\\"').replace("'", "\\'")
    
    # Remove excessive pauses for cleaner speech
    text = re.sub(r'\.{3,}', '...', text)
    
    return text.strip()

# Enhanced natural text-to-speech component
def natural_text_to_speech_component(text):
    """Enhanced TTS with more natural speech patterns"""
    if not text:
        return
    
    # Check for ElevenLabs API key for premium voice
    elevenlabs_key = st.secrets.get("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY")
    
    if elevenlabs_key:
        # Use ElevenLabs for natural voice
        tts_html = create_elevenlabs_speech(text, elevenlabs_key)
    else:
        # Enhanced browser TTS with natural parameters
        tts_html = create_enhanced_browser_speech(text)
    
    st.components.v1.html(tts_html, height=80)

def create_elevenlabs_speech(text, api_key):
    """Create natural speech using ElevenLabs API"""
    voice_type = st.session_state.user_profile.get('voice_type', 'caring')
    
    # ElevenLabs voice IDs for different personalities
    voice_ids = {
        'caring': 'EXAVITQu4vr4xnSDxMaL',      # Bella - warm and caring
        'professional': 'ErXwobaYiN019PkySvjV',  # Antoni - professional
        'energetic': 'ThT5KcBeYPX3keUQqHPh',    # Dorothy - energetic
        'wise': 'onwK4e9ZLuTAKqWW03F9'          # Daniel - wise and deep
    }
    
    voice_id = voice_ids.get(voice_type, voice_ids['caring'])
    clean_text = clean_text_for_speech(text)
    
    return f"""
    <script>
    async function speakWithElevenLabs() {{
        try {{
            const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/{voice_id}', {{
                method: 'POST',
                headers: {{
                    'Accept': 'audio/mpeg',
                    'Content-Type': 'application/json',
                    'xi-api-key': '{api_key}'
                }},
                body: JSON.stringify({{
                    text: `{clean_text}`,
                    model_id: 'eleven_monolingual_v1',
                    voice_settings: {{
                        stability: 0.7,
                        similarity_boost: 0.8,
                        style: 0.5,
                        use_speaker_boost: true
                    }}
                }})
            }});
            
            if (response.ok) {{
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                document.getElementById('speakButton').innerHTML = '🔇 Stop Speaking';
                audio.play();
                
                audio.onended = function() {{
                    document.getElementById('speakButton').innerHTML = '🔊 Play Response';
                }};
            }} else {{
                fallbackToWebSpeech();
            }}
        }} catch (error) {{
            console.error('ElevenLabs error:', error);
            fallbackToWebSpeech();
        }}
    }}
    
    function fallbackToWebSpeech() {{
        // Fallback to enhanced browser speech
        enhancedWebSpeech();
    }}
    
    // Auto-play if enabled
    var autoPlay = {str(st.session_state.user_profile.get('auto_speak', True)).lower()};
    if (autoPlay) {{
        setTimeout(speakWithElevenLabs, 800);
    }}
    </script>
    
    <div style="text-align: center; margin: 10px 0;">
        <button id="speakButton" onclick="speakWithElevenLabs()" style="
            background: linear-gradient(45deg, #9370DB, #8A2BE2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(147, 112, 219, 0.4);
        ">
            🔊 Play Natural Voice
        </button>
    </div>
    """

def create_enhanced_browser_speech(text):
    """Enhanced browser speech with natural parameters"""
    voice_type = st.session_state.user_profile.get('voice_type', 'caring')
    voice_speed = st.session_state.user_profile.get('voice_speed', 0.8)
    voice_pitch = st.session_state.user_profile.get('voice_pitch', 1.0)
    
    # Add natural speech patterns
    enhanced_text = enhance_text_for_natural_speech(text, voice_type)
    clean_text = clean_text_for_speech(enhanced_text)
    
    return f"""
    <script>
    function enhancedWebSpeech() {{
        if ('speechSynthesis' in window) {{
            speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(`{clean_text}`);
            
            // Enhanced natural parameters
            utterance.rate = {voice_speed * 0.9};  // Slightly slower for clarity
            utterance.pitch = {voice_pitch};
            utterance.volume = 1.0;
            
            // Add breathing pauses and emphasis
            let voices = speechSynthesis.getVoices();
            if (voices.length === 0) {{
                setTimeout(() => {{
                    voices = speechSynthesis.getVoices();
                    selectBestVoice();
                }}, 100);
            }} else {{
                selectBestVoice();
            }}
            
            function selectBestVoice() {{
                let selectedVoice = null;
                const voiceType = '{voice_type}';
                
                // Premium voice selection with quality filtering
                const premiumVoices = voices.filter(voice => 
                    voice.lang.startsWith('en-') && 
                    (voice.localService === true || voice.name.includes('Premium') || 
                     voice.name.includes('Enhanced') || voice.name.includes('Neural'))
                );
                
                if (voiceType === 'caring') {{
                    selectedVoice = premiumVoices.find(voice => 
                        voice.name.includes('Female') || voice.name.includes('Woman') ||
                        voice.name.includes('Samantha') || voice.name.includes('Karen') ||
                        voice.name.includes('Susan') || voice.name.includes('Victoria')
                    );
                }} else if (voiceType === 'professional') {{
                    selectedVoice = premiumVoices.find(voice => 
                        voice.name.includes('Alex') || voice.name.includes('Daniel') ||
                        voice.name.includes('David') || voice.name.includes('Mark')
                    );
                }} else if (voiceType === 'energetic') {{
                    selectedVoice = premiumVoices.find(voice => 
                        voice.name.includes('Zira') || voice.name.includes('Catherine') ||
                        voice.name.includes('Fiona') || voice.name.includes('Moira')
                    );
                }} else if (voiceType === 'wise') {{
                    selectedVoice = premiumVoices.find(voice => 
                        voice.name.includes('Bruce') || voice.name.includes('George') ||
                        voice.name.includes('Arthur') || voice.name.includes('James')
                    );
                }}
                
                // Fallback to best available voice
                if (!selectedVoice) {{
                    selectedVoice = premiumVoices[0] || voices.find(voice => 
                        voice.lang.startsWith('en-') && voice.quality !== 'low'
                    ) || voices[0];
                }}
                
                if (selectedVoice) {{
                    utterance.voice = selectedVoice;
                }}
                
                // Enhanced speech events
                utterance.onstart = function() {{
                    document.getElementById('speakButton').innerHTML = '🔇 Stop Speaking';
                    document.getElementById('speakButton').style.background = 'linear-gradient(45deg, #ff4757, #ff3742)';
                }};
                
                utterance.onend = function() {{
                    document.getElementById('speakButton').innerHTML = '🔊 Play Response';
                    document.getElementById('speakButton').style.background = 'linear-gradient(45deg, #9370DB, #8A2BE2)';
                }};
                
                utterance.onerror = function(event) {{
                    console.error('Speech synthesis error:', event.error);
                    document.getElementById('speakButton').innerHTML = '🔊 Try Again';
                }};
                
                speechSynthesis.speak(utterance);
            }}
        }}
    }}
    
    // Auto-play if enabled
    var autoPlay = {str(st.session_state.user_profile.get('auto_speak', True)).lower()};
    if (autoPlay) {{
        setTimeout(enhancedWebSpeech, 800);
    }}
    </script>
    
    <div style="text-align: center; margin: 10px 0;">
        <button id="speakButton" onclick="enhancedWebSpeech()" style="
            background: linear-gradient(45deg, #9370DB, #8A2BE2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(147, 112, 219, 0.4);
        ">
            🔊 Play Response
        </button>
    </div>
    """

def clean_text_for_speech(text):
    """Clean and prepare text for more natural speech"""
    # Remove markdown
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    
    # Escape quotes for JavaScript
    text = text.replace('"', '\\"').replace("'", "\\'")
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def enhance_text_for_natural_speech(text, voice_type):
    """Add natural speech patterns and emphasis"""
    
    # Add natural pauses
    text = re.sub(r'([.!?])', r'\1... ', text)
    text = re.sub(r'([,:;])', r'\1. ', text)
    
    # Add personality-based enhancements
    if voice_type == 'caring':
        text = re.sub(r'\b(you|your)\b', r'you', text, flags=re.IGNORECASE)
        text = re.sub(r'!', '! That\'s wonderful!', text)
    elif voice_type == 'energetic':
        text = re.sub(r'\bgreat\b', 'absolutely fantastic', text, flags=re.IGNORECASE)
        text = re.sub(r'\bgood\b', 'amazing', text, flags=re.IGNORECASE)
    elif voice_type == 'wise':
        text = re.sub(r'\bremember\b', 'always remember', text, flags=re.IGNORECASE)
        text = re.sub(r'\.', '. Take a moment to consider this.', text, count=1)
    
    return text

# Avatar component with HeyGen integration
def avatar_component(is_speaking=False, latest_message=""):
    """Display talking avatar with HeyGen integration"""
    avatar_emoji = st.session_state.user_profile.get('avatar', '👩‍💼')
    heygen_key = setup_heygen()
    
    if heygen_key and latest_message and is_speaking:
        # Generate real avatar video
        video_id = generate_avatar_video(latest_message, heygen_key)
        
        if video_id:
            # Display HeyGen avatar video
            avatar_html = f"""
            <div class="avatar-container">
                <div class="avatar-video">
                    <video id="avatarVideo" autoplay muted controls style="
                        width: 300px; 
                        height: 300px; 
                        border-radius: 50%; 
                        object-fit: cover;
                        border: 5px solid #8A2BE2;
                        box-shadow: 0 8px 25px rgba(138, 43, 226, 0.4);
                    ">
                        <source src="https://api.heygen.com/v2/video/{video_id}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
            </div>
            
            <script>
            // Auto-play avatar video
            document.getElementById('avatarVideo').addEventListener('loadeddata', function() {{
                this.play();
            }});
            </script>
            """
        else:
            # Fallback to animated emoji
            avatar_html = create_emoji_avatar(avatar_emoji, is_speaking)
    else:
        # Use emoji avatar as fallback or when not speaking
        avatar_html = create_emoji_avatar(avatar_emoji, is_speaking)
    
    st.markdown(avatar_html, unsafe_allow_html=True)

def create_emoji_avatar(avatar_emoji, is_speaking):
    """Create animated emoji avatar as fallback"""
    avatar_class = "avatar speaking" if is_speaking else "avatar"
    
    return f"""
    <div class="avatar-container">
        <div class="{avatar_class}">
            {avatar_emoji}
        </div>
        <div class="avatar-status">
            {'🎤 Speaking...' if is_speaking else '💭 Listening...'}
        </div>
    </div>
    """

# Chat interface
def chat_interface():
    st.markdown("### 💬 Conversation")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="coach-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Add empathy to text based on voice type
def add_empathy_to_text(text, voice_type):
    """Add natural pauses and emotional context to make speech more empathetic"""
    
    # Add natural pauses for better flow
    text = re.sub(r'([.!?])', r'\1... ', text)  # Pause after sentences
    text = re.sub(r'([,;])', r'\1. ', text)     # Slight pause after commas
    
    # Add emotional context based on voice type
    if voice_type == 'caring':
        # Add warmth and encouragement
        text = re.sub(r'\bgreat\b', 'absolutely wonderful', text, flags=re.IGNORECASE)
        text = re.sub(r'\bgood\b', 'really good', text, flags=re.IGNORECASE)
        text = re.sub(r'\byes\b', 'yes, exactly', text, flags=re.IGNORECASE)
        
    elif voice_type == 'energetic':
        # Add enthusiasm
        text = re.sub(r'\bgreat\b', 'fantastic', text, flags=re.IGNORECASE)
        text = re.sub(r'\bgood\b', 'amazing', text, flags=re.IGNORECASE)
        text = re.sub(r'!', '! That\'s exciting!', text)
        
    elif voice_type == 'wise':
        # Add thoughtful pauses and wisdom
        text = re.sub(r'\bremember\b', 'always remember', text, flags=re.IGNORECASE)
        text = re.sub(r'\bimportant\b', 'very important', text, flags=re.IGNORECASE)
        
    return text

# User profile sidebar
def user_profile_sidebar():
    with st.sidebar:
        st.header("Personalize Your Coach")
        
        # Basic Profile
        st.subheader("Basic Information")
        name = st.text_input("Your Name", value=st.session_state.user_profile.get('name', ''))
        goals = st.text_area("Primary Goals", value=st.session_state.user_profile.get('goals', ''), 
                            help="What do you want to achieve in wealth and success?")
        
        experience = st.selectbox(
            "Experience Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(
                st.session_state.user_profile.get('experience', 'Beginner')
            )
        )
        
        # Avatar Customization
        st.subheader("Choose Your Coach Avatar")
        avatar_options = {
            "👩‍💼": "Sarah - Professional Coach",
            "👨‍💼": "Marcus - Business Mentor", 
            "👩‍🎓": "Dr. Emily - Academic Expert",
            "👨‍🔬": "Prof. David - Research Specialist",
            "👩‍⚕️": "Dr. Lisa - Wellness Coach",
            "👨‍🏫": "Coach Michael - Motivational Speaker",
            "👩‍💻": "Alex - Tech Entrepreneur",
            "👨‍🎨": "Creative Director James",
            "👩‍🔧": "Engineer Maya - Problem Solver",
            "👨‍🚀": "Captain Steve - Visionary Leader",
            "👩‍🌾": "Sustainable Success - Emma",
            "👨‍⚖️": "Strategic Advisor - Robert"
        }
        
        current_avatar = st.session_state.user_profile.get('avatar', '👩‍💼')
        avatar_choice = st.selectbox(
            "Select Avatar",
            options=list(avatar_options.keys()),
            format_func=lambda x: f"{x} {avatar_options[x]}",
            index=list(avatar_options.keys()).index(current_avatar) if current_avatar in avatar_options else 0
        )
        
        # Voice Customization
        st.subheader("Voice & Personality")
        
        voice_type = st.selectbox(
            "Coach Personality",
            ["caring", "professional", "energetic", "wise"],
            index=["caring", "professional", "energetic", "wise"].index(
                st.session_state.user_profile.get('voice_type', 'caring')
            ),
            format_func=lambda x: {
                'caring': '💝 Caring & Nurturing',
                'professional': '💼 Professional & Direct', 
                'energetic': '⚡ Energetic & Enthusiastic',
                'wise': '🧙‍♂️ Wise & Thoughtful'
            }[x]
        )
        
        voice_speed = st.slider(
            "Speaking Speed",
            min_value=0.5, max_value=1.5, value=st.session_state.user_profile.get('voice_speed', 0.8),
            step=0.1, help="Slower = More thoughtful, Faster = More energetic"
        )
        
        voice_pitch = st.slider(
            "Voice Pitch", 
            min_value=0.5, max_value=2.0, value=st.session_state.user_profile.get('voice_pitch', 1.0),
            step=0.1, help="Lower = More authoritative, Higher = More friendly"
        )
        
        auto_speak = st.checkbox(
            "Auto-play responses", 
            value=st.session_state.user_profile.get('auto_speak', True),
            help="Automatically speak coach responses"
        )
        
        # Focus Areas
        st.subheader("Focus Areas")
        focus_areas = st.multiselect(
            "What areas do you want to focus on?",
            [
                "💰 Financial Planning",
                "📈 Career Growth", 
                "🚀 Entrepreneurship",
                "📊 Investment Strategy",
                "⏰ Time Management",
                "👑 Leadership Skills",
                "🤝 Networking",
                "🧠 Personal Development",
                "💎 Wealth Mindset",
                "🎯 Goal Achievement"
            ],
            default=st.session_state.user_profile.get('focus_areas', [])
        )
        
        # Save Profile
        if st.button("Save Profile", type="primary", key="save_profile_btn"):
            st.session_state.user_profile = {
                'name': name,
                'goals': goals,
                'experience': experience,
                'avatar': avatar_choice,
                'voice_type': voice_type,
                'voice_speed': voice_speed,
                'voice_pitch': voice_pitch,
                'auto_speak': auto_speak,
                'focus_areas': focus_areas
            }
            st.success("✅ Profile saved! Your coach is now personalized!")
            st.rerun()
        
        # Preview Section
        if st.session_state.user_profile:
            st.subheader("👀 Preview")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{avatar_choice}</div>", 
                          unsafe_allow_html=True)
            with col2:
                st.write(f"**{voice_type.title()}** personality")
                st.write(f"Speed: {voice_speed}x")
                st.write(f"Pitch: {voice_pitch}x")

def get_personalized_greeting():
    """Generate a personalized greeting when user first arrives or changes profile"""
    profile = st.session_state.user_profile
    name = profile.get('name', 'there')
    avatar = profile.get('avatar', '👩‍💼') 
    voice_type = profile.get('voice_type', 'caring')
    
    greetings = {
        'caring': f"Hello {name}! {avatar} I'm so glad you're here. I'm your caring success coach, and I'm genuinely excited to support you on your journey to wealth and success. How are you feeling today?",
        'professional': f"Good day, {name}! {avatar} I'm your professional success coach. I'm here to provide you with clear, actionable strategies for achieving your wealth and success goals. What would you like to focus on today?", 
        'energetic': f"Hey there, {name}! {avatar} I'm absolutely thrilled to be your energetic success coach! Let's create some amazing momentum toward your dreams and goals. What's got you excited today?",
        'wise': f"Welcome, {name}. {avatar} I'm honored to serve as your wise mentor on the path to success and prosperity. Through experience and insight, we'll navigate your journey together. What wisdom are you seeking today?"
    }
    
    return greetings.get(voice_type, f"Hello {name}! {avatar} Welcome to your success coaching session. How can I help you today?")

# Main app
def main():
    load_css()
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Avatar Success Coach</h1>
        <p>Your AI-powered wealth and success mentor</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User profile sidebar
    user_profile_sidebar()
    
    # Show personalized greeting if profile exists but no chat history
    if st.session_state.user_profile and not st.session_state.chat_history:
        greeting = get_personalized_greeting()
        st.session_state.chat_history.append({
            'role': 'coach',
            'content': greeting,
            'timestamp': datetime.now()
        })
        st.session_state.is_speaking = True
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Avatar with HeyGen integration
        latest_response = ""
        if st.session_state.chat_history:
            latest_msg = st.session_state.chat_history[-1]
            if latest_msg['role'] == 'coach':
                latest_response = latest_msg['content']
        
        avatar_component(st.session_state.is_speaking, latest_response)
        
        # WhatsApp-style voice input
        st.markdown("### 🎤 Voice Message")
        voice_html = whatsapp_voice_note_component()
        st.components.v1.html(voice_html, height=200)
        
        # Handle voice input messages
        if st.button("🔄 Check Voice Input", key="check_voice"):
            # This would normally receive data from the voice component
            # For now, we'll add a placeholder
            pass
    
    with col2:
        # Chat interface
        chat_interface()
        
        # Text input with form for auto-clearing
        st.markdown("### ✍️ Type Your Message")
        
        with st.form("message_form", clear_on_submit=True):
            user_input = st.text_area(
                "What would you like to discuss about your path to success?",
                height=100,
                placeholder="Ask about goal setting, financial planning, mindset, or any success-related topic...",
                key="user_message"
            )
            
            col_send, col_clear = st.columns([1, 1])
            
            with col_send:
                submitted = st.form_submit_button("Send Message", type="primary")
                
            if submitted and user_input.strip():
                # Add user message to history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                
                # Get coach response
                with st.spinner("Coach is thinking..."):
                    coach_response = get_coach_response(user_input, st.session_state.chat_history)
                
                # Add coach response to history
                st.session_state.chat_history.append({
                    'role': 'coach',
                    'content': coach_response,
                    'timestamp': datetime.now()
                })
                
                # Set speaking state
                st.session_state.is_speaking = True
                
                st.rerun()
        
        # Clear chat button (outside the form)
        if st.button("Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.session_state.is_speaking = False
            st.rerun()
        
        # Show latest coach response with TTS
        if st.session_state.chat_history:
            latest_message = st.session_state.chat_history[-1]
            if latest_message['role'] == 'coach':
                st.markdown("### 🔊 Latest Response")
                st.info(latest_message['content'])
                text_to_speech_component(latest_message['content'])
        
        # Debug section (can be removed in production)
        with st.expander("🔍 Debug Info", expanded=False):
            st.json({
                'api_key_set': bool(st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")),
                'chat_history_length': len(st.session_state.chat_history),
                'user_profile': st.session_state.user_profile,
                'is_speaking': st.session_state.is_speaking
            })
            
            # API Test Button
            if st.button("🧪 Test Gemini API", key="test_api_btn"):
                try:
                    model, model_name = setup_gemini()
                    test_response = model.generate_content("Say 'Hello! API is working perfectly!' in a friendly way.")
                    st.success(f"✅ API Working with {model_name}: {test_response.text}")
                except Exception as e:
                    st.error(f"❌ API Error: {str(e)}")
                    st.info("Possible solutions:\n1. Check your API key\n2. Verify internet connection\n3. Check API quota limits\n4. Try updating your API key")

# CRM tracking (simple file-based)
def log_conversation():
    if st.session_state.chat_history:
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'user_profile': st.session_state.user_profile,
            'conversation': st.session_state.chat_history
        }
        
        # In a real implementation, you'd save this to a database
        # For now, we'll just keep it in session state
        pass

if __name__ == "__main__":
    main()
