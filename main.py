import streamlit as st
import google.generativeai as genai
import json
import time
import base64
import re
import requests
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
    if 'voice_played' not in st.session_state:
        st.session_state.voice_played = False

# Configure APIs
def setup_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        st.error("❌ Please set your Gemini API key in .streamlit/secrets.toml")
        st.stop()
   
    try:
        genai.configure(api_key=api_key)
        model_names = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
       
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                test_response = model.generate_content("Say 'Connected'")
                if test_response and test_response.text:
                    return model, model_name
            except:
                continue
       
        st.error("❌ Could not connect to Gemini")
        st.stop()
               
    except Exception as e:
        st.error(f"❌ Gemini API Error: {str(e)}")
        st.stop()

def setup_heygen():
    """Setup HeyGen API (kept for compatibility)"""
    return st.secrets.get("HEYGEN_API_KEY") or os.getenv("HEYGEN_API_KEY")

def setup_elevenlabs():
    """Setup ElevenLabs for natural voice"""
    return st.secrets.get("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY")

# Fixed Avatar Component
def avatar_component(is_speaking=False):
    """Display fixed avatar with proper rendering"""
   
    profile = st.session_state.user_profile
    avatar_choice = profile.get('avatar', 'sophia')
   
    # Avatar selection with personality and gender
    avatar_configs = {
        'sophia': {'emoji': '👩‍💼', 'name': 'Sophia', 'voice_type': 'professional', 'gender': 'female'},
        'marcus': {'emoji': '👨‍💼', 'name': 'Marcus', 'voice_type': 'confident', 'gender': 'male'},
        'elena': {'emoji': '👩‍⚕️', 'name': 'Elena', 'voice_type': 'caring', 'gender': 'female'},
        'david': {'emoji': '👨‍🎓', 'name': 'David', 'voice_type': 'wise', 'gender': 'male'},
        'maya': {'emoji': '👩‍🏫', 'name': 'Maya', 'voice_type': 'energetic', 'gender': 'female'},
        'james': {'emoji': '👨‍💻', 'name': 'James', 'voice_type': 'executive', 'gender': 'male'}
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

# WhatsApp-style Voice Note Component
def whatsapp_voice_note():
    """WhatsApp-style voice recording interface"""
   
    st.markdown("### 🎤 Voice Message")
   
    # Voice note container
    voice_html = """
    <div class="voice-note-container">
        <div class="voice-controls">
            <button id="voiceButton"
                    onmousedown="startRecording()"
                    onmouseup="stopRecording()"
                    ontouchstart="startRecording()"
                    ontouchend="stopRecording()"
                    style="
                        background: linear-gradient(135deg, #8A2BE2, #9370DB);
                        border: none;
                        border-radius: 50%;
                        width: 70px;
                        height: 70px;
                        color: white;
                        font-size: 28px;
                        cursor: pointer;
                        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.4);
                        transition: all 0.2s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        user-select: none;
                        -webkit-user-select: none;
                    "
                    onmouseover="if(!this.classList.contains('recording')) this.style.transform='scale(1.1)'"
                    onmouseout="if(!this.classList.contains('recording')) this.style.transform='scale(1)'">
                🎤
            </button>
            <div id="recordingStatus" style="margin-left: 20px; color: #8A2BE2; font-weight: bold; font-size: 16px;">
                Hold to record voice message
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
            margin-top: 15px;
            padding: 15px;
            background: rgba(138, 43, 226, 0.1);
            border-radius: 10px;
            display: none;
            border-left: 4px solid #8A2BE2;
        "></div>
    </div>

    <script>
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
            document.getElementById('recordingStatus').innerHTML = '🔴 Recording... Release to send';
            document.getElementById('voiceWaveform').style.display = 'flex';
        };
       
        recognition.onresult = function(event) {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
           
            document.getElementById('transcriptionResult').innerHTML = '📝 ' + transcript;
            document.getElementById('transcriptionResult').style.display = 'block';
           
            // Auto-submit final result
            if (event.results[event.results.length - 1].isFinal && transcript.trim()) {
                // Store transcript for Streamlit to pick up
                sessionStorage.setItem('voice_input', transcript.trim());
                document.getElementById('recordingStatus').innerHTML = '✅ Message recorded! Processing...';
            }
        };
       
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            document.getElementById('recordingStatus').innerHTML = '❌ Error: ' + event.error + '. Try again.';
            resetRecording();
        };
       
        recognition.onend = function() {
            resetRecording();
        };
    }

    function startRecording() {
        if (isRecording) return;
       
        isRecording = true;
        const button = document.getElementById('voiceButton');
        button.classList.add('recording');
        document.getElementById('transcriptionResult').style.display = 'none';
       
        if (recognition) {
            try {
                recognition.start();
            } catch (error) {
                console.error('Recognition start error:', error);
                resetRecording();
            }
        } else {
            alert('Speech recognition not supported. Please use Chrome or Edge browser.');
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
        const button = document.getElementById('voiceButton');
        button.classList.remove('recording');
        document.getElementById('recordingStatus').innerHTML = 'Hold to record voice message';
        document.getElementById('voiceWaveform').style.display = 'none';
    }
    </script>
    """
   
    st.components.v1.html(voice_html, height=200)
   
    # Check for voice input
    if st.button("🔄 Check for Voice Input", key="voice_check"):
        st.info("Voice input integration ready. Hold the microphone button to record.")

# Fixed Natural Voice with MOBILE SUPPORT
def natural_voice_component(text, voice_type="professional"):
    """Single voice playback with mobile support - prevents doubles"""
    if not text or st.session_state.get('voice_played', False):
        return
   
    # Mark voice as played to prevent doubles
    st.session_state.voice_played = True
   
    # Get avatar gender for proper voice selection
    profile = st.session_state.user_profile
    avatar_choice = profile.get('avatar', 'sophia')
    avatar_configs = {
        'sophia': {'gender': 'female', 'voice_type': 'professional'},
        'marcus': {'gender': 'male', 'voice_type': 'confident'},
        'elena': {'gender': 'female', 'voice_type': 'caring'},
        'david': {'gender': 'male', 'voice_type': 'wise'},
        'maya': {'gender': 'female', 'voice_type': 'energetic'},
        'james': {'gender': 'male', 'voice_type': 'executive'}
    }
    avatar_gender = avatar_configs.get(avatar_choice, {}).get('gender', 'female')
   
    elevenlabs_key = setup_elevenlabs()
   
    if elevenlabs_key and elevenlabs_key != "your_elevenlabs_api_key_here":
        # Premium ElevenLabs voice with gender matching
        create_instant_elevenlabs_voice(text, elevenlabs_key, voice_type, avatar_gender)
    else:
        # Enhanced browser TTS with mobile support
        create_mobile_friendly_voice(text, voice_type, avatar_gender)

def create_mobile_friendly_voice(text, voice_type, gender):
    """Enhanced mobile-friendly browser TTS with GUARANTEED mobile support"""
   
    clean_text = enhance_text_for_speech(text, voice_type)
   
    # Voice personality settings
    voice_settings = {
        'professional': {'rate': 0.85, 'pitch': 1.0, 'emphasis': 'neutral'},
        'confident': {'rate': 1.1, 'pitch': 0.8, 'emphasis': 'strong'},
        'caring': {'rate': 0.75, 'pitch': 1.3, 'emphasis': 'gentle'},
        'wise': {'rate': 0.65, 'pitch': 0.7, 'emphasis': 'thoughtful'},
        'energetic': {'rate': 1.25, 'pitch': 1.4, 'emphasis': 'excited'},
        'executive': {'rate': 0.9, 'pitch': 0.85, 'emphasis': 'authoritative'}
    }
   
    settings = voice_settings.get(voice_type, voice_settings['professional'])
   
    # Strong gender adjustments
    if gender == 'male':
        settings['pitch'] = max(0.4, settings['pitch'] - 0.4)  # Much deeper for males
    else:
        settings['pitch'] = min(1.6, settings['pitch'] + 0.2)  # Higher for females
   
    # Add personality-specific pauses and emphasis
    if voice_type == 'wise':
        clean_text = clean_text.replace('.', '... ')
        clean_text = clean_text.replace(',', ', ')
    elif voice_type == 'energetic':
        clean_text = clean_text.replace('!', '! ')
        clean_text = clean_text.replace('.', '! ')
    elif voice_type == 'caring':
        clean_text = clean_text.replace('you', 'you... ')
    elif voice_type == 'confident':
        clean_text = clean_text.replace('.', '. ')
   
    # Create unique ID for this voice instance
    voice_id = f"voice_{int(time.time() * 1000)}"
   
    voice_html = f"""
    <div style="
        padding: 20px;
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        border-radius: 20px;
        border: 2px solid rgba(138, 43, 226, 0.3);
        margin: 15px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.2);
    ">
        <div id="voiceMessage_{voice_id}" style="
            margin-bottom: 15px;
            color: #8A2BE2;
            font-weight: bold;
            font-size: 16px;
        ">
            🎭 Your coach is speaking...
        </div>
       
        <div id="voiceButtonContainer_{voice_id}" style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
            <!-- Auto-play attempt button (hidden initially) -->
            <button id="autoPlayButton_{voice_id}" onclick="tryAutoPlay_{voice_id}()" style="
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 12px 20px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
                display: none;
                font-size: 14px;
            ">
                🔊 Auto-Play Voice
            </button>
           
            <!-- Manual play button for mobile -->
            <button id="manualPlayButton_{voice_id}" onclick="playVoiceManually_{voice_id}()" style="
                background: linear-gradient(135deg, #8A2BE2, #9370DB);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 12px 20px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3);
                display: block;
                font-size: 14px;
                margin: 0 5px;
            ">
                🔊 Tap to Hear Voice
            </button>
           
            <!-- Stop button -->
            <button id="stopButton_{voice_id}" onclick="stopVoice_{voice_id}()" style="
                background: linear-gradient(135deg, #f44336, #da190b);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 12px 20px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
                display: none;
                font-size: 14px;
            ">
                ⏹️ Stop
            </button>
        </div>
       
        <!-- Voice status indicator -->
        <div id="voiceStatus_{voice_id}" style="
            margin-top: 10px;
            padding: 8px 12px;
            background: rgba(138, 43, 226, 0.1);
            border-radius: 15px;
            font-size: 12px;
            color: #8A2BE2;
            font-weight: bold;
            display: none;
        "></div>
    </div>

    <script>
    let isMobileDevice_{voice_id} = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    let voiceUtterance_{voice_id} = null;
    let isPlaying_{voice_id} = false;
   
    function playVoiceMobileFriendly_{voice_id}() {{
        if ('speechSynthesis' in window) {{
            // Cancel any existing speech
            speechSynthesis.cancel();
           
            voiceUtterance_{voice_id} = new SpeechSynthesisUtterance(`{clean_text}`);
            isPlaying_{voice_id} = true;
            voiceUtterance_{voice_id}.rate = {settings['rate']};
            voiceUtterance_{voice_id}.pitch = {settings['pitch']};
            voiceUtterance_{voice_id}.volume = 1.0;
           
            // Update UI for playing state
            document.getElementById('voiceMessage_{voice_id}').innerHTML = '🎤 Your coach is now speaking...';
            document.getElementById('manualPlayButton_{voice_id}').style.display = 'none';
            document.getElementById('stopButton_{voice_id}').style.display = 'block';
            document.getElementById('voiceStatus_{voice_id}').style.display = 'block';
            document.getElementById('voiceStatus_{voice_id}').innerHTML = '🔊 Voice playing...';
           
            // Gender and personality-based voice selection
            const voices = speechSynthesis.getVoices();
            let bestVoice;
           
            if ('{gender}' === 'male') {{
                if ('{voice_type}' === 'wise') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('daniel') ||
                         v.name.toLowerCase().includes('alex') ||
                         v.name.toLowerCase().includes('male'))
                    );
                }} else if ('{voice_type}' === 'confident' || '{voice_type}' === 'executive') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('david') ||
                         v.name.toLowerCase().includes('mark') ||
                         v.name.toLowerCase().includes('male'))
                    );
                }}
               
                if (!bestVoice) {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        v.name.toLowerCase().includes('male')
                    );
                }}
            }} else {{
                if ('{voice_type}' === 'caring') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('samantha') ||
                         v.name.toLowerCase().includes('susan') ||
                         v.name.toLowerCase().includes('female'))
                    );
                }} else if ('{voice_type}' === 'energetic') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('victoria') ||
                         v.name.toLowerCase().includes('karen') ||
                         v.name.toLowerCase().includes('female'))
                    );
                }} else if ('{voice_type}' === 'professional') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('alex') ||
                         v.name.toLowerCase().includes('female'))
                    );
                }}
            }}
           
            if (!bestVoice) {{
                bestVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
            }}
           
            if (bestVoice) {{
                voiceUtterance_{voice_id}.voice = bestVoice;
                console.log('Selected voice:', bestVoice.name, 'for', '{voice_type}', '{gender}');
            }}
           
            // Voice event handlers
            voiceUtterance_{voice_id}.onstart = function() {{
                console.log('Voice started playing');
                document.getElementById('voiceStatus_{voice_id}').innerHTML = '🎵 Voice is playing...';
            }};
           
            voiceUtterance_{voice_id}.onend = function() {{
                console.log('Voice finished playing');
                isPlaying_{voice_id} = false;
                document.getElementById('voiceMessage_{voice_id}').innerHTML = '✅ Voice message completed!';
                document.getElementById('manualPlayButton_{voice_id}').style.display = 'block';
                document.getElementById('stopButton_{voice_id}').style.display = 'none';
                document.getElementById('voiceStatus_{voice_id}').innerHTML = '✅ Playback completed';
               
                // Hide after 3 seconds
                setTimeout(() => {{
                    document.getElementById('voiceStatus_{voice_id}').style.display = 'none';
                }}, 3000);
            }};
           
            voiceUtterance_{voice_id}.onerror = function(event) {{
                console.error('Voice error:', event.error);
                isPlaying_{voice_id} = false;
                document.getElementById('voiceMessage_{voice_id}').innerHTML = '❌ Voice playback failed';
                document.getElementById('manualPlayButton_{voice_id}').style.display = 'block';
                document.getElementById('stopButton_{voice_id}').style.display = 'none';
                document.getElementById('voiceStatus_{voice_id}').innerHTML = '❌ Playback error: ' + event.error;
            }};
           
            // Voice-specific adjustments
            if ('{voice_type}' === 'wise') {{
                voiceUtterance_{voice_id}.rate = voiceUtterance_{voice_id}.rate * 0.8;
            }} else if ('{voice_type}' === 'energetic') {{
                voiceUtterance_{voice_id}.rate = voiceUtterance_{voice_id}.rate * 1.2;
                voiceUtterance_{voice_id}.volume = 1.0;
            }} else if ('{voice_type}' === 'caring') {{
                voiceUtterance_{voice_id}.pitch = voiceUtterance_{voice_id}.pitch * 1.1;
            }}
           
            // Start speech
            speechSynthesis.speak(voiceUtterance_{voice_id});
            console.log('Voice started for {voice_type} {gender}');
        }} else {{
            document.getElementById('voiceMessage_{voice_id}').innerHTML = '❌ Voice not supported in this browser';
            document.getElementById('voiceStatus_{voice_id}').innerHTML = 'Please use Chrome, Safari, or Edge';
            document.getElementById('voiceStatus_{voice_id}').style.display = 'block';
        }}
    }}
   
    function playVoiceManually_{voice_id}() {{
        console.log('Manual play triggered for mobile');
        playVoiceMobileFriendly_{voice_id}();
    }}
   
    function tryAutoPlay_{voice_id}() {{
        console.log('Attempting auto-play');
        playVoiceMobileFriendly_{voice_id}();
    }}
   
    function stopVoice_{voice_id}() {{
        console.log('Stopping voice playback');
        if (speechSynthesis) {{
            speechSynthesis.cancel();
        }}
        isPlaying_{voice_id} = false;
       
        document.getElementById('voiceMessage_{voice_id}').innerHTML = '⏹️ Voice stopped';
        document.getElementById('manualPlayButton_{voice_id}').style.display = 'block';
        document.getElementById('stopButton_{voice_id}').style.display = 'none';
        document.getElementById('voiceStatus_{voice_id}').innerHTML = '⏹️ Playback stopped';
       
        setTimeout(() => {{
            document.getElementById('voiceStatus_{voice_id}').style.display = 'none';
        }}, 2000);
    }}
   
    // Enhanced mobile and desktop detection
    console.log('Device detection - Mobile:', isMobileDevice_{voice_id});
   
    // Try auto-play for desktop, show manual button for mobile
    if (isMobileDevice_{voice_id}) {{
        // Mobile: Always show manual play button
        console.log('Mobile device detected - manual play required');
        document.getElementById('voiceMessage_{voice_id}').innerHTML = '📱 Tap the button below to hear your coach!';
        document.getElementById('manualPlayButton_{voice_id}').style.display = 'block';
       
        // Try auto-play anyway (some mobile browsers allow it)
        document.getElementById('autoPlayButton_{voice_id}').style.display = 'block';
        setTimeout(() => {{
            try {{
                playVoiceMobileFriendly_{voice_id}();
                // If auto-play works, hide manual button after 2 seconds
                setTimeout(() => {{
                    if (speechSynthesis.speaking) {{
                        document.getElementById('manualPlayButton_{voice_id}').style.display = 'none';
                        document.getElementById('autoPlayButton_{voice_id}').style.display = 'none';
                    }}
                }}, 2000);
            }} catch (error) {{
                console.log('Auto-play failed on mobile, manual interaction required');
            }}
        }}, 300);
       
    }} else {{
        // Desktop: Try auto-play immediately
        console.log('Desktop device - attempting auto-play');
        document.getElementById('manualPlayButton_{voice_id}').style.display = 'none';
       
        if (speechSynthesis.getVoices().length > 0) {{
            setTimeout(playVoiceMobileFriendly_{voice_id}, 500);
        }} else {{
            speechSynthesis.onvoiceschanged = function() {{
                setTimeout(playVoiceMobileFriendly_{voice_id}, 500);
            }};
        }}
       
        // Show manual button as backup if auto-play fails
        setTimeout(() => {{
            if (!speechSynthesis.speaking && !isPlaying_{voice_id}) {{
                console.log('Auto-play failed, showing manual button');
                document.getElementById('manualPlayButton_{voice_id}').style.display = 'block';
                document.getElementById('voiceMessage_{voice_id}').innerHTML = '🖥️ Click to hear your coach (auto-play blocked)';
            }}
        }}, 2000);
    }}
   
    // Global error handling
    window.addEventListener('error', function(e) {{
        if (e.message.includes('play')) {{
            console.log('Voice play error detected, ensuring manual controls are available');
            document.getElementById('manualPlayButton_{voice_id}').style.display = 'block';
        }}
    }});
    </script>
    """
   
    st.components.v1.html(voice_html, height=180)

def create_instant_elevenlabs_voice(text, api_key, voice_type, gender):
    """Instant ElevenLabs voice with gender-matched voices"""
   
    # Voice selection based on gender and personality
    if gender == 'male':
        voice_configs = {
            'professional': {'voice_id': 'TxGEqnHWrfWFTfGW9XjX', 'name': 'Professional Male'},
            'confident': {'voice_id': 'VR6AewLTigWG4xSOukaG', 'name': 'Confident Male'},
            'caring': {'voice_id': 'IKne3meq5aSn9XLyUdCD', 'name': 'Caring Male'},
            'wise': {'voice_id': 'onwK4e9ZLuTAKqWW03F9', 'name': 'Wise Male'},
            'energetic': {'voice_id': 'pNInz6obpgDQGcFmaJgB', 'name': 'Energetic Male'},
            'executive': {'voice_id': 'Yko7PKHZNXotIFUBG7I9', 'name': 'Executive Male'}
        }
    else:  # female
        voice_configs = {
            'professional': {'voice_id': 'EXAVITQu4vr4xnSDxMaL', 'name': 'Professional Female'},
            'confident': {'voice_id': 'ThT5KcBeYPX3keUQqHPh', 'name': 'Confident Female'},
            'caring': {'voice_id': '21m00Tcm4TlvDq8ikWAM', 'name': 'Caring Female'},
            'wise': {'voice_id': 'XrExE9yKIg1WjnnlVkGX', 'name': 'Wise Female'},
            'energetic': {'voice_id': 'AZnzlk1XvdvUeBnXmlld', 'name': 'Energetic Female'},
            'executive': {'voice_id': 'SOYHLrjzK2X1ezoPC6cr', 'name': 'Executive Female'}
        }
   
    voice_config = voice_configs.get(voice_type, voice_configs['professional'])
    voice_id = voice_config['voice_id']
   
    # Clean text for speech
    clean_text = enhance_text_for_speech(text, voice_type)
   
    # Instant voice generation and playback
    voice_html = f"""
    <script>
    // Prevent multiple simultaneous voices
    if (window.speechSynthesis) {{
        window.speechSynthesis.cancel();
    }}
   
    async function playInstantVoice() {{
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
                        stability: {0.9 if voice_type == 'wise' else 0.7 if voice_type == 'professional' else 0.5},
                        similarity_boost: {0.9 if voice_type == 'professional' else 0.8 if voice_type == 'wise' else 0.6},
                        style: {0.2 if voice_type == 'caring' else 0.6 if voice_type == 'energetic' else 0.5},
                        use_speaker_boost: {str(voice_type in ['confident', 'executive', 'energetic']).lower()},
                        speed: {0.8 if voice_type == 'wise' else 1.0 if voice_type == 'energetic' else 1.0}
                    }}
                }})
            }});
           
            if (response.ok) {{
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
               
                // Enhanced mobile-friendly audio playback
                audio.play().then(() => {{
                    console.log('ElevenLabs audio playing successfully');
                }}).catch(e => {{
                    console.log('ElevenLabs autoplay blocked on mobile, using browser TTS fallback');
                    fallbackToBrowserTTS();
                }});
               
            }} else {{
                console.log('ElevenLabs failed, using browser TTS');
                fallbackToBrowserTTS();
            }}
        }} catch (error) {{
            console.log('Voice error, using browser TTS');
            fallbackToBrowserTTS();
        }}
    }}
   
    function fallbackToBrowserTTS() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel(); // Stop any existing speech
           
            const utterance = new SpeechSynthesisUtterance(`{clean_text}`);
           
            // Personality-specific settings for fallback
            if ('{voice_type}' === 'wise') {{
                utterance.rate = 0.6;
                utterance.pitch = {0.5 if gender == 'male' else 0.8};
            }} else if ('{voice_type}' === 'energetic') {{
                utterance.rate = 1.1;
                utterance.pitch = {0.7 if gender == 'male' else 1.5};
            }} else if ('{voice_type}' === 'caring') {{
                utterance.rate = 0.75;
                utterance.pitch = {0.6 if gender == 'male' else 1.3};
            }} else if ('{voice_type}' === 'confident') {{
                utterance.rate = 1.0;
                utterance.pitch = {0.4 if gender == 'male' else 0.9};
            }} else if ('{voice_type}' === 'professional') {{
                utterance.rate = 0.85;
                utterance.pitch = {0.6 if gender == 'male' else 1.0};
            }} else {{
                utterance.rate = 0.9;
                utterance.pitch = {0.6 if gender == 'male' else 1.0};
            }}
           
            utterance.volume = 1.0;
           
            // Gender-based voice selection for fallback
            const voices = speechSynthesis.getVoices();
            let bestVoice;
           
            if ('{gender}' === 'male') {{
                bestVoice = voices.find(v =>
                    v.lang.startsWith('en-') &&
                    (v.name.toLowerCase().includes('male') ||
                     v.name.toLowerCase().includes('david') ||
                     v.name.toLowerCase().includes('mark'))
                );
            }} else {{
                bestVoice = voices.find(v =>
                    v.lang.startsWith('en-') &&
                    (v.name.toLowerCase().includes('female') ||
                     v.name.toLowerCase().includes('samantha'))
                );
            }}
           
            if (!bestVoice) {{
                bestVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
            }}
           
            if (bestVoice) utterance.voice = bestVoice;
           
            speechSynthesis.speak(utterance);
        }}
    }}
   
    // Start playing immediately
    playInstantVoice();
    </script>
    """
   
    st.components.v1.html(voice_html, height=0)

def create_instant_browser_voice(text, voice_type, gender):
    """Instant browser TTS with DISTINCT gender and personality matching"""
   
    clean_text = enhance_text_for_speech(text, voice_type)
   
    # MUCH MORE DISTINCT voice personality settings
    voice_settings = {
        'professional': {'rate': 0.85, 'pitch': 1.0, 'emphasis': 'neutral'},
        'confident': {'rate': 1.1, 'pitch': 0.8, 'emphasis': 'strong'},
        'caring': {'rate': 0.75, 'pitch': 1.3, 'emphasis': 'gentle'},
        'wise': {'rate': 0.65, 'pitch': 0.7, 'emphasis': 'thoughtful'},
        'energetic': {'rate': 1.15, 'pitch': 1.4, 'emphasis': 'excited'},
        'executive': {'rate': 0.9, 'pitch': 0.85, 'emphasis': 'authoritative'}
    }
   
    settings = voice_settings.get(voice_type, voice_settings['professional'])
   
    # Strong gender adjustments
    if gender == 'male':
        settings['pitch'] = max(0.4, settings['pitch'] - 0.4)  # Much deeper for males
    else:
        settings['pitch'] = min(1.6, settings['pitch'] + 0.2)  # Higher for females
   
    # Add personality-specific pauses and emphasis
    if voice_type == 'wise':
        clean_text = clean_text.replace('.', '... ')  # Thoughtful pauses
        clean_text = clean_text.replace(',', ', ')    # More deliberate
    elif voice_type == 'energetic':
        clean_text = clean_text.replace('!', '! ')    # Excitement bursts
        clean_text = clean_text.replace('.', '! ')    # Turn periods to exclamation
    elif voice_type == 'caring':
        clean_text = clean_text.replace('you', 'you... ')  # Gentle emphasis
    elif voice_type == 'confident':
        clean_text = clean_text.replace('.', '. ')    # Firm statements
   
    voice_html = f"""
    <script>
    function playInstantBrowserVoice() {{
        if ('speechSynthesis' in window) {{
            speechSynthesis.cancel(); // Clear any previous speech
           
            const utterance = new SpeechSynthesisUtterance(`{clean_text}`);
            utterance.rate = {settings['rate']};
            utterance.pitch = {settings['pitch']};
            utterance.volume = 1.0;
           
            // Personality-specific voice selection
            const voices = speechSynthesis.getVoices();
            let bestVoice;
           
            if ('{gender}' === 'male') {{
                // Male voice selection with personality matching
                if ('{voice_type}' === 'wise') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('daniel') ||
                         v.name.toLowerCase().includes('alex') ||
                         v.name.toLowerCase().includes('male'))
                    );
                }} else if ('{voice_type}' === 'confident' || '{voice_type}' === 'executive') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('david') ||
                         v.name.toLowerCase().includes('mark') ||
                         v.name.toLowerCase().includes('male'))
                    );
                }}
               
                // Fallback to any male voice
                if (!bestVoice) {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        v.name.toLowerCase().includes('male')
                    );
                }}
            }} else {{
                // Female voice selection with personality matching  
                if ('{voice_type}' === 'caring') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('samantha') ||
                         v.name.toLowerCase().includes('susan') ||
                         v.name.toLowerCase().includes('female'))
                    );
                }} else if ('{voice_type}' === 'energetic') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('victoria') ||
                         v.name.toLowerCase().includes('karen') ||
                         v.name.toLowerCase().includes('female'))
                    );
                }} else if ('{voice_type}' === 'professional') {{
                    bestVoice = voices.find(v =>
                        v.lang.startsWith('en-') &&
                        (v.name.toLowerCase().includes('alex') ||
                         v.name.toLowerCase().includes('female'))
                    );
                }}
            }}
           
            // Fallback to any English voice
            if (!bestVoice) {{
                bestVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
            }}
           
            if (bestVoice) {{
                utterance.voice = bestVoice;
                console.log('Selected voice:', bestVoice.name, 'for', '{voice_type}', '{gender}');
            }}
           
            // Personality-specific speech adjustments
            if ('{voice_type}' === 'wise') {{
                utterance.rate = utterance.rate * 0.8;  // Even slower for wisdom
            }} else if ('{voice_type}' === 'energetic') {{
                utterance.rate = utterance.rate * 1.2;  // Even faster for energy
                utterance.volume = 1.0;  // Full volume for excitement
            }} else if ('{voice_type}' === 'caring') {{
                utterance.pitch = utterance.pitch * 1.1;  // Softer, higher for caring
            }}
           
            // Play immediately
            speechSynthesis.speak(utterance);
        }}
    }}
   
    // Handle voice loading
    if (speechSynthesis.getVoices().length > 0) {{
        playInstantBrowserVoice();
    }} else {{
        speechSynthesis.onvoiceschanged = playInstantBrowserVoice;
    }}
    </script>
    """
   
    st.components.v1.html(voice_html, height=0)

def enhance_text_for_speech(text, voice_type):
    """Make text MUCH more distinct for each personality type"""
   
    # Remove markdown and clean
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = text.replace('\n', ' ').strip()
   
    # DRAMATIC personality-based enhancements
    if voice_type == 'caring':
        # Gentle, nurturing speech patterns
        text = re.sub(r'\byou\b', 'you, dear', text, flags=re.IGNORECASE, count=1)
        text = re.sub(r'\.', '. Take your time with this.', text, count=1)
        text = re.sub(r'!', '. This is wonderful!', text)
        text = text.replace(' can ', ' absolutely can ')
        text = text.replace(' will ', ' will surely ')
       
    elif voice_type == 'energetic':
        # Excited, fast, motivational speech
        text = re.sub(r'\bgreat\b', 'absolutely AMAZING', text, flags=re.IGNORECASE)
        text = re.sub(r'\bgood\b', 'fantastic', text, flags=re.IGNORECASE)
        text = re.sub(r'\.', '! Let\'s do this!', text, count=1)
        text = re.sub(r'\byes\b', 'YES! Absolutely!', text, flags=re.IGNORECASE)
        text = text.replace(' can ', ' can totally ')
        text = text.replace(' will ', ' will definitely ')
        text += ' I\'m SO excited for you!'
       
    elif voice_type == 'wise':
        # Slow, thoughtful, philosophical speech
        text = re.sub(r'\bremember\b', 'always keep in mind', text, flags=re.IGNORECASE)
        text = re.sub(r'\.', '... Consider this carefully.', text, count=1)
        text = re.sub(r'\bthink\b', 'reflect deeply', text, flags=re.IGNORECASE)
        text = 'Hmm... ' + text
        text = text.replace(' is ', ' truly is ')
        text = text.replace(' can ', ' may indeed ')
       
    elif voice_type == 'professional':
        # Clear, direct, business-like speech
        text = re.sub(r'\.', '. Let me be clear on this point.', text, count=1)
        text = re.sub(r'\bI think\b', 'Based on my analysis', text, flags=re.IGNORECASE)
        text = text.replace(' should ', ' must strategically ')
        text = text.replace(' can ', ' should systematically ')
       
    elif voice_type == 'confident':
        # Strong, assertive, powerful speech
        text = re.sub(r'\.', '. I\'m absolutely certain of this.', text, count=1)
        text = re.sub(r'\bI believe\b', 'I KNOW', text, flags=re.IGNORECASE)
        text = text.replace(' might ', ' WILL ')
        text = text.replace(' could ', ' WILL ')
        text = 'Listen up! ' + text
       
    elif voice_type == 'executive':
        # Authoritative, commanding, leadership speech
        text = re.sub(r'\.', '. This is exactly what successful leaders do.', text, count=1)
        text = re.sub(r'\bwe should\b', 'we MUST execute', text, flags=re.IGNORECASE)
        text = text.replace(' need to ', ' must immediately ')
        text = 'Here\'s the strategic approach: ' + text
   
    # Add natural speech patterns with MORE dramatic pauses
    text = re.sub(r'([.!?])', r'\1 ', text)
    text = re.sub(r'([,:])', r'\1 ', text)
   
    # Escape for JavaScript
    text = text.replace('"', '\\"').replace("'", "\\'")
    text = re.sub(r'\s+', ' ', text)
   
    return text.strip()

# Load coaching knowledge base
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

# Generate coach response
def get_coach_response(user_input, chat_history):
    try:
        model, model_name = setup_gemini()
       
        # Get user profile
        profile = st.session_state.user_profile
        name = profile.get('name', 'there')
        voice_type = profile.get('voice_type', 'caring')
        goals = profile.get('goals', 'general success')
       
        # Build conversational context
        context = f"""You are a {voice_type} success coach speaking to {name}.
        Their goals: {goals}
       
        Recent conversation:"""
       
        # Add recent messages
        for msg in chat_history[-3:]:
            role = "Coach" if msg['role'] == 'coach' else name
            context += f"\n{role}: {msg['content']}"
       
        context += f"\n{name}: {user_input}"
       
        # Natural coaching prompt
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

# Voice Input Processing Functions
def check_for_pending_voice_message():
    """Check for voice messages in URL parameters (legacy)"""
    if 'voice_msg' in st.query_params:
        voice_message = st.query_params['voice_msg']
        del st.query_params['voice_msg']
        return voice_message
    return None

def process_voice_message(voice_input):
    """Process voice message automatically"""
    if not voice_input or not voice_input.strip():
        return
   
    st.session_state.voice_played = False
   
    st.session_state.chat_history.append({
        'role': 'user',
        'content': voice_input,
        'timestamp': datetime.now()
    })
   
    with st.spinner("Your coach is responding to your voice message..."):
        coach_response = get_coach_response(voice_input, st.session_state.chat_history)
   
    st.session_state.chat_history.append({
        'role': 'coach',
        'content': coach_response,
        'timestamp': datetime.now()
    })
   
    st.session_state.is_speaking = True
    st.rerun()

# Chat interface
def chat_interface():
    st.markdown("### 💬 Conversation")
   
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
       
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="coach-message">{message["content"]}</div>', unsafe_allow_html=True)
       
        st.markdown('</div>', unsafe_allow_html=True)

# Enhanced user profile sidebar
def user_profile_sidebar():
    with st.sidebar:
        st.header("👤 Your Coach Settings")
       
        # Basic info
        name = st.text_input("Your Name", value=st.session_state.user_profile.get('name', ''))
        goals = st.text_area("Your Goals", value=st.session_state.user_profile.get('goals', ''))
       
        # Enhanced avatar choices
        st.subheader("🎭 Choose Your AI Coach")
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
        st.subheader("🎤 Voice Style")
        voice_type = st.selectbox(
            "Coach Personality",
            ["caring", "professional", "energetic", "wise"],
            index=["caring", "professional", "energetic", "wise"].index(
                st.session_state.user_profile.get('voice_type', 'caring')
            ),
            format_func=lambda x: {
                'caring': '💝 Caring & Supportive',
                'professional': '💼 Professional & Direct',
                'energetic': '⚡ Energetic & Motivating',
                'wise': '🧙‍♂️ Wise & Thoughtful'
            }[x]
        )
       
        # Save profile
        if st.button("💾 Save Settings", type="primary"):
            st.session_state.user_profile = {
                'name': name,
                'goals': goals,
                'avatar': avatar_choice,
                'voice_type': voice_type,
                'voice_speed': 0.9,
                'voice_pitch': 1.0
            }
            st.success("✅ Settings saved!")
            st.rerun()

# Main app
def main():
    load_css()
    init_session_state()
   
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
        <h1>🎯 Avatar Success Coach</h1>
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
        # Fixed avatar display
        avatar_component(st.session_state.is_speaking)
       
        # ONLY play voice for NEW coach messages
        if (st.session_state.chat_history and
            st.session_state.chat_history[-1]['role'] == 'coach' and
            st.session_state.is_speaking and
            not st.session_state.voice_played):
           
            latest_response = st.session_state.chat_history[-1]['content']
            voice_type = st.session_state.user_profile.get('voice_type', 'professional')
            natural_voice_component(latest_response, voice_type)
       
        # Reset speaking state after voice plays
        if st.session_state.is_speaking:
            st.session_state.is_speaking = False
   
    with col2:
        # Chat interface
        chat_interface()
       
        # Regular text input form with voice section below
        st.markdown("### ✍️ Send Message")
       
        with st.form("message_form", clear_on_submit=True):
            user_input = st.text_area(
                "Type your message:",
                height=80,
                placeholder="Ask about your goals, challenges, or anything related to success...",
                key="user_text_input"
            )
           
            submitted = st.form_submit_button("Send", type="primary")
           
            if submitted and user_input.strip():
                # Reset voice flag for new conversation
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
               
                st.session_state.is_speaking = True
                st.rerun()
       
        # Check and process voice message using session state
        if 'pending_voice_input' in st.session_state and st.session_state.pending_voice_input:
            voice_input = st.session_state.pending_voice_input
            st.session_state.pending_voice_input = None  # Clear it
           
            # Process voice message
            st.session_state.voice_played = False
           
            st.session_state.chat_history.append({
                'role': 'user',
                'content': voice_input,
                'timestamp': datetime.now()
            })
           
            with st.spinner("Your coach is responding to your voice message..."):
                coach_response = get_coach_response(voice_input, st.session_state.chat_history)
           
            st.session_state.chat_history.append({
                'role': 'coach',
                'content': coach_response,
                'timestamp': datetime.now()
            })
           
            st.session_state.is_speaking = True
            st.rerun()
       
        # Voice recording section BELOW the form with button on right
        st.markdown("---")
        st.markdown("### 🎤 Voice Message")
       
        voice_section_html = f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
            border-radius: 20px;
            border: 2px solid rgba(138, 43, 226, 0.2);
            margin: 10px 0;
        ">
            <!-- Voice Status Area (LEFT) -->
            <div id="voiceStatusArea" style="
                flex-grow: 1;
                padding: 10px 15px;
                background: white;
                border-radius: 15px;
                border: 1px solid #ddd;
                min-height: 50px;
                display: flex;
                align-items: center;
            ">
                <div id="voiceStatus" style="
                    color: #8A2BE2;
                    font-weight: bold;
                    font-size: 14px;
                ">
                    🎤 Tap once to record, tap again to stop and send message
                </div>
            </div>
           
            <!-- Voice Button (RIGHT SIDE) - CLICK ONLY -->
            <button id="tapVoiceButton"
                    onclick="handleVoiceTap()"
                    style="
                        background: linear-gradient(135deg, #8A2BE2, #9370DB);
                        border: none;
                        border-radius: 50%;
                        width: 70px;
                        height: 70px;
                        color: white;
                        font-size: 28px;
                        cursor: pointer;
                        box-shadow: 0 4px 20px rgba(138, 43, 226, 0.4);
                        transition: all 0.3s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        user-select: none;
                        -webkit-user-select: none;
                        flex-shrink: 0;
                    "
                    onmouseover="this.style.transform='scale(1.05)'"
                    onmouseout="this.style.transform='scale(1)'">
                🎤
            </button>
        </div>
       
        <!-- Voice Waveform Animation -->
        <div id="voiceWaveform" style="
            display: none;
            justify-content: center;
            align-items: center;
            gap: 4px;
            margin: 15px 0;
            padding: 20px;
            background: rgba(138, 43, 226, 0.1);
            border-radius: 15px;
        ">
            <div class="wave-bar" style="width: 5px; height: 25px; background: linear-gradient(135deg, #8A2BE2, #9370DB); border-radius: 3px; animation: wave 1.2s ease-in-out infinite;"></div>
            <div class="wave-bar" style="width: 5px; height: 25px; background: linear-gradient(135deg, #8A2BE2, #9370DB); border-radius: 3px; animation: wave 1.2s ease-in-out infinite; animation-delay: 0.1s;"></div>
            <div class="wave-bar" style="width: 5px; height: 25px; background: linear-gradient(135deg, #8A2BE2, #9370DB); border-radius: 3px; animation: wave 1.2s ease-in-out infinite; animation-delay: 0.2s;"></div>
            <div class="wave-bar" style="width: 5px; height: 25px; background: linear-gradient(135deg, #8A2BE2, #9370DB); border-radius: 3px; animation: wave 1.2s ease-in-out infinite; animation-delay: 0.3s;"></div>
            <div class="wave-bar" style="width: 5px; height: 25px; background: linear-gradient(135deg, #8A2BE2, #9370DB); border-radius: 3px; animation: wave 1.2s ease-in-out infinite; animation-delay: 0.4s;"></div>
        </div>

        <script>
        // TAP-TO-RECORD VOICE SYSTEM - NO HOLDING REQUIRED
        let tapRecognition;
        let tapRecordingActive = false;
        let tapVoiceTranscript = '';
        let tapButtonState = 'ready'; // 'ready', 'recording', 'processing'
       
        console.log('🎤 TAP-TO-RECORD Voice System Loading...');
       
        // CSS Animations for tap system
        const tapStyle = document.createElement('style');
        tapStyle.textContent = `
            @keyframes wave {{
                0%, 100% {{ height: 25px; }}
                50% {{ height: 45px; }}
            }}
            .tap-recording {{
                background: linear-gradient(135deg, #ff4757, #ff3742) !important;
                animation: tap-pulse-record 1s ease-in-out infinite !important;
                transform: scale(1.1) !important;
            }}
            .tap-processing {{
                background: linear-gradient(135deg, #4CAF50, #45a049) !important;
                animation: tap-pulse-process 1s ease-in-out infinite !important;
                transform: scale(1.05) !important;
            }}
            @keyframes tap-pulse-record {{
                0% {{ box-shadow: 0 4px 20px rgba(255, 71, 87, 0.4); }}
                50% {{ box-shadow: 0 6px 30px rgba(255, 71, 87, 0.8); }}
                100% {{ box-shadow: 0 4px 20px rgba(255, 71, 87, 0.4); }}
            }}
            @keyframes tap-pulse-process {{
                0% {{ box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4); }}
                50% {{ box-shadow: 0 6px 30px rgba(76, 175, 80, 0.8); }}
                100% {{ box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4); }}
            }}
        `;
        document.head.appendChild(tapStyle);
       
        // TAP-TO-RECORD Speech Recognition Setup
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            tapRecognition = new SpeechRecognition();
           
            // Optimized settings for tap recording
            tapRecognition.continuous = false;         // Single recognition session
            tapRecognition.interimResults = true;      // Show real-time results
            tapRecognition.maxAlternatives = 1;        // Best result only
            tapRecognition.lang = 'en-US';
           
            // When recognition starts
            tapRecognition.onstart = function() {{
                console.log('✅ TAP Recording started');
                document.getElementById('voiceStatus').innerHTML = '🔴 Recording now... Tap STOP when finished speaking';
                document.getElementById('voiceWaveform').style.display = 'flex';
                tapVoiceTranscript = '';
            }};
           
            // Process speech results
            tapRecognition.onresult = function(event) {{
                let currentTranscript = '';
               
                for (let i = event.resultIndex; i < event.results.length; i++) {{
                    if (event.results[i].isFinal) {{
                        tapVoiceTranscript += event.results[i][0].transcript + ' ';
                    }} else {{
                        currentTranscript += event.results[i][0].transcript;
                    }}
                }}
               
                const displayText = (tapVoiceTranscript + currentTranscript).trim();
                if (displayText) {{
                    document.getElementById('voiceStatus').innerHTML = '📝 Heard: "' + displayText + '"';
                }}
            }};
           
            // When recognition ends (user tapped stop or timeout)
            tapRecognition.onend = function() {{
                console.log('🛑 TAP Recording ended. Transcript:', tapVoiceTranscript.trim());
               
                if (tapVoiceTranscript.trim()) {{
                    // Auto-send the message
                    autoSendVoiceMessage(tapVoiceTranscript.trim());
                }} else {{
                    document.getElementById('voiceStatus').innerHTML = '❌ No speech detected. Try again.';
                    tapResetButton();
                }}
            }};
           
            // Handle errors
            tapRecognition.onerror = function(event) {{
                console.error('TAP Recognition error:', event.error);
                let errorMsg = '❌ Error: ';
               
                switch(event.error) {{
                    case 'no-speech':
                        errorMsg += 'No speech detected. Speak louder!';
                        break;
                    case 'audio-capture':
                        errorMsg += 'Microphone not available.';
                        break;
                    case 'not-allowed':
                        errorMsg += 'Microphone access denied.';
                        break;
                    default:
                        errorMsg += event.error;
                }}
               
                document.getElementById('voiceStatus').innerHTML = errorMsg;
                setTimeout(tapResetButton, 3000);
            }};
           
        }} else {{
            document.getElementById('voiceStatus').innerHTML = '❌ Voice recording not supported. Use Chrome/Edge browser.';
        }}

        // Main tap handler function - NO HOLDING
        function handleVoiceTap() {{
            console.log('🖱️ Voice button tapped. Current state:', tapButtonState);
           
            if (tapButtonState === 'ready') {{
                // First tap: Start recording
                tapStartRecording();
            }} else if (tapButtonState === 'recording') {{
                // Second tap: Stop recording
                tapStopRecording();
            }} else if (tapButtonState === 'processing') {{
                console.log('⏳ Already processing, ignoring tap');
                return;
            }}
        }}

        // Start recording function
        function tapStartRecording() {{
            console.log('▶️ TAP: Starting voice recording');
           
            tapButtonState = 'recording';
            tapRecordingActive = true;
           
            const button = document.getElementById('tapVoiceButton');
            button.classList.add('tap-recording');
            button.innerHTML = '⏹️'; // Change to STOP icon
           
            document.getElementById('voiceStatus').innerHTML = '🔴 Recording... Tap the STOP button when done speaking';
            document.getElementById('voiceWaveform').style.display = 'flex';
           
            if (tapRecognition) {{
                try {{
                    tapVoiceTranscript = '';
                    tapRecognition.start();
                }} catch (error) {{
                    console.error('Failed to start TAP recording:', error);
                    document.getElementById('voiceStatus').innerHTML = '❌ Failed to start recording';
                    tapResetButton();
                }}
            }}
        }}

        // Stop recording function  
        function tapStopRecording() {{
            console.log('⏹️ TAP: Stopping voice recording');
           
            tapButtonState = 'processing';
            tapRecordingActive = false;
           
            const button = document.getElementById('tapVoiceButton');
            button.classList.remove('tap-recording');
            button.classList.add('tap-processing');
            button.innerHTML = '⏳'; // Change to processing icon
           
            document.getElementById('voiceStatus').innerHTML = '⏳ Processing and sending your message...';
           
            if (tapRecognition) {{
                tapRecognition.stop(); // This will trigger onend
            }}
        }}

        // DIRECT Voice-to-Conversation Integration
        function autoSendVoiceMessage(message) {{
            console.log('🚀 DIRECT: Sending voice message to conversation:', message);
           
            document.getElementById('voiceStatus').innerHTML = '🚀 Sending to conversation: "' + message + '"';
           
            // DIRECT METHOD: Use URL parameters to send message directly to Streamlit
            // This bypasses the form and goes straight to the conversation
            const currentUrl = new URL(window.location.href);
           
            // Clear any existing parameters
            currentUrl.searchParams.delete('auto_voice_message');
            currentUrl.searchParams.delete('voice_timestamp');
           
            // Add voice message parameters for direct processing
            currentUrl.searchParams.set('voice_direct_send', encodeURIComponent(message.trim()));
            currentUrl.searchParams.set('voice_send_timestamp', Date.now().toString());
           
            console.log('🔄 DIRECT: Redirecting to send voice message directly to conversation');
            console.log('📝 Message:', message.trim());
           
            // Immediate redirect to process the voice message
            window.location.href = currentUrl.toString();
        }}

        // URL fallback method
        function tapUrlFallback(message) {{
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('auto_voice_message', encodeURIComponent(message));
            currentUrl.searchParams.set('voice_timestamp', Date.now().toString());
            console.log('🔄 Redirecting with voice message');
            window.location.href = currentUrl.toString();
        }}

        // Reset button to ready state
        function tapResetButton() {{
            console.log('🔄 Resetting tap button to ready state');
           
            tapButtonState = 'ready';
            tapRecordingActive = false;
            tapVoiceTranscript = '';
           
            const button = document.getElementById('tapVoiceButton');
            button.classList.remove('tap-recording', 'tap-processing');
            button.innerHTML = '🎤'; // Reset to microphone
           
            document.getElementById('voiceStatus').innerHTML = '🎤 Tap once to record, tap again to stop and send message';
            document.getElementById('voiceWaveform').style.display = 'none';
        }}
       
        console.log('✅ TAP-TO-RECORD Voice System Ready!');
        </script>
        """
       
        st.components.v1.html(voice_section_html, height=200)
       
        # DIRECT VOICE-TO-CONVERSATION PROCESSING
        voice_processed = False
       
        # Check for DIRECT voice message (new method)
        if 'voice_direct_send' in st.query_params and 'voice_send_timestamp' in st.query_params:
            voice_message = st.query_params['voice_direct_send']
            voice_timestamp = st.query_params['voice_send_timestamp']
           
            # Clear the parameters immediately
            del st.query_params['voice_direct_send']
            del st.query_params['voice_send_timestamp']
            voice_processed = True
           
            st.info(f"🎤 Voice Message Received: \"{voice_message}\"")
       
        # Check for auto voice message (fallback method)
        elif 'auto_voice_message' in st.query_params and 'voice_timestamp' in st.query_params:
            voice_message = st.query_params['auto_voice_message']
            voice_timestamp = st.query_params['voice_timestamp']
           
            # Clear the parameters immediately
            del st.query_params['auto_voice_message']
            del st.query_params['voice_timestamp']
            voice_processed = True
       
        # Fallback to old method
        elif 'voice_message' in st.query_params and 'voice_timestamp' in st.query_params:
            voice_message = st.query_params['voice_message']
            voice_timestamp = st.query_params['voice_timestamp']
           
            # Clear the parameters immediately
            del st.query_params['voice_message']
            del st.query_params['voice_timestamp']
            voice_processed = True
       
        if voice_processed:
           
            if voice_message.strip():
                # DIRECT processing - add straight to conversation
                st.success(f"🎤 Voice Message: \"{voice_message}\"")
                st.info("✨ Sending to conversation...")
               
                # Reset voice flag for new conversation
                st.session_state.voice_played = False
               
                # Add user voice message to conversation history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': voice_message.strip(),
                    'timestamp': datetime.now()
                })
               
                # Get coach response immediately
                with st.spinner("🤖 Your coach is responding to your voice message..."):
                    coach_response = get_coach_response(voice_message.strip(), st.session_state.chat_history)
               
                # Add coach response to conversation
                st.session_state.chat_history.append({
                    'role': 'coach',
                    'content': coach_response,
                    'timestamp': datetime.now()
                })
               
                # Enable voice response from coach
                st.session_state.is_speaking = True
               
                # Show success message
                st.balloons()  # Fun animation to show success
               
                # Force immediate refresh to show the updated conversation
                time.sleep(0.5)  # Brief pause to show the success message
                st.rerun()
       
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.is_speaking = False
            st.session_state.voice_played = False
            st.rerun()
       
        # Debug section
        st.markdown("---")
        st.markdown("### 🔧 Debug & API Tests")
       
        with st.expander("Debug Tools", expanded=False):
            col_debug1, col_debug2 = st.columns(2)
           
            with col_debug1:
                st.subheader("🎤 Voice Test")
                if st.button("🔊 Test Voice System"):
                    st.session_state.voice_played = False  # Reset for test
                    avatar_choice = st.session_state.user_profile.get('avatar', 'sophia')
                    voice_type = st.session_state.user_profile.get('voice_type', 'caring')
                   
                    st.write(f"Testing {voice_type} voice for: {avatar_choice}")
                   
                    # Get avatar gender for test
                    avatar_configs = {
                        'sophia': {'gender': 'female'},
                        'marcus': {'gender': 'male'},
                        'elena': {'gender': 'female'},
                        'david': {'gender': 'male'},
                        'maya': {'gender': 'female'},
                        'james': {'gender': 'male'}
                    }
                    test_gender = avatar_configs.get(avatar_choice, {}).get('gender', 'female')
                   
                    # Personality-specific test messages
                    test_messages = {
                        'caring': "I really care about your success. You can absolutely achieve your goals, dear.",
                        'professional': "Based on my analysis, you should strategically focus on your objectives.",
                        'energetic': "This is absolutely AMAZING! I'm SO excited for your success! Let's do this!",
                        'wise': "Hmm... Always keep in mind that true success comes from within. Consider this carefully.",
                        'confident': "Listen up! I KNOW you will achieve greatness. I'm absolutely certain of this.",
                        'executive': "Here's the strategic approach: we MUST execute your plan immediately."
                    }
                   
                    test_text = test_messages.get(voice_type, "Hello, this is a voice test.")
                   
                    # Test with actual personality
                    elevenlabs_key = setup_elevenlabs()
                    if elevenlabs_key and elevenlabs_key != "your_elevenlabs_api_key_here":
                        create_instant_elevenlabs_voice(test_text, elevenlabs_key, voice_type, test_gender)
                    else:
                        create_mobile_friendly_voice(test_text, voice_type, test_gender)
               
                st.subheader("🎤 Voice Input Test")
                if st.button("🔊 Test Voice Recording"):
                    st.info("Use the voice button next to the text input above to test voice recording!")
                    st.markdown("**Instructions:**")
                    st.markdown("1. Hold the 🎤 button next to the text input")
                    st.markdown("2. Speak your message clearly")
                    st.markdown("3. Release the button to auto-send")
               
                # Test ALL personalities button
                if st.button("🎭 Test All Personalities"):
                    st.session_state.voice_played = False
                    st.write("Testing all voice personalities...")
                   
                    personalities = ['caring', 'professional', 'energetic', 'wise', 'confident', 'executive']
                    test_messages = {
                        'caring': "💝 Caring: I really care about you, dear.",
                        'professional': "💼 Professional: Based on analysis, focus strategically.",
                        'energetic': "⚡ Energetic: This is AMAZING! Let's do this!",
                        'wise': "🧙‍♂️ Wise: Hmm... Consider this carefully.",
                        'confident': "💪 Confident: Listen up! I KNOW you'll succeed!",
                        'executive': "👔 Executive: Here's the strategic approach."
                    }
                   
                    for i, personality in enumerate(personalities):
                        st.write(f"{i+1}. {test_messages[personality]}")
                       
                        # Brief pause between personalities  
                        if i < len(personalities) - 1:
                            st.write("---")
               
                st.subheader("🎭 Avatar Animation Test")
                if st.button("🎬 Test Avatar Animation"):
                    st.info("Testing avatar animation - check the avatar above!")
                    st.session_state.is_speaking = True
                    st.rerun()
           
            with col_debug2:
                st.subheader("🔧 System Status")
                st.write("**API Connections:**")
                st.write(f"✅ Gemini AI: {bool(st.secrets.get('GEMINI_API_KEY'))}")
                st.write(f"✅ ElevenLabs: {bool(setup_elevenlabs())}")
                st.write(f"✅ HeyGen: {bool(setup_heygen())}")
               
                st.write("**Current Settings:**")
                st.write(f"Avatar: {st.session_state.user_profile.get('avatar', 'sophia')}")
                st.write(f"Voice Type: {st.session_state.user_profile.get('voice_type', 'caring')}")
                st.write(f"Chat Messages: {len(st.session_state.chat_history)}")
                st.write(f"Voice Played: {st.session_state.voice_played}")
                st.write(f"Is Speaking: {st.session_state.is_speaking}")

if __name__ == "__main__":
    main()

