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
        justify-content: center;
        align-items: center;
        padding: 2rem;
        background: linear-gradient(135deg, #F8F4FF 0%, #E6E6FA 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.2);
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
    
    /* Slider Purple Theme */
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
    
    /* Slider thumb */
    .stSlider > div > div > div > div > div > div {
        background: #9370DB !important;
        border: 2px solid #8A2BE2 !important;
        box-shadow: 0 2px 8px rgba(138, 43, 226, 0.4) !important;
    }
    
    /* Slider value display */
    .stSlider > div > div > div > div > div > div > div {
        color: #8A2BE2 !important;
        font-weight: bold !important;
    }
    
    /* Slider labels - restore original color - MORE SPECIFIC */
    .stSlider > label,
    .stSlider label,
    .stSlider > div > label,
    div[data-testid="stSlider"] label,
    .stSlider label[data-testid="stWidgetLabel"],
    .css-1d391kg .stSlider label {
        color: rgba(250, 250, 250, 0.6) !important;
        font-weight: 600 !important;
    }
    
    /* Override any purple text in sliders */
    .stSlider label[style*="color: #4A154B"],
    .stSlider label[style*="color: #8A2BE2"] {
        color: rgba(250, 250, 250, 0.6) !important;
    }
    
    /* Ensure all sidebar text is consistent except buttons */
    .css-1d391kg p,
    .css-1d391kg label,
    .css-1d391kg span,
    .css-1d391kg div[data-testid="stMarkdownContainer"] {
        color: rgba(250, 250, 250, 0.6) !important;
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
    
    /* Streamlit slider thumb override */
    .stSlider button[role="slider"] {
        background: #8A2BE2 !important;
        border: 3px solid #6A1B9A !important;
        box-shadow: 0 2px 10px rgba(138, 43, 226, 0.5) !important;
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

# Configure Gemini AI
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

# Speech recognition component
def speech_to_text_component():
    st.markdown("### 🎤 Voice Input")
    
    # Add speech recognition JavaScript
    speech_js = """
    <script>
    function startSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            var recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                document.getElementById('status').innerHTML = 'Listening...';
                document.getElementById('micButton').innerHTML = '🔴 Stop';
            };
            
            recognition.onresult = function(event) {
                var transcript = event.results[0][0].transcript;
                document.getElementById('speechResult').value = transcript;
                document.getElementById('status').innerHTML = 'Speech captured!';
                document.getElementById('micButton').innerHTML = '🎤 Start Recording';
            };
            
            recognition.onerror = function(event) {
                document.getElementById('status').innerHTML = 'Error: ' + event.error;
                document.getElementById('micButton').innerHTML = '🎤 Start Recording';
            };
            
            recognition.onend = function() {
                document.getElementById('micButton').innerHTML = '🎤 Start Recording';
            };
            
            recognition.start();
        } else {
            alert('Speech recognition not supported in this browser');
        }
    }
    </script>
    
    <button onclick="startSpeechRecognition()" id="micButton">🎤 Start Recording</button>
    <div id="status">Ready to listen</div>
    <input type="text" id="speechResult" style="width: 100%; margin-top: 10px;" placeholder="Your speech will appear here">
    """
    
    st.components.v1.html(speech_js, height=150)

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

# Text-to-speech component
def text_to_speech_component(text):
    if text:
        # Get user's voice preferences
        voice_speed = st.session_state.user_profile.get('voice_speed', 0.8)
        voice_pitch = st.session_state.user_profile.get('voice_pitch', 1.0)
        voice_type = st.session_state.user_profile.get('voice_type', 'caring')
        
        # Add emotional context to the text based on content
        empathetic_text = add_empathy_to_text(text, voice_type)
        clean_speech_text = clean_text(empathetic_text)
        
        tts_js = f"""
        <script>
        function speakText() {{
            if ('speechSynthesis' in window) {{
                // Stop any currently playing speech
                speechSynthesis.cancel();
                
                var utterance = new SpeechSynthesisUtterance(`{clean_speech_text}`);
                utterance.rate = {voice_speed};
                utterance.pitch = {voice_pitch};
                utterance.volume = 1.0;
                
                // Load voices and select based on user preference
                var voices = speechSynthesis.getVoices();
                if (voices.length === 0) {{
                    setTimeout(function() {{
                        voices = speechSynthesis.getVoices();
                        selectVoice();
                    }}, 100);
                }} else {{
                    selectVoice();
                }}
                
                function selectVoice() {{
                    var voiceType = '{voice_type}';
                    var selectedVoice = null;
                    
                    // Voice selection based on personality type
                    if (voiceType === 'caring') {{
                        selectedVoice = voices.find(voice => 
                            voice.lang.startsWith('en-') && 
                            (voice.name.includes('Female') || voice.name.includes('Karen') || 
                             voice.name.includes('Susan') || voice.name.includes('Victoria'))
                        );
                    }} else if (voiceType === 'professional') {{
                        selectedVoice = voices.find(voice => 
                            voice.lang.startsWith('en-') && 
                            (voice.name.includes('Samantha') || voice.name.includes('Alex') ||
                             voice.name.includes('Daniel'))
                        );
                    }} else if (voiceType === 'energetic') {{
                        selectedVoice = voices.find(voice => 
                            voice.lang.startsWith('en-') && 
                            (voice.name.includes('Zira') || voice.name.includes('Catherine') ||
                             voice.name.includes('Moira'))
                        );
                    }} else if (voiceType === 'wise') {{
                        selectedVoice = voices.find(voice => 
                            voice.lang.startsWith('en-') && 
                            (voice.name.includes('David') || voice.name.includes('Mark') ||
                             voice.name.includes('Bruce'))
                        );
                    }}
                    
                    // Fallback to any good English voice
                    if (!selectedVoice) {{
                        selectedVoice = voices.find(voice => 
                            voice.lang.startsWith('en-') && voice.quality !== 'low'
                        );
                    }}
                    
                    if (selectedVoice) {{
                        utterance.voice = selectedVoice;
                    }}
                    
                    speechSynthesis.speak(utterance);
                }}
                
                utterance.onstart = function() {{
                    document.getElementById('speakButton').innerHTML = '🔇 Stop Speaking';
                    document.getElementById('speakButton').onclick = function() {{ 
                        speechSynthesis.cancel();
                        document.getElementById('speakButton').innerHTML = '🔊 Play Response';
                        document.getElementById('speakButton').onclick = speakText;
                    }};
                }};
                
                utterance.onend = function() {{
                    document.getElementById('speakButton').innerHTML = '🔊 Play Response';
                    document.getElementById('speakButton').onclick = speakText;
                }};
                
                utterance.onerror = function(event) {{
                    console.error('Speech synthesis error:', event.error);
                    document.getElementById('speakButton').innerHTML = '🔊 Play Response (Error)';
                }};
                
            }} else {{
                alert('Text-to-speech is not supported in this browser. Please try Chrome or Edge.');
            }}
        }}
        
        // Auto-play if enabled
        var autoPlay = {str(st.session_state.user_profile.get('auto_speak', True)).lower()};
        if (autoPlay) {{
            setTimeout(speakText, 800);
        }}
        </script>
        
        <div style="text-align: center; margin: 10px 0;">
            <button id="speakButton" onclick="speakText()" style="
                background: linear-gradient(45deg, #9370DB, #8A2BE2);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(147, 112, 219, 0.4);
                border: 1px solid rgba(138, 43, 226, 0.3);
            " onmouseover="
                this.style.background='linear-gradient(45deg, #8A2BE2, #7B68EE)'; 
                this.style.transform='translateY(-2px)'; 
                this.style.boxShadow='0 6px 20px rgba(147, 112, 219, 0.5)'
            " onmouseout="
                this.style.background='linear-gradient(45deg, #9370DB, #8A2BE2)'; 
                this.style.transform='translateY(0px)'; 
                this.style.boxShadow='0 4px 15px rgba(147, 112, 219, 0.4)'
            ">
                🔊 Play Response
            </button>
        </div>
        """
        
        st.components.v1.html(tts_js, height=80)

# Avatar component
def avatar_component(is_speaking=False):
    avatar_emoji = st.session_state.user_profile.get('avatar', '👩‍💼')
    avatar_class = "avatar speaking" if is_speaking else "avatar"
    
    avatar_html = f"""
    <div class="avatar-container">
        <div class="{avatar_class}">
            {avatar_emoji}
        </div>
    </div>
    """
    
    st.markdown(avatar_html, unsafe_allow_html=True)

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
        # Avatar
        avatar_component(st.session_state.is_speaking)
        
        # Speech input
        speech_to_text_component()
    
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
