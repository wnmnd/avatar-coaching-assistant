import streamlit as st
import google.generativeai as genai
import json
import time
import base64
import re
import requests
from datetime import datetime
import os
import hashlib

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
        min-height: 300px;
    }
    
    .avatar-display {
        text-align: center;
    }
    
    .avatar-emoji {
        font-size: 120px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
        display: block;
    }
    
    .avatar-name {
        font-size: 18px;
        font-weight: bold;
        color: #8A2BE2;
        margin-bottom: 15px;
    }
    
    .voice-visualizer {
        display: flex;
        gap: 4px;
        align-items: end;
        height: 40px;
        opacity: 0;
        transition: opacity 0.3s ease;
        justify-content: center;
    }
    
    .voice-bar {
        width: 6px;
        height: 10px;
        background: linear-gradient(45deg, #8A2BE2, #9370DB);
        border-radius: 3px;
        animation: voice-wave 0.8s ease-in-out infinite;
    }
    
    .voice-bar:nth-child(1) { animation-delay: 0s; }
    .voice-bar:nth-child(2) { animation-delay: 0.1s; }
    .voice-bar:nth-child(3) { animation-delay: 0.2s; }
    .voice-bar:nth-child(4) { animation-delay: 0.3s; }
    .voice-bar:nth-child(5) { animation-delay: 0.4s; }
    
    @keyframes voice-wave {
        0%, 100% { height: 10px; }
        50% { height: 35px; }
    }
    
    .avatar-speaking .avatar-emoji {
        animation: talking 0.5s ease-in-out infinite alternate;
        transform: scale(1.1);
    }
    
    .avatar-speaking .voice-visualizer {
        opacity: 1;
    }
    
    @keyframes talking {
        0% { transform: scale(1.1) rotate(-1deg); }
        100% { transform: scale(1.15) rotate(1deg); }
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
        gap: 15px;
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
    
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
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
    
    .crm-container {
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid rgba(138, 43, 226, 0.2);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# CRM System Functions
def get_crm_file_path():
    """Get the path to CRM data file"""
    return "crm_data.json"

def load_crm_data():
    """Load CRM data from file"""
    crm_file = get_crm_file_path()
    try:
        if os.path.exists(crm_file):
            with open(crm_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading CRM data: {str(e)}")
    return {}

def save_crm_data(data):
    """Save CRM data to file"""
    crm_file = get_crm_file_path()
    try:
        with open(crm_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        st.error(f"Error saving CRM data: {str(e)}")
        return False

def create_user_key(nickname, email):
    """Create a unique key for user identification"""
    return hashlib.md5(f"{nickname.lower()}:{email.lower()}".encode()).hexdigest()

def save_user_to_crm(nickname, email, goals, chat_history, user_profile):
    """Save user data to CRM"""
    crm_data = load_crm_data()
    user_key = create_user_key(nickname, email)
    
    user_data = {
        'nickname': nickname,
        'email': email,
        'goals': goals,
        'chat_history': chat_history,
        'user_profile': user_profile,
        'last_updated': datetime.now().isoformat(),
        'created_date': crm_data.get(user_key, {}).get('created_date', datetime.now().isoformat())
    }
    
    crm_data[user_key] = user_data
    return save_crm_data(crm_data)

def load_user_from_crm(nickname, email):
    """Load user data from CRM"""
    crm_data = load_crm_data()
    user_key = create_user_key(nickname, email)
    return crm_data.get(user_key)

def get_all_users_summary():
    """Get summary of all users in CRM"""
    crm_data = load_crm_data()
    summary = []
    for user_key, user_data in crm_data.items():
        summary.append({
            'nickname': user_data.get('nickname', 'Unknown'),
            'email': user_data.get('email', 'Unknown'),
            'chat_messages': len(user_data.get('chat_history', [])),
            'last_updated': user_data.get('last_updated', 'Unknown')
        })
    return summary

# Initialize session state
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'is_speaking' not in st.session_state:
        st.session_state.is_speaking = False
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'voice_played' not in st.session_state:
        st.session_state.voice_played = False
    if 'voice_message_ready' not in st.session_state:
        st.session_state.voice_message_ready = None
    if 'crm_logged_in' not in st.session_state:
        st.session_state.crm_logged_in = False
    if 'crm_user_data' not in st.session_state:
        st.session_state.crm_user_data = {}

# Configure APIs
def setup_gemini():
    # Use your Gemini API key directly
    api_key = "AIzaSyA9VPlM-MSjDYytvd4J2wQ_f1nc5Tmd7dk"
    
    # Also check secrets/environment as fallback
    if not api_key:
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("❌ Gemini API key not found")
        st.stop()
    
    try:
        genai.configure(api_key=api_key)
        model_names = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                test_response = model.generate_content("Say 'Connected'")
                if test_response and test_response.text:
                    # Show success message
                    return model, model_name
            except Exception as e:
                continue
        
        st.error("❌ Could not connect to any Gemini model")
        st.stop()
                
    except Exception as e:
        st.error(f"❌ Gemini API Error: {str(e)}")
        st.stop()

def setup_elevenlabs():
    """Setup ElevenLabs for natural voice"""
    # Use your API key
    api_key = "sk_11bac39a10fe50c34f1e5f11abdcae05780e0369489d918d"
    
    # Also check secrets/environment as fallback
    if not api_key:
        api_key = st.secrets.get("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY")
    
    if api_key and api_key.startswith("sk_"):
        return api_key
    else:
        return None

# Fixed Avatar Component
def avatar_component(is_speaking=False):
    """Display fixed avatar with proper rendering"""
    
    profile = st.session_state.user_profile
    avatar_choice = profile.get('avatar', 'sophia')
    
    # Avatar selection with personality and gender
    avatar_configs = {
        'sophia': {'emoji': '👩‍💼', 'name': 'Sophia', 'voice_id': 'LcfcDJNUP1GQjkzn1xUU', 'gender': 'female'},
        'marcus': {'emoji': '👨‍💼', 'name': 'Marcus', 'voice_id': 'pNInz6obpgDQGcFmaJgB', 'gender': 'male'}, 
        'elena': {'emoji': '👩‍⚕️', 'name': 'Elena', 'voice_id': 'jsCqWAovK2LkecY7zXl4', 'gender': 'female'},
        'david': {'emoji': '👨‍🎓', 'name': 'David', 'voice_id': 'VR6AewLTigWG4xSOukaG', 'gender': 'male'},
        'maya': {'emoji': '👩‍🏫', 'name': 'Maya', 'voice_id': 'z9fAnlkpzviPz146aGWa', 'gender': 'female'},
        'james': {'emoji': '👨‍💻', 'name': 'James', 'voice_id': 'ErXwobaYiN019PkySvjV', 'gender': 'male'}
    }
    
    config = avatar_configs.get(avatar_choice, avatar_configs['sophia'])
    avatar_emoji = config['emoji']
    avatar_name = config['name']
    
    # Simplified but effective avatar display
    speaking_class = "avatar-speaking" if is_speaking else ""
    status_text = f"🎤 {avatar_name} is speaking..." if is_speaking else f"💭 {avatar_name} is ready to help"
    
    avatar_html = f"""
    <div class="avatar-container">
        <div class="avatar-display {speaking_class}" id="avatarDisplay">
            <div class="avatar-emoji">{avatar_emoji}</div>
            <div class="avatar-name">{avatar_name}</div>
            <div class="voice-visualizer">
                <div class="voice-bar"></div>
                <div class="voice-bar"></div>
                <div class="voice-bar"></div>
                <div class="voice-bar"></div>
                <div class="voice-bar"></div>
            </div>
        </div>
        <div class="avatar-status">{status_text}</div>
    </div>
    """
    
    st.markdown(avatar_html, unsafe_allow_html=True)

# Enhanced Voice Recorder with CRM Integration
def enhanced_voice_recorder():
    """Big button that auto-detects when you finish speaking"""
    
    voice_recorder_html = f"""
    <div style="
        padding: 25px;
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        border-radius: 20px;
        border: 2px solid rgba(138, 43, 226, 0.2);
        margin: 10px 0;
        text-align: center;
    ">
        <div id="voiceStatus" style="
            padding: 20px;
            background: white;
            border-radius: 15px;
            margin-bottom: 25px;
            color: #8A2BE2;
            font-weight: bold;
            font-size: 18px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        ">
            🎤 Click to start recording
        </div>
        
        <div id="transcriptionBox" style="
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 25px;
            min-height: 60px;
            border: 2px dashed #ddd;
            color: #333;
            font-size: 16px;
            display: none;
        ">
            Your speech will appear here...
        </div>
        
        <button id="voiceBtn" onclick="handleVoiceClick()" style="
            background: linear-gradient(135deg, #8A2BE2, #9370DB);
            border: none;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            color: white;
            font-size: 48px;
            cursor: pointer;
            box-shadow: 0 8px 30px rgba(138, 43, 226, 0.4);
            transition: all 0.3s ease;
            margin: 15px;
        ">🎤</button>
        
        <div style="margin-top: 20px; color: #666; font-size: 16px; font-weight: bold;">
            Click to record • Automatically detects when you finish speaking
        </div>
        
        <textarea id="hiddenVoiceText" style="position: absolute; left: -9999px; opacity: 0;" 
                  placeholder="voice_transcription_area"></textarea>
    </div>

    <script>
    let recognition = null;
    let isRecording = false;
    let recordedText = '';
    let silenceTimer = null;
    let finalTranscript = '';
    
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {{
            console.log('Recording started');
            updateStatus('🔴 Listening... Speak your message clearly');
            showTranscription();
            finalTranscript = '';
        }};
        
        recognition.onresult = function(event) {{
            let interimText = '';
            finalTranscript = '';
            
            for (let i = 0; i < event.results.length; i++) {{
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {{
                    finalTranscript += transcript + ' ';
                }} else {{
                    interimText += transcript;
                }}
            }}
            
            recordedText = (finalTranscript + interimText).trim();
            document.getElementById('transcriptionBox').innerHTML = '📝 "' + recordedText + '"';
            
            if (silenceTimer) {{
                clearTimeout(silenceTimer);
            }}
            
            if (finalTranscript.trim()) {{
                silenceTimer = setTimeout(() => {{
                    if (isRecording) {{
                        completeRecording();
                    }}
                }}, 3000);
            }}
        }};
        
        recognition.onend = function() {{
            console.log('Recognition ended');
            if (isRecording) {{
                completeRecording();
            }}
        }};
        
        recognition.onerror = function(event) {{
            console.error('Speech error:', event.error);
            updateStatus('❌ Error: ' + event.error + '. Click to try again.');
            resetButton();
        }};
    }} else {{
        updateStatus('❌ Voice not supported. Use Chrome/Edge browser.');
    }}
    
    function handleVoiceClick() {{
        if (!recognition) {{
            alert('Voice recognition not available. Please use Chrome or Edge browser.');
            return;
        }}
        
        if (!isRecording) {{
            startRecording();
        }} else {{
            stopRecording();
        }}
    }}
    
    function startRecording() {{
        isRecording = true;
        recordedText = '';
        finalTranscript = '';
        
        const btn = document.getElementById('voiceBtn');
        btn.style.background = 'linear-gradient(135deg, #ff4757, #ff3742)';
        btn.innerHTML = '🔴';
        btn.style.animation = 'pulse 1.5s infinite';
        
        try {{
            recognition.start();
        }} catch (error) {{
            console.error('Failed to start recording:', error);
            updateStatus('❌ Failed to start. Click to try again.');
            resetButton();
        }}
    }}
    
    function stopRecording() {{
        isRecording = false;
        recognition.stop();
        
        if (silenceTimer) {{
            clearTimeout(silenceTimer);
        }}
        
        completeRecording();
    }}
    
    function completeRecording() {{
        isRecording = false;
        recognition.stop();
        
        if (silenceTimer) {{
            clearTimeout(silenceTimer);
        }}
        
        const finalMessage = (finalTranscript || recordedText).trim();
        
        if (!finalMessage) {{
            updateStatus('❌ No speech detected. Click to try again.');
            resetButton();
            return;
        }}
        
        updateStatus('✅ Message recorded and sent automatically!');
        
        const hiddenTextArea = document.getElementById('hiddenVoiceText');
        hiddenTextArea.value = finalMessage;
        
        // Auto-send the voice message
        const url = new URL(window.location.href);
        url.searchParams.set('voice_input', encodeURIComponent(finalMessage));
        url.searchParams.set('timestamp', Date.now().toString());
        window.location.href = url.toString();
        
        const btn = document.getElementById('voiceBtn');
        btn.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
        btn.innerHTML = '✅';
        btn.style.animation = 'none';
        
        document.getElementById('transcriptionBox').innerHTML = '✅ Sent: "' + finalMessage + '"';
    }}
    
    function updateStatus(message) {{
        document.getElementById('voiceStatus').innerHTML = message;
    }}
    
    function showTranscription() {{
        document.getElementById('transcriptionBox').style.display = 'block';
    }}
    
    function resetButton() {{
        isRecording = false;
        const btn = document.getElementById('voiceBtn');
        btn.style.background = 'linear-gradient(135deg, #8A2BE2, #9370DB)';
        btn.innerHTML = '🎤';
        btn.style.animation = 'none';
        updateStatus('🎤 Click to start recording');
        document.getElementById('transcriptionBox').style.display = 'none';
        recordedText = '';
        finalTranscript = '';
        
        if (silenceTimer) {{
            clearTimeout(silenceTimer);
        }}
        
        const hiddenTextArea = document.getElementById('hiddenVoiceText');
        hiddenTextArea.value = '';
    }}
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {{
            0% {{ transform: scale(1); box-shadow: 0 8px 30px rgba(255, 71, 87, 0.4); }}
            50% {{ transform: scale(1.05); box-shadow: 0 12px 40px rgba(255, 71, 87, 0.8); }}
            100% {{ transform: scale(1); box-shadow: 0 8px 30px rgba(255, 71, 87, 0.4); }}
        }}
    `;
    document.head.appendChild(style);
    </script>
    """
    
    st.components.v1.html(voice_recorder_html, height=450)

# Natural Voice Component (cleaned up)
def natural_voice_component(text, voice_type="professional"):
    """Enhanced voice playback with clean interface"""
    if not text or st.session_state.get('voice_played', False):
        return
    
    st.session_state.voice_played = True
    
    profile = st.session_state.user_profile
    avatar_choice = profile.get('avatar', 'sophia')
    avatar_configs = {
        'sophia': {'gender': 'female', 'voice_id': 'LcfcDJNUP1GQjkzn1xUU', 'name': 'Emily'},
        'marcus': {'gender': 'male', 'voice_id': 'pNInz6obpgDQGcFmaJgB', 'name': 'Adam'}, 
        'elena': {'gender': 'female', 'voice_id': 'jsCqWAovK2LkecY7zXl4', 'name': 'Freya'},
        'david': {'gender': 'male', 'voice_id': 'VR6AewLTigWG4xSOukaG', 'name': 'Arnold'},
        'maya': {'gender': 'female', 'voice_id': 'z9fAnlkpzviPz146aGWa', 'name': 'Glinda'},
        'james': {'gender': 'male', 'voice_id': 'ErXwobaYiN019PkySvjV', 'name': 'Antoni'}
    }
    avatar_info = avatar_configs.get(avatar_choice, avatar_configs['sophia'])
    
    elevenlabs_key = setup_elevenlabs()
    
    if elevenlabs_key and elevenlabs_key.startswith("sk_"):
        create_instant_elevenlabs_voice(text, elevenlabs_key, voice_type, avatar_info)
    else:
        create_mobile_friendly_voice(text, voice_type, avatar_info['gender'])

def create_mobile_friendly_voice(text, voice_type, gender):
    """Mobile-friendly browser TTS"""
    
    clean_text = enhance_text_for_speech(text, voice_type)
    
    voice_settings = {
        'caring': {'rate': 0.75, 'pitch': 1.2},
        'professional': {'rate': 0.9, 'pitch': 1.0},
        'energetic': {'rate': 1.3, 'pitch': 1.4}
    }
    
    settings = voice_settings.get(voice_type, voice_settings['professional'])
    
    if gender == 'male':
        settings['pitch'] = max(0.4, settings['pitch'] - 0.4)
    else:
        settings['pitch'] = min(1.6, settings['pitch'] + 0.2)
    
    voice_html = f"""
    <div style="
        padding: 15px;
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        border-radius: 15px;
        border: 1px solid rgba(138, 43, 226, 0.2);
        margin: 10px 0;
        text-align: center;
    ">
        <div style="margin-bottom: 10px; color: #8A2BE2; font-weight: bold;">
            Your coach is speaking...
        </div>
        <button id="playVoiceButton" onclick="playVoiceManually()" style="
            background: linear-gradient(135deg, #8A2BE2, #9370DB);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 10px 20px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3);
            display: none;
        ">
            🔊 Tap to hear voice (Mobile)
        </button>
    </div>

    <script>
    let isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    let voiceUtterance = null;
    
    function playVoiceMobileFriendly() {{
        if ('speechSynthesis' in window) {{
            speechSynthesis.cancel();
            
            voiceUtterance = new SpeechSynthesisUtterance(`{clean_text}`);
            voiceUtterance.rate = {settings['rate']};
            voiceUtterance.pitch = {settings['pitch']};
            voiceUtterance.volume = 1.0;
            
            const voices = speechSynthesis.getVoices();
            let bestVoice;
            
            if ('{gender}' === 'male') {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    v.name.toLowerCase().includes('male')
                );
            }} else {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    v.name.toLowerCase().includes('female')
                );
            }}
            
            if (!bestVoice) {{
                bestVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
            }}
            
            if (bestVoice) {{
                voiceUtterance.voice = bestVoice;
            }}
            
            speechSynthesis.speak(voiceUtterance);
        }}
    }}
    
    function playVoiceManually() {{
        const button = document.getElementById('playVoiceButton');
        button.style.display = 'none';
        playVoiceMobileFriendly();
    }}
    
    if (isMobileDevice) {{
        document.getElementById('playVoiceButton').style.display = 'inline-block';
    }} else {{
        if (speechSynthesis.getVoices().length > 0) {{
            setTimeout(playVoiceMobileFriendly, 500);
        }} else {{
            speechSynthesis.onvoiceschanged = function() {{
                setTimeout(playVoiceMobileFriendly, 500);
            }};
        }}
    }}
    
    setTimeout(() => {{
        if (!isMobileDevice || speechSynthesis.speaking) {{
            document.getElementById('playVoiceButton').style.display = 'none';
        }}
    }}, 1000);
    </script>
    """
    
    st.components.v1.html(voice_html, height=120)

def create_instant_elevenlabs_voice(text, api_key, voice_type, avatar_info):
    """Clean ElevenLabs voice with minimal UI"""
    
    if not api_key or not api_key.startswith("sk_") or len(api_key) < 20:
        st.error(f"❌ Invalid ElevenLabs API key format")
        return
    
    voice_id = avatar_info['voice_id']
    voice_name = f"{avatar_info['name']} ({avatar_info['gender']})"
    
    personality_settings = {
        'caring': {
            'stability': 0.8,
            'similarity_boost': 0.9,
            'style': 0.2,
            'speed': 0.8
        },
        'professional': {
            'stability': 0.9,
            'similarity_boost': 0.8,
            'style': 0.4,
            'speed': 1.0
        },
        'energetic': {
            'stability': 0.5,
            'similarity_boost': 0.7,
            'style': 0.8,
            'speed': 1.2
        }
    }
    
    settings = personality_settings.get(voice_type, personality_settings['professional'])
    clean_text = enhance_text_for_speech(text, voice_type)
    
    voice_html = f"""
    <div style="
        padding: 15px;
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        border-radius: 15px;
        border: 1px solid rgba(138, 43, 226, 0.2);
        margin: 10px 0;
        text-align: center;
    ">
        <div style="margin-bottom: 10px; color: #8A2BE2; font-weight: bold;">
            🎤 {voice_name} is speaking...
        </div>
        
        <div id="voiceStatus" style="
            padding: 10px; 
            background: white; 
            border-radius: 8px; 
            margin: 10px 0;
            color: #333;
            font-size: 14px;
        ">
            Initializing voice...
        </div>
        
        <button onclick="retryVoice()" style="
            background: linear-gradient(135deg, #8A2BE2, #9370DB);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 12px;
            cursor: pointer;
            margin: 5px;
        ">Retry</button>
    </div>
    
    <script>
    if (window.speechSynthesis) {{
        window.speechSynthesis.cancel();
    }}
    
    function updateVoiceStatus(message, color = '#333') {{
        const statusDiv = document.getElementById('voiceStatus');
        statusDiv.innerHTML = message;
        statusDiv.style.color = color;
    }}
    
    function retryVoice() {{
        playInstantVoice();
    }}
    
    async function playInstantVoice() {{
        updateVoiceStatus('Connecting to ElevenLabs...', '#4169e1');
        
        try {{
            const requestBody = {{
                text: `{clean_text}`,
                model_id: 'eleven_monolingual_v1',
                voice_settings: {{
                    stability: {settings['stability']},
                    similarity_boost: {settings['similarity_boost']},
                    style: {settings['style']},
                    use_speaker_boost: true,
                    speed: {settings['speed']}
                }}
            }};
            
            const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/{voice_id}', {{
                method: 'POST',
                headers: {{
                    'Accept': 'audio/mpeg',
                    'Content-Type': 'application/json',
                    'xi-api-key': '{api_key}'
                }},
                body: JSON.stringify(requestBody)
            }});
            
            if (response.ok) {{
                updateVoiceStatus('Playing voice...', '#28a745');
                
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                audio.play().then(() => {{
                    updateVoiceStatus('{voice_name} speaking', '#28a745');
                }}).catch(error => {{
                    updateVoiceStatus('⚠Audio blocked - using browser fallback', '#ff8c00');
                    setTimeout(fallbackToBrowserTTS, 500);
                }});
                
                audio.onended = function() {{
                    URL.revokeObjectURL(audioUrl);
                    updateVoiceStatus('✅ Voice completed', '#28a745');
                }};
                
            }} else {{
                updateVoiceStatus('❌ ElevenLabs error - using browser fallback', '#dc3545');
                setTimeout(fallbackToBrowserTTS, 1000);
            }}
            
        }} catch (error) {{
            updateVoiceStatus('❌ Network error - using browser fallback', '#dc3545');
            setTimeout(fallbackToBrowserTTS, 1000);
        }}
    }}
    
    function fallbackToBrowserTTS() {{
        updateVoiceStatus('🤖 Using browser voice', '#ff8c00');
        
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(`{clean_text}`);
            utterance.rate = {settings['speed'] * 0.9};
            utterance.pitch = {0.6 if avatar_info['gender'] == 'male' else 1.2};
            utterance.volume = 1.0;
            
            const voices = speechSynthesis.getVoices();
            let bestVoice = voices.find(v => 
                v.lang.startsWith('en-') && 
                v.name.toLowerCase().includes('{avatar_info['gender']}')
            ) || voices.find(v => v.lang.startsWith('en-')) || voices[0];
            
            if (bestVoice) {{
                utterance.voice = bestVoice;
            }}
            
            utterance.onstart = function() {{
                updateVoiceStatus('Browser voice playing', '#ff8c00');
            }};
            
            utterance.onend = function() {{
                updateVoiceStatus('Browser voice completed', '#ff8c00');
            }};
            
            speechSynthesis.speak(utterance);
        }}
    }}
    
    setTimeout(playInstantVoice, 500);
    </script>
    """
    
    st.components.v1.html(voice_html, height=120)

def enhance_text_for_speech(text, voice_type):
    """Make text more expressive for voice"""
    
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = text.replace('\n', ' ').strip()
    
    if voice_type == 'caring':
        text = re.sub(r'\byou\b', 'you, dear', text, flags=re.IGNORECASE, count=1)
        text = text.replace(' can ', ' absolutely can ')
        
    elif voice_type == 'energetic':
        text = re.sub(r'\bgreat\b', 'absolutely AMAZING', text, flags=re.IGNORECASE)
        text = text.replace(' can ', ' can totally ')
        text += ' I\'m excited for you!'
        
    elif voice_type == 'professional':
        text = text.replace(' should ', ' must strategically ')
    
    text = re.sub(r'([.!?])', r'\1 ', text)
    text = re.sub(r'([,:])', r'\1 ', text)
    
    text = text.replace('"', '\\"').replace("'", "\\'")
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def load_coaching_knowledge():
    return """
    You are a professional success and wealth coach with a warm, human personality. 
    
    CORE PRINCIPLES:
    - Success requires daily disciplined actions and consistent learning
    - True wealth encompasses money, time, purpose, and freedom
    - Focus on actionable strategies and practical steps
    
    COACHING STYLE:
    - Be conversational and natural, like a real human coach
    - Ask thoughtful questions to understand the client
    - Provide specific, actionable advice
    - Show genuine care and empathy
    - Use examples and stories to illustrate points
    - Keep responses under 100 words for natural conversation flow
    """

def get_coach_response(user_input, chat_history):
    try:
        model, model_name = setup_gemini()
        
        profile = st.session_state.user_profile
        name = profile.get('name', 'there')
        voice_type = profile.get('voice_type', 'caring')
        goals = profile.get('goals', 'general success')
        
        context = f"""You are a {voice_type} success coach speaking to {name}.
        Their goals: {goals}
        
        Recent conversation:"""
        
        for msg in chat_history[-3:]:
            role = "Coach" if msg['role'] == 'coach' else name
            context += f"\n{role}: {msg['content']}"
        
        context += f"\n{name}: {user_input}"
        
        prompt = f"""{context}
        
        Respond as a {voice_type} human coach. Be natural, conversational, and helpful. 
        Keep it under 80 words and ask a follow-up question to continue the conversation."""
        
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.8,
                'max_output_tokens': 150,
                'top_p': 0.9
            }
        )
        
        if response and response.text:
            return response.text.strip()
        else:
            return f"I'm here to help you, {name}. What's on your mind today?"
            
    except Exception as e:
        name = st.session_state.user_profile.get('name', 'there')
        return f"I'm still here for you, {name}. Could you share that with me again?"

def chat_interface():
    st.markdown("### Conversation")
    
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="coach-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def crm_login_interface():
    """CRM Login Interface"""
    st.markdown("""
    <div class="crm-container">
        <h3 style="color: #8A2BE2; text-align: center; margin-bottom: 20px;">
            Welcome to Avatar Success Coach
        </h3>
        <p style="text-align: center; margin-bottom: 20px; color: #666;">
            Enter your details to continue or create a new session
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("crm_login_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nickname = st.text_input("Nickname", placeholder="Enter your nickname")
        
        with col2:
            email = st.text_input("Email", placeholder="your.email@example.com")
        
        goals = st.text_area("Your Goals", placeholder="What do you want to achieve?", height=100)
        
        login_submitted = st.form_submit_button("🚀 Start Coaching Session", type="primary")
        
        if login_submitted:
            if nickname.strip() and email.strip():
                # Try to load existing user
                existing_user = load_user_from_crm(nickname, email)
                
                if existing_user:
                    # Restore previous session
                    st.session_state.chat_history = existing_user.get('chat_history', [])
                    st.session_state.user_profile = existing_user.get('user_profile', {})
                    st.session_state.crm_user_data = existing_user
                    st.success(f"Welcome back, {nickname}! Your previous session has been restored.")
                    st.info(f"You have {len(st.session_state.chat_history)} previous messages.")
                else:
                    # Create new user
                    st.session_state.chat_history = []
                    st.session_state.user_profile = {
                        'name': nickname,
                        'goals': goals,
                        'avatar': 'sophia',
                        'voice_type': 'caring'
                    }
                    st.session_state.crm_user_data = {
                        'nickname': nickname,
                        'email': email,
                        'goals': goals
                    }
                    st.success(f"Welcome, {nickname}! Starting your new coaching journey.")
                
                st.session_state.crm_logged_in = True
                
                # Save to CRM
                save_user_to_crm(
                    nickname, 
                    email, 
                    goals, 
                    st.session_state.chat_history, 
                    st.session_state.user_profile
                )
                
                st.rerun()
            else:
                st.error("Please enter both nickname and email to continue.")

def user_profile_sidebar():
    """Enhanced sidebar with CRM integration"""
    with st.sidebar:
        if st.session_state.crm_logged_in:
            # User info display
            user_data = st.session_state.crm_user_data
            st.markdown(f"""
            ### Welcome, {user_data.get('nickname', 'User')}!
            **Email:** {user_data.get('email', 'N/A')}  
            **💬 Messages:** {len(st.session_state.chat_history)}
            """)
            
            # Logout button
            if st.button("Logout", type="secondary"):
                # Save current session before logout
                save_user_to_crm(
                    user_data.get('nickname', ''),
                    user_data.get('email', ''),
                    st.session_state.user_profile.get('goals', ''),
                    st.session_state.chat_history,
                    st.session_state.user_profile
                )
                
                # Clear session
                st.session_state.crm_logged_in = False
                st.session_state.chat_history = []
                st.session_state.user_profile = {}
                st.session_state.crm_user_data = {}
                st.rerun()
            
            st.markdown("---")
        
        st.header("Coach Settings")
        
        # Basic info
        name = st.text_input("Your Name", value=st.session_state.user_profile.get('name', ''))
        goals = st.text_area("Your Goals", value=st.session_state.user_profile.get('goals', ''))
        
        # Avatar choices (cleaned up)
        st.subheader("Choose Your AI Coach")
        avatar_options = {
            "sophia": "👩‍💼 Sophia - Professional Female Coach",
            "marcus": "👨‍💼 Marcus - Business Male Mentor", 
            "elena": "👩‍⚕️ Elena - Caring Female Guide",
            "david": "👨‍🎓 David - Wise Male Advisor",
            "maya": "👩‍🏫 Maya - Energetic Female Coach",
            "james": "👨‍💻 James - Executive Male Coach"
        }
        
        avatar_choice = st.selectbox(
            "Select Your Coach Avatar",
            options=list(avatar_options.keys()),
            format_func=lambda x: avatar_options[x],
            index=list(avatar_options.keys()).index(
                st.session_state.user_profile.get('avatar', 'sophia')
            )
        )
        
        # Voice personality
        st.subheader("Voice Personality")
        voice_type = st.selectbox(
            "Coach Personality",
            ["caring", "professional", "energetic"],
            index=["caring", "professional", "energetic"].index(
                st.session_state.user_profile.get('voice_type', 'caring')
            ),
            format_func=lambda x: {
                'caring': 'Caring & Supportive',
                'professional': 'Professional & Direct', 
                'energetic': 'Energetic & Motivating'
            }[x]
        )
        
        # Save profile
        if st.button("Save Settings", type="primary"):
            st.session_state.user_profile = {
                'name': name,
                'goals': goals,
                'avatar': avatar_choice,
                'voice_type': voice_type
            }
            
            # Save to CRM if logged in
            if st.session_state.crm_logged_in:
                user_data = st.session_state.crm_user_data
                save_user_to_crm(
                    user_data.get('nickname', ''),
                    user_data.get('email', ''),
                    goals,
                    st.session_state.chat_history,
                    st.session_state.user_profile
                )
            
            st.success("✅ Settings saved!")
            st.rerun()
        
        # CRM Admin (optional)
        if st.checkbox("🔧 Show CRM Admin"):
            st.subheader("📊 CRM Statistics")
            users_summary = get_all_users_summary()
            st.write(f"**Total Users:** {len(users_summary)}")
            
            for user in users_summary[-3:]:  # Show last 3 users
                st.write(f"• **{user['nickname']}** - {user['chat_messages']} messages")

def process_voice_input():
    """Process voice input from URL parameters with CRM integration"""
    if 'voice_input' in st.query_params and 'timestamp' in st.query_params:
        voice_message = st.query_params['voice_input']
        timestamp = st.query_params['timestamp']
        
        # Clear the parameters immediately
        del st.query_params['voice_input']
        del st.query_params['timestamp']
        
        if voice_message.strip():
            st.session_state.voice_played = False
            
            # Add user message to conversation
            st.session_state.chat_history.append({
                'role': 'user',
                'content': voice_message.strip(),
                'timestamp': datetime.now()
            })
            
            # Get coach response
            with st.spinner("Your coach is responding..."):
                coach_response = get_coach_response(voice_message, st.session_state.chat_history)
            
            # Add coach response to conversation
            st.session_state.chat_history.append({
                'role': 'coach',
                'content': coach_response,
                'timestamp': datetime.now()
            })
            
            # Save to CRM
            if st.session_state.crm_logged_in:
                user_data = st.session_state.crm_user_data
                save_user_to_crm(
                    user_data.get('nickname', ''),
                    user_data.get('email', ''),
                    st.session_state.user_profile.get('goals', ''),
                    st.session_state.chat_history,
                    st.session_state.user_profile
                )
            
            st.session_state.is_speaking = True
            st.success(f"🎤 Voice message processed: \"{voice_message}\"")
            st.rerun()

def main():
    load_css()
    init_session_state()
    
    # Process voice input first
    process_voice_input()
    
    # Check if user is logged in
    if not st.session_state.crm_logged_in:
        crm_login_interface()
        return
    
    # Reset voice played flag on new interaction
    if 'last_chat_length' not in st.session_state:
        st.session_state.last_chat_length = 0
    
    current_chat_length = len(st.session_state.chat_history)
    if current_chat_length > st.session_state.last_chat_length:
        st.session_state.voice_played = False
        st.session_state.last_chat_length = current_chat_length
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Avatar Success Coach</h1>
        <p>Your AI-powered success mentor with instant talking avatars</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    user_profile_sidebar()
    
    # Show greeting for new users
    if st.session_state.user_profile and not st.session_state.chat_history:
        name = st.session_state.user_profile.get('name', 'there')
        avatar = st.session_state.user_profile.get('avatar', 'sophia')
        
        greeting = f"Hello {name}! I'm {avatar.title()}, your personal success coach. I'm here to help you achieve your wealth and success goals. What would you like to work on today?"
        
        st.session_state.chat_history.append({
            'role': 'coach',
            'content': greeting,
            'timestamp': datetime.now()
        })
        st.session_state.is_speaking = True
    
    # Main layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Avatar display
        avatar_component(st.session_state.is_speaking)
        
        # Voice playback for NEW coach messages only
        if (st.session_state.chat_history and 
            st.session_state.chat_history[-1]['role'] == 'coach' and 
            st.session_state.is_speaking and 
            not st.session_state.voice_played):
            
            latest_response = st.session_state.chat_history[-1]['content']
            voice_type = st.session_state.user_profile.get('voice_type', 'professional')
            natural_voice_component(latest_response, voice_type)
        
        if st.session_state.is_speaking:
            st.session_state.is_speaking = False
    
    with col2:
        # Chat interface
        chat_interface()
        
        # Regular text input
        st.markdown("### Send Message")
        
        with st.form("message_form", clear_on_submit=True):
            user_input = st.text_area(
                "Type your message:",
                height=80,
                placeholder="Ask about your goals, challenges, or anything related to success...",
                key="user_text_input"
            )
            
            submitted = st.form_submit_button("Send", type="primary")
            
            if submitted and user_input.strip():
                st.session_state.voice_played = False
                
                # Add user message
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                
                # Get coach response
                with st.spinner("Your coach is thinking..."):
                    coach_response = get_coach_response(user_input, st.session_state.chat_history)
                
                # Add coach response
                st.session_state.chat_history.append({
                    'role': 'coach',
                    'content': coach_response,
                    'timestamp': datetime.now()
                })
                
                # Save to CRM
                if st.session_state.crm_logged_in:
                    user_data = st.session_state.crm_user_data
                    save_user_to_crm(
                        user_data.get('nickname', ''),
                        user_data.get('email', ''),
                        st.session_state.user_profile.get('goals', ''),
                        st.session_state.chat_history,
                        st.session_state.user_profile
                    )
                
                st.session_state.is_speaking = True
                st.rerun()
        
        # Voice recording section
        st.markdown("---")
        st.markdown("### Voice Message")
        
        # Voice recorder
        enhanced_voice_recorder()
        
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.is_speaking = False
            st.session_state.voice_played = False
            
            # Save cleared chat to CRM
            if st.session_state.crm_logged_in:
                user_data = st.session_state.crm_user_data
                save_user_to_crm(
                    user_data.get('nickname', ''),
                    user_data.get('email', ''),
                    st.session_state.user_profile.get('goals', ''),
                    st.session_state.chat_history,
                    st.session_state.user_profile
                )
            
            st.rerun()

if __name__ == "__main__":
    main()
