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

# FIXED Natural Voice with MOBILE SUPPORT and DISTINCT VOICES
def natural_voice_component(text, voice_type="professional"):
    """Enhanced voice playback with distinct personalities and mobile support"""
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
        create_enhanced_elevenlabs_voice(text, elevenlabs_key, voice_type, avatar_gender)
    else:
        # Enhanced browser TTS with DISTINCT personalities
        create_enhanced_mobile_voice(text, voice_type, avatar_gender)

def create_enhanced_mobile_voice(text, voice_type, gender):
    """ENHANCED mobile-friendly browser TTS with DISTINCT voices and personalities"""
   
    clean_text = enhance_text_for_speech(text, voice_type)
   
    # FIXED Voice personality settings with better speed control
    voice_settings = {
        'professional': {'rate': 0.9, 'pitch': 1.0, 'emphasis': 'neutral'},
        'confident': {'rate': 1.0, 'pitch': 0.8, 'emphasis': 'strong'},
        'caring': {'rate': 0.8, 'pitch': 1.2, 'emphasis': 'gentle'},
        'wise': {'rate': 0.7, 'pitch': 0.8, 'emphasis': 'thoughtful'},
        'energetic': {'rate': 1.1, 'pitch': 1.3, 'emphasis': 'excited'},  # FIXED: Slower but still energetic
        'executive': {'rate': 0.95, 'pitch': 0.9, 'emphasis': 'authoritative'}
    }
   
    settings = voice_settings.get(voice_type, voice_settings['professional'])
   
    # ENHANCED gender adjustments for MORE distinct voices
    if gender == 'male':
        settings['pitch'] = max(0.3, settings['pitch'] - 0.5)  # Much deeper for males
        settings['rate'] = settings['rate'] * 0.95  # Slightly slower for authority
        
        # SPECIAL FIX for energetic males - make them more energetic
        if voice_type == 'energetic':
            settings['rate'] = 1.25  # Much faster for energetic males
            settings['pitch'] = 0.7   # Still deep but not too deep
    else:
        settings['pitch'] = min(1.8, settings['pitch'] + 0.3)  # Higher for females
        settings['rate'] = settings['rate'] * 1.05  # Slightly faster for femininity
   
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
            🎭 Your {voice_type} {gender} coach is speaking...
        </div>
       
        <div id="voiceButtonContainer_{voice_id}" style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
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
   
    function playVoiceEnhanced_{voice_id}() {{
        if ('speechSynthesis' in window) {{
            // Cancel any existing speech
            speechSynthesis.cancel();
           
            voiceUtterance_{voice_id} = new SpeechSynthesisUtterance(`{clean_text}`);
            isPlaying_{voice_id} = true;
            voiceUtterance_{voice_id}.rate = {settings['rate']};
            voiceUtterance_{voice_id}.pitch = {settings['pitch']};
            voiceUtterance_{voice_id}.volume = 1.0;
           
            // Update UI for playing state
            document.getElementById('voiceMessage_{voice_id}').innerHTML = '🎤 Your {voice_type} {gender} coach is speaking...';
            document.getElementById('manualPlayButton_{voice_id}').style.display = 'none';
            document.getElementById('stopButton_{voice_id}').style.display = 'block';
            document.getElementById('voiceStatus_{voice_id}').style.display = 'block';
            document.getElementById('voiceStatus_{voice_id}').innerHTML = '🔊 Playing {voice_type} {gender} voice...';
           
            // ENHANCED gender and personality-based voice selection
            const voices = speechSynthesis.getVoices();
            let bestVoice = null;
           
            console.log('Available voices:', voices.map(v => v.name + ' (' + v.lang + ')'));
           
            if ('{gender}' === 'male') {{
                // ENHANCED Male voice selection with much more distinct options
                const maleVoiceNames = [
                    'Google UK English Male', 'Microsoft David Desktop', 'Alex', 'Daniel', 'David',
                    'Fred', 'Jorge', 'Juan', 'Diego', 'Carlos', 'Microsoft Mark', 'Google US English',
                    'Chrome OS UK English Male', 'Chrome OS US English Male'
                ];
               
                if ('{voice_type}' === 'wise') {{
                    // Deeper, slower voices for wisdom
                    const wiseVoices = ['Daniel', 'David', 'Alex', 'Google UK English Male', 'Microsoft David Desktop'];
                    bestVoice = voices.find(v => 
                        v.lang.startsWith('en-') && wiseVoices.some(name => v.name.includes(name))
                    );
                }} else if ('{voice_type}' === 'confident' || '{voice_type}' === 'executive') {{
                    // Strong, commanding voices
                    const strongVoices = ['Microsoft Mark', 'David', 'Google US English', 'Alex'];
                    bestVoice = voices.find(v => 
                        v.lang.startsWith('en-') && strongVoices.some(name => v.name.includes(name))
                    );
                }} else if ('{voice_type}' === 'energetic') {{
                    // Younger, more dynamic male voices
                    const energeticVoices = ['Google US English', 'Fred', 'Jorge', 'Microsoft Mark'];
                    bestVoice = voices.find(v => 
                        v.lang.startsWith('en-') && energeticVoices.some(name => v.name.includes(name))
                    );
                }}
               
                // Fallback for males
                if (!bestVoice) {{
                    bestVoice = voices.find(v => 
                        v.lang.startsWith('en-') && 
                        (v.name.toLowerCase().includes('male') || 
                         v.name.toLowerCase().includes('david') ||
                         v.name.toLowerCase().includes('alex') ||
                         v.name.toLowerCase().includes('daniel'))
                    );
                }}
            }} else {{
                // ENHANCED Female voice selection with much more distinct options
                const femaleVoiceNames = [
                    'Google UK English Female', 'Microsoft Zira Desktop', 'Samantha', 'Victoria', 'Karen',
                    'Susan', 'Fiona', 'Moira', 'Tessa', 'Microsoft Hazel', 'Google US English',
                    'Chrome OS UK English Female', 'Chrome OS US English Female'
                ];
               
                if ('{voice_type}' === 'caring') {{
                    // Soft, warm female voices
                    const caringVoices = ['Samantha', 'Susan', 'Microsoft Zira Desktop', 'Google UK English Female'];
                    bestVoice = voices.find(v => 
                        v.lang.startsWith('en-') && caringVoices.some(name => v.name.includes(name))
                    );
                }} else if ('{voice_type}' === 'energetic') {{
                    // Bright, enthusiastic female voices
                    const energeticVoices = ['Victoria', 'Karen', 'Tessa', 'Google US English'];
                    bestVoice = voices.find(v => 
                        v.lang.startsWith('en-') && energeticVoices.some(name => v.name.includes(name))
                    );
                }} else if ('{voice_type}' === 'professional') {{
                    // Clear, business-like female voices
                    const professionalVoices = ['Microsoft Hazel', 'Fiona', 'Google UK English Female'];
                    bestVoice = voices.find(v => 
                        v.lang.startsWith('en-') && professionalVoices.some(name => v.name.includes(name))
                    );
                }}
               
                // Fallback for females
                if (!bestVoice) {{
                    bestVoice = voices.find(v => 
                        v.lang.startsWith('en-') && 
                        (v.name.toLowerCase().includes('female') || 
                         v.name.toLowerCase().includes('samantha') ||
                         v.name.toLowerCase().includes('victoria') ||
                         v.name.toLowerCase().includes('susan'))
                    );
                }}
            }}
           
            // Final fallback to any English voice
            if (!bestVoice) {{
                bestVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
            }}
           
            if (bestVoice) {{
                voiceUtterance_{voice_id}.voice = bestVoice;
                console.log('Selected voice:', bestVoice.name, 'for', '{voice_type}', '{gender}');
            }}
           
            // PERSONALITY-SPECIFIC adjustments
            if ('{voice_type}' === 'wise') {{
                voiceUtterance_{voice_id}.rate = voiceUtterance_{voice_id}.rate * 0.85;  // Slower for wisdom
            }} else if ('{voice_type}' === 'energetic') {{
                if ('{gender}' === 'male') {{
                    // FIXED: Energetic males need more energy
                    voiceUtterance_{voice_id}.rate = voiceUtterance_{voice_id}.rate * 1.3;  // Much faster for energetic males
                    voiceUtterance_{voice_id}.pitch = Math.max(0.6, voiceUtterance_{voice_id}.pitch);  // Not too deep
                }} else {{
                    voiceUtterance_{voice_id}.rate = voiceUtterance_{voice_id}.rate * 1.15;  // Fast but controlled for females
                }}
                voiceUtterance_{voice_id}.volume = 1.0;  // Full volume for excitement
            }} else if ('{voice_type}' === 'caring') {{
                voiceUtterance_{voice_id}.pitch = voiceUtterance_{voice_id}.pitch * 1.1;  // Softer, higher for caring
                voiceUtterance_{voice_id}.rate = voiceUtterance_{voice_id}.rate * 0.9;   // Slightly slower for caring
            }} else if ('{voice_type}' === 'confident' || '{voice_type}' === 'executive') {{
                voiceUtterance_{voice_id}.rate = voiceUtterance_{voice_id}.rate * 0.95;  // Slightly slower for authority
                voiceUtterance_{voice_id}.volume = 1.0;  // Full volume for confidence
            }}
           
            // Voice event handlers
            voiceUtterance_{voice_id}.onstart = function() {{
                console.log('Enhanced voice started playing:', '{voice_type}', '{gender}');
                document.getElementById('voiceStatus_{voice_id}').innerHTML = '🎵 Playing {voice_type} {gender} voice...';
            }};
           
            voiceUtterance_{voice_id}.onend = function() {{
                console.log('Enhanced voice finished playing');
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
                console.error('Enhanced voice error:', event.error);
                isPlaying_{voice_id} = false;
                document.getElementById('voiceMessage_{voice_id}').innerHTML = '❌ Voice playback failed';
                document.getElementById('manualPlayButton_{voice_id}').style.display = 'block';
                document.getElementById('stopButton_{voice_id}').style.display = 'none';
                document.getElementById('voiceStatus_{voice_id}').innerHTML = '❌ Playback error: ' + event.error;
            }};
           
            // Start speech with mobile compatibility
            try {{
                speechSynthesis.speak(voiceUtterance_{voice_id});
                console.log('Enhanced voice started for {voice_type} {gender}');
            }} catch (error) {{
                console.error('Speech synthesis error:', error);
                document.getElementById('voiceStatus_{voice_id}').innerHTML = '❌ Voice playback failed';
            }}
        }} else {{
            document.getElementById('voiceMessage_{voice_id}').innerHTML = '❌ Voice not supported in this browser';
            document.getElementById('voiceStatus_{voice_id}').innerHTML = 'Please use Chrome, Safari, or Edge';
            document.getElementById('voiceStatus_{voice_id}').style.display = 'block';
        }}
    }}
   
    function playVoiceManually_{voice_id}() {{
        console.log('Manual play triggered for enhanced mobile voice');
        playVoiceEnhanced_{voice_id}();
    }}
   
    function stopVoice_{voice_id}() {{
        console.log('Stopping enhanced voice playback');
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
   
    // Enhanced mobile and desktop detection with better autoplay
    console.log('Enhanced device detection - Mobile:', isMobileDevice_{voice_id});
   
    // MOBILE-FIRST approach with better autoplay handling
    if (isMobileDevice_{voice_id}) {{
        // Mobile: Try autoplay first, then show manual button
        console.log('Mobile device detected - attempting smart autoplay');
        document.getElementById('voiceMessage_{voice_id}').innerHTML = '📱 Starting voice for mobile device...';
       
        // Try autoplay after a small delay to let the page settle
        setTimeout(() => {{
            try {{
                playVoiceEnhanced_{voice_id}();
                // If autoplay works on mobile, great! If not, user can tap button
            }} catch (error) {{
                console.log('Mobile autoplay failed (expected), manual button available');
                document.getElementById('voiceMessage_{voice_id}').innerHTML = '📱 Tap button to hear your coach!';
            }}
        }}, 500);
       
    }} else {{
        // Desktop: More aggressive autoplay
        console.log('Desktop device - attempting enhanced autoplay');
        document.getElementById('manualPlayButton_{voice_id}').style.display = 'none';
       
        // Wait for voices to load, then auto-play
        if (speechSynthesis.getVoices().length > 0) {{
            setTimeout(playVoiceEnhanced_{voice_id}, 800);
        }} else {{
            speechSynthesis.onvoiceschanged = function() {{
                setTimeout(playVoiceEnhanced_{voice_id}, 800);
            }};
        }}
       
        // Show manual button as backup if auto-play fails
        setTimeout(() => {{
            if (!speechSynthesis.speaking && !isPlaying_{voice_id}) {{
                console.log('Desktop auto-play failed, showing manual button');
                document.getElementById('manualPlayButton_{voice_id}').style.display = 'block';
                document.getElementById('voiceMessage_{voice_id}').innerHTML = '🖥️ Click to hear your coach (autoplay was blocked)';
            }}
        }}, 3000);
    }}
    </script>
    """
   
    st.components.v1.html(voice_html, height=180)

def create_enhanced_elevenlabs_voice(text, api_key, voice_type, gender):
    """Enhanced ElevenLabs voice with better voice selection and mobile support"""
   
    # ENHANCED Voice selection with more distinct voices
    if gender == 'male':
        voice_configs = {
            'professional': {'voice_id': 'TxGEqnHWrfWFTfGW9XjX', 'name': 'Professional Male', 'stability': 0.9, 'similarity': 0.9},
            'confident': {'voice_id': 'VR6AewLTigWG4xSOukaG', 'name': 'Confident Male', 'stability': 0.8, 'similarity': 0.8},
            'caring': {'voice_id': 'IKne3meq5aSn9XLyUdCD', 'name': 'Caring Male', 'stability': 0.9, 'similarity': 0.9},
            'wise': {'voice_id': 'onwK4e9ZLuTAKqWW03F9', 'name': 'Wise Male', 'stability': 0.95, 'similarity': 0.9},
            'energetic': {'voice_id': 'pNInz6obpgDQGcFmaJgB', 'name': 'Energetic Male', 'stability': 0.6, 'similarity': 0.7},
            'executive': {'voice_id': 'Yko7PKHZNXotIFUBG7I9', 'name': 'Executive Male', 'stability': 0.85, 'similarity': 0.85}
        }
    else:  # female
        voice_configs = {
            'professional': {'voice_id': 'EXAVITQu4vr4xnSDxMaL', 'name': 'Professional Female', 'stability': 0.9, 'similarity': 0.9},
            'confident': {'voice_id': 'ThT5KcBeYPX3keUQqHPh', 'name': 'Confident Female', 'stability': 0.8, 'similarity': 0.8},
            'caring': {'voice_id': '21m00Tcm4TlvDq8ikWAM', 'name': 'Caring Female', 'stability': 0.9, 'similarity': 0.9},
            'wise': {'voice_id': 'XrExE9yKIg1WjnnlVkGX', 'name': 'Wise Female', 'stability': 0.95, 'similarity': 0.9},
            'energetic': {'voice_id': 'AZnzlk1XvdvUeBnXmlld', 'name': 'Energetic Female', 'stability': 0.5, 'similarity': 0.7},
            'executive': {'voice_id': 'SOYHLrjzK2X1ezoPC6cr', 'name': 'Executive Female', 'stability': 0.85, 'similarity': 0.85}
        }
   
    voice_config = voice_configs.get(voice_type, voice_configs['professional'])
    voice_id = voice_config['voice_id']
   
    # Enhanced text for speech
    clean_text = enhance_text_for_speech(text, voice_type)
   
    # Enhanced speed settings
    speed_settings = {
        'wise': 0.8,
        'caring': 0.85,
        'professional': 1.0,
        'executive': 0.95,
        'confident': 1.05,
        'energetic': 1.1 if gender == 'female' else 1.25  # FIXED: Faster for energetic males
    }
   
    voice_speed = speed_settings.get(voice_type, 1.0)
   
    # Enhanced voice generation and playback with mobile support
    voice_html = f"""
    <div style="
        padding: 15px;
        background: linear-gradient(135deg, #e8f5e8, #f0f8ff);
        border-radius: 15px;
        border: 2px solid rgba(76, 175, 80, 0.3);
        margin: 10px 0;
        text-align: center;
    ">
        <div style="color: #4CAF50; font-weight: bold; margin-bottom: 10px;">
            🎭 Premium ElevenLabs Voice: {voice_config['name']}
        </div>
        <div id="elevenlabsStatus" style="color: #666; font-size: 14px;">
            🔄 Loading premium voice...
        </div>
    </div>

    <script>
    async function playEnhancedElevenLabsVoice() {{
        const statusEl = document.getElementById('elevenlabsStatus');
        
        try {{
            statusEl.innerHTML = '🔄 Generating premium {voice_type} {gender} voice...';
            
            const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/{voice_id}', {{
                method: 'POST',
                headers: {{
                    'Accept': 'audio/mpeg',
                    'Content-Type': 'application/json',
                    'xi-api-key': '{api_key}'
                }},
                body: JSON.stringify({{
                    text: `{clean_text}`,
                    model_id: 'eleven_turbo_v2',
                    voice_settings: {{
                        stability: {voice_config['stability']},
                        similarity_boost: {voice_config['similarity']},
                        style: {0.3 if voice_type == 'caring' else 0.8 if voice_type == 'energetic' else 0.5},
                        use_speaker_boost: {str(voice_type in ['confident', 'executive', 'energetic']).lower()},
                        speed: {voice_speed}
                    }}
                }})
            }});
           
            if (response.ok) {{
                statusEl.innerHTML = '🎵 Playing premium {voice_type} voice...';
                
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                // Enhanced mobile-friendly audio playback
                audio.preload = 'auto';
                
                // Mobile compatibility settings
                audio.setAttribute('playsinline', true);
                audio.setAttribute('webkit-playsinline', true);
                
                const playPromise = audio.play();
                
                if (playPromise !== undefined) {{
                    playPromise.then(() => {{
                        console.log('ElevenLabs premium voice playing successfully');
                        statusEl.innerHTML = '🎵 Premium voice playing...';
                    }}).catch(error => {{
                        console.log('ElevenLabs autoplay blocked, using browser TTS fallback');
                        statusEl.innerHTML = '📱 Autoplay blocked - using browser voice fallback';
                        enhancedFallbackToBrowserTTS();
                    }});
                }}
                
                audio.onended = () => {{
                    statusEl.innerHTML = '✅ Premium voice completed!';
                    setTimeout(() => {{
                        statusEl.style.display = 'none';
                    }}, 3000);
                }};
                
                audio.onerror = () => {{
                    statusEl.innerHTML = '❌ Audio error - using browser voice';
                    enhancedFallbackToBrowserTTS();
                }};
                
            }} else {{
                console.log('ElevenLabs API failed, using browser TTS');
                statusEl.innerHTML = '🔄 API limit reached - using enhanced browser voice';
                enhancedFallbackToBrowserTTS();
            }}
        }} catch (error) {{
            console.log('ElevenLabs error, using browser TTS:', error);
            statusEl.innerHTML = '🔄 Using enhanced browser voice';
            enhancedFallbackToBrowserTTS();
        }}
    }}
   
    function enhancedFallbackToBrowserTTS() {{
        if ('speechSynthesis' in window) {{
            speechSynthesis.cancel();
           
            const utterance = new SpeechSynthesisUtterance(`{clean_text}`);
           
            // Enhanced personality-specific settings for fallback
            if ('{voice_type}' === 'wise') {{
                utterance.rate = 0.7;
                utterance.pitch = {0.4 if gender == 'male' else 0.8};
            }} else if ('{voice_type}' === 'energetic') {{
                utterance.rate = {1.3 if gender == 'male' else 1.1};  // FIXED: Faster for energetic males
                utterance.pitch = {0.7 if gender == 'male' else 1.4};
            }} else if ('{voice_type}' === 'caring') {{
                utterance.rate = 0.8;
                utterance.pitch = {0.6 if gender == 'male' else 1.3};
            }} else if ('{voice_type}' === 'confident') {{
                utterance.rate = 1.0;
                utterance.pitch = {0.4 if gender == 'male' else 0.9};
            }} else if ('{voice_type}' === 'professional') {{
                utterance.rate = 0.9;
                utterance.pitch = {0.6 if gender == 'male' else 1.0};
            }} else {{
                utterance.rate = 0.9;
                utterance.pitch = {0.6 if gender == 'male' else 1.0};
            }}
           
            utterance.volume = 1.0;
           
            // Enhanced voice selection for fallback
            const voices = speechSynthesis.getVoices();
            let bestVoice = null;
           
            if ('{gender}' === 'male') {{
                bestVoice = voices.find(v =>
                    v.lang.startsWith('en-') &&
                    (v.name.toLowerCase().includes('male') ||
                     v.name.toLowerCase().includes('david') ||
                     v.name.toLowerCase().includes('daniel') ||
                     v.name.toLowerCase().includes('alex'))
                );
            }} else {{
                bestVoice = voices.find(v =>
                    v.lang.startsWith('en-') &&
                    (v.name.toLowerCase().includes('female') ||
                     v.name.toLowerCase().includes('samantha') ||
                     v.name.toLowerCase().includes('victoria'))
                );
            }}
           
            if (!bestVoice) {{
                bestVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
            }}
           
            if (bestVoice) utterance.voice = bestVoice;
           
            speechSynthesis.speak(utterance);
            
            utterance.onend = () => {{
                document.getElementById('elevenlabsStatus').innerHTML = '✅ Browser voice completed!';
            }};
        }}
    }}
   
    // Start enhanced voice immediately
    if (speechSynthesis.getVoices().length > 0) {{
        setTimeout(playEnhancedElevenLabsVoice, 500);
    }} else {{
        speechSynthesis.onvoiceschanged = () => {{
            setTimeout(playEnhancedElevenLabsVoice, 500);
        }};
    }}
    </script>
    """
   
    st.components.v1.html(voice_html, height=80)

def enhance_text_for_speech(text, voice_type):
    """ENHANCED text processing for MORE distinct personality voices"""
   
    # Remove markdown and clean
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = text.replace('\n', ' ').strip()
   
    # ENHANCED personality-based speech modifications
    if voice_type == 'caring':
        # Gentle, nurturing speech patterns
        text = re.sub(r'\byou\b', 'you, my friend', text, flags=re.IGNORECASE, count=1)
        text = re.sub(r'\.', '. Please take your time with this.', text, count=1)
        text = text.replace(' can ', ' absolutely can ')
        text = text.replace(' will ', ' will surely ')
        text = text.replace(' are ', ' are truly ')
       
    elif voice_type == 'energetic':
        # HIGH ENERGY, motivational speech
        text = re.sub(r'\bgreat\b', 'absolutely FANTASTIC', text, flags=re.IGNORECASE)
        text = re.sub(r'\bgood\b', 'AMAZING', text, flags=re.IGNORECASE)
        text = re.sub(r'\.', '! This is incredible!', text, count=1)
        text = text.replace(' can ', ' can TOTALLY ')
        text = text.replace(' will ', ' will DEFINITELY ')
        text = 'WOW! ' + text + ' I am SO pumped about this!'
       
    elif voice_type == 'wise':
        # Deep, thoughtful, philosophical speech
        text = re.sub(r'\bremember\b', 'always keep in mind', text, flags=re.IGNORECASE)
        text = re.sub(r'\.', '... Think deeply about this.', text, count=1)
        text = 'Hmm... Let me share some wisdom. ' + text
        text = text.replace(' is ', ' truly is ')
        text = text.replace(' can ', ' may indeed ')
       
    elif voice_type == 'professional':
        # Clear, direct, business-focused speech
        text = re.sub(r'\.', '. Let me be very clear about this.', text, count=1)
        text = re.sub(r'\bI think\b', 'Based on my professional analysis', text, flags=re.IGNORECASE)
        text = text.replace(' should ', ' must strategically ')
        text = 'From a professional standpoint: ' + text
       
    elif voice_type == 'confident':
        # Strong, assertive, powerful speech
        text = re.sub(r'\.', '. I am absolutely certain about this.', text, count=1)
        text = re.sub(r'\bI believe\b', 'I KNOW for certain', text, flags=re.IGNORECASE)
        text = text.replace(' might ', ' WILL ')
        text = text.replace(' could ', ' WILL absolutely ')
        text = 'Listen to me: ' + text + ' Trust me on this!'
       
    elif voice_type == 'executive':
        # Authoritative, commanding, leadership speech
        text = re.sub(r'\.', '. This is exactly what top executives do.', text, count=1)
        text = text.replace(' need to ', ' must immediately ')
        text = 'Here is the executive strategy: ' + text + ' Execute this plan now.'
   
    # Add natural speech patterns with personality-specific pauses
    if voice_type == 'wise':
        text = re.sub(r'([.!?])', r'\1... ', text)  # Long pauses for wisdom
    elif voice_type == 'energetic':
        text = re.sub(r'([.!?])', r'\1 ', text)     # Quick pauses for energy
    else:
        text = re.sub(r'([.!?])', r'\1 ', text)     # Normal pauses
   
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

# FIXED Voice Note Processing - Direct Integration
def process_voice_message_directly(voice_input):
    """FIXED: Process voice message and add directly to conversation"""
    if not voice_input or not voice_input.strip():
        return False
   
    try:
        # Clean the voice input
        voice_text = voice_input.strip()
        
        # Reset voice flag for new conversation
        st.session_state.voice_played = False
       
        # Add user voice message to conversation history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': voice_text,
            'timestamp': datetime.now()
        })
       
        # Get coach response immediately
        coach_response = get_coach_response(voice_text, st.session_state.chat_history)
       
        # Add coach response to conversation
        st.session_state.chat_history.append({
            'role': 'coach',
            'content': coach_response,
            'timestamp': datetime.now()
        })
       
        # Enable voice response from coach
        st.session_state.is_speaking = True
        
        return True
        
    except Exception as e:
        st.error(f"Voice processing error: {str(e)}")
        return False

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
            ["caring", "professional", "energetic", "wise", "confident", "executive"],
            index=["caring", "professional", "energetic", "wise", "confident", "executive"].index(
                st.session_state.user_profile.get('voice_type', 'caring')
            ),
            format_func=lambda x: {
                'caring': '💝 Caring & Supportive',
                'professional': '💼 Professional & Direct',
                'energetic': '⚡ Energetic & Motivating',
                'wise': '🧙‍♂️ Wise & Thoughtful',
                'confident': '💪 Confident & Strong',
                'executive': '👔 Executive & Authoritative'
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
        <p>Your AI-powered success mentor with enhanced talking avatars</p>
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
       
        # Regular text input form
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
       
        # FIXED Voice recording section with DIRECT message processing
        st.markdown("---")
        st.markdown("### 🎤 Voice Message")
       
        # FIXED voice note processing - check for voice input FIRST
        voice_processed = False
        
        # Check for voice message parameters (multiple methods for compatibility)
        voice_params_to_check = [
            'voice_direct_send',
            'auto_voice_message', 
            'voice_message',
            'voice_input_processed'
        ]
        
        for param in voice_params_to_check:
            if param in st.query_params:
                voice_message = st.query_params[param]
                # Clear the parameter immediately
                del st.query_params[param]
                
                if voice_message and voice_message.strip():
                    st.success(f"🎤 Voice Message Received: \"{voice_message}\"")
                    
                    # Process the voice message directly
                    if process_voice_message_directly(voice_message):
                        st.balloons()  # Show success animation
                        time.sleep(0.5)  # Brief pause
                        st.rerun()  # Refresh to show updated conversation
                    
                    voice_processed = True
                    break
       
        # Enhanced voice recording interface - FIXED for mobile
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
                    🎤 Tap to start recording, tap again to stop and send
                </div>
            </div>
           
            <!-- Voice Button (RIGHT SIDE) -->
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
        // FIXED TAP-TO-RECORD VOICE SYSTEM with DIRECT message sending
        let tapRecognition;
        let tapRecordingActive = false;
        let tapVoiceTranscript = '';
        let tapButtonState = 'ready'; // 'ready', 'recording', 'processing'
       
        console.log('🎤 FIXED Voice System Loading...');
       
        // Enhanced CSS animations
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
       
        // ENHANCED Speech Recognition Setup
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            tapRecognition = new SpeechRecognition();
           
            // Optimized settings for better accuracy
            tapRecognition.continuous = false;
            tapRecognition.interimResults = true;
            tapRecognition.maxAlternatives = 3;  // More alternatives for better accuracy
            tapRecognition.lang = 'en-US';
           
            tapRecognition.onstart = function() {{
                console.log('✅ Enhanced recording started');
                document.getElementById('voiceStatus').innerHTML = '🔴 Recording... Speak clearly, then tap STOP';
                document.getElementById('voiceWaveform').style.display = 'flex';
                tapVoiceTranscript = '';
            }};
           
            tapRecognition.onresult = function(event) {{
                let currentTranscript = '';
                let finalTranscript = '';
               
                for (let i = event.resultIndex; i < event.results.length; i++) {{
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {{
                        finalTranscript += transcript + ' ';
                    }} else {{
                        currentTranscript += transcript;
                    }}
                }}
               
                // Update running transcript
                if (finalTranscript) {{
                    tapVoiceTranscript += finalTranscript;
                }}
               
                const displayText = (tapVoiceTranscript + currentTranscript).trim();
                if (displayText) {{
                    document.getElementById('voiceStatus').innerHTML = '📝 Heard: "' + displayText + '"';
                }}
            }};
           
            tapRecognition.onend = function() {{
                console.log('🛑 Recording ended. Final transcript:', tapVoiceTranscript.trim());
               
                if (tapVoiceTranscript.trim()) {{
                    // FIXED: Send the message DIRECTLY to conversation
                    sendVoiceMessageToConversation(tapVoiceTranscript.trim());
                }} else {{
                    document.getElementById('voiceStatus').innerHTML = '❌ No speech detected. Try again.';
                    tapResetButton();
                }}
            }};
           
            tapRecognition.onerror = function(event) {{
                console.error('Recognition error:', event.error);
                let errorMsg = '❌ Error: ';
                
                switch(event.error) {{
                    case 'no-speech':
                        errorMsg += 'No speech detected. Speak louder!';
                        break;
                    case 'audio-capture':
                        errorMsg += 'Microphone not available.';
                        break;
                    case 'not-allowed':
                        errorMsg += 'Microphone permission denied.';
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

        // Main tap handler
        function handleVoiceTap() {{
            console.log('🖱️ Voice button tapped. State:', tapButtonState);
           
            if (tapButtonState === 'ready') {{
                tapStartRecording();
            }} else if (tapButtonState === 'recording') {{
                tapStopRecording();
            }}
        }}

        function tapStartRecording() {{
            console.log('▶️ Starting voice recording');
           
            tapButtonState = 'recording';
            tapRecordingActive = true;
           
            const button = document.getElementById('tapVoiceButton');
            button.classList.add('tap-recording');
            button.innerHTML = '⏹️';
           
            document.getElementById('voiceStatus').innerHTML = '🔴 Recording... Speak now, then tap STOP';
            document.getElementById('voiceWaveform').style.display = 'flex';
           
            if (tapRecognition) {{
                try {{
                    tapVoiceTranscript = '';
                    tapRecognition.start();
                }} catch (error) {{
                    console.error('Failed to start recording:', error);
                    document.getElementById('voiceStatus').innerHTML = '❌ Failed to start recording';
                    tapResetButton();
                }}
            }}
        }}

        function tapStopRecording() {{
            console.log('⏹️ Stopping voice recording');
           
            tapButtonState = 'processing';
            tapRecordingActive = false;
           
            const button = document.getElementById('tapVoiceButton');
            button.classList.remove('tap-recording');
            button.classList.add('tap-processing');
            button.innerHTML = '⏳';
           
            document.getElementById('voiceStatus').innerHTML = '⏳ Processing and sending your message...';
           
            if (tapRecognition) {{
                tapRecognition.stop();
            }}
        }}

        // FIXED: Send voice message DIRECTLY to conversation
        function sendVoiceMessageToConversation(message) {{
            console.log('🚀 FIXED: Sending voice message directly:', message);
           
            document.getElementById('voiceStatus').innerHTML = '🚀 Sending: "' + message + '"';
           
            // MULTIPLE methods to ensure message gets through
            const currentUrl = new URL(window.location.href);
           
            // Clear existing parameters
            ['voice_direct_send', 'auto_voice_message', 'voice_message', 'voice_input_processed'].forEach(param => {{
                currentUrl.searchParams.delete(param);
            }});
           
            // Method 1: Direct send (primary)
            currentUrl.searchParams.set('voice_direct_send', encodeURIComponent(message.trim()));
            currentUrl.searchParams.set('voice_timestamp', Date.now().toString());
           
            console.log('🔄 FIXED: Redirecting to process voice message');
            console.log('📝 Message:', message.trim());
           
            // Immediate redirect for reliable processing
            window.location.href = currentUrl.toString();
        }}

        function tapResetButton() {{
            console.log('🔄 Resetting voice button');
           
            tapButtonState = 'ready';
            tapRecordingActive = false;
            tapVoiceTranscript = '';
           
            const button = document.getElementById('tapVoiceButton');
            button.classList.remove('tap-recording', 'tap-processing');
            button.innerHTML = '🎤';
           
            document.getElementById('voiceStatus').innerHTML = '🎤 Tap to start recording, tap again to stop and send';
            document.getElementById('voiceWaveform').style.display = 'none';
        }}
       
        console.log('✅ FIXED Voice System Ready!');
        </script>
        """
       
        st.components.v1.html(voice_section_html, height=200)
       
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.is_speaking = False
            st.session_state.voice_played = False
            st.rerun()

if __name__ == "__main__":
    main()
