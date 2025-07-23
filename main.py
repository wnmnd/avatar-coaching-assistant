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
    if 'voice_message_ready' not in st.session_state:
        st.session_state.voice_message_ready = None

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
    # Use your updated API key
    api_key = "sk_0048770c4dd23670baac2de2cd6f616e2856935e8297be5f"
    
    # Also check secrets/environment as fallback
    if not api_key:
        api_key = st.secrets.get("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY")
    
    # Debug information
    if api_key and api_key.startswith("sk_"):
        return api_key
    else:
        return None

# Fixed Avatar Component
def avatar_component(is_speaking=False):
    """Display fixed avatar with proper rendering"""
    
    profile = st.session_state.user_profile
    avatar_choice = profile.get('avatar', 'sophia')
    
    # Avatar selection with personality and gender (updated with your voice mappings)
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

# BIG BUTTON AUTO-SEND VOICE RECORDER - WORKING VERSION!
def enhanced_voice_recorder():
    """Big button that auto-detects when you finish speaking and provides easy send"""
    
    # Voice recorder HTML with the BIG BUTTON design
    voice_recorder_html = f"""
    <div style="
        padding: 25px;
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        border-radius: 20px;
        border: 2px solid rgba(138, 43, 226, 0.2);
        margin: 10px 0;
        text-align: center;
    ">
        <!-- Status Display -->
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
        
        <!-- Transcription Display -->
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
        
        <!-- BIG VOICE BUTTON -->
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
        
        <!-- Hidden textarea that Streamlit can read -->
        <textarea id="hiddenVoiceText" style="position: absolute; left: -9999px; opacity: 0;" 
                  placeholder="voice_transcription_area"></textarea>
    </div>

    <script>
    let recognition = null;
    let isRecording = false;
    let recordedText = '';
    let silenceTimer = null;
    let finalTranscript = '';
    
    // Initialize speech recognition
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
            
            // Clear existing silence timer
            if (silenceTimer) {{
                clearTimeout(silenceTimer);
            }}
            
            // Set new silence timer - auto-complete after 3 seconds of silence
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
        
        updateStatus('✅ Recorded: "' + finalMessage + '" - Message ready to send!');
        
        // Put the text in the hidden textarea
        const hiddenTextArea = document.getElementById('hiddenVoiceText');
        hiddenTextArea.value = finalMessage;
        
        // Change button to indicate ready to send
        const btn = document.getElementById('voiceBtn');
        btn.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
        btn.innerHTML = '✅';
        btn.style.animation = 'none';
        
        // Show message is ready
        document.getElementById('transcriptionBox').innerHTML = '✅ Ready: "' + finalMessage + '"<br><small>Message captured! Use the send button below.</small>';
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
        
        // Clear the hidden textarea
        const hiddenTextArea = document.getElementById('hiddenVoiceText');
        hiddenTextArea.value = '';
    }}
    
    // CSS animations
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
    
    # Check if there's voice text captured and provide send button
    voice_message_script = """
    <script>
    const hiddenTextArea = document.getElementById('hiddenVoiceText');
    if (hiddenTextArea && hiddenTextArea.value.trim()) {
        // Voice message is ready
        console.log('Voice message ready:', hiddenTextArea.value);
    }
    </script>
    """
    st.components.v1.html(voice_message_script, height=0)
    
    # Simple send button that appears when voice is captured
    send_col1, send_col2, send_col3 = st.columns([1, 2, 1])
    with send_col2:
        if st.button("📤 Send Voice Message", key="send_voice_btn", type="primary", 
                    help="Send the voice message you just recorded"):
            
            # Get voice message from JavaScript using a simple approach
            get_voice_script = """
            <script>
            const hiddenTextArea = document.getElementById('hiddenVoiceText');
            if (hiddenTextArea && hiddenTextArea.value.trim()) {
                // Signal that we have a message ready
                sessionStorage.setItem('voice_ready_to_send', hiddenTextArea.value);
                console.log('Voice message ready for sending:', hiddenTextArea.value);
            } else {
                alert('No voice message recorded yet. Please record a message first.');
            }
            </script>
            """
            st.components.v1.html(get_voice_script, height=0)
            
            # Check session storage for the message
            check_voice_script = """
            <script>
            const voiceMessage = sessionStorage.getItem('voice_ready_to_send');
            if (voiceMessage) {
                // Clear it from storage
                sessionStorage.removeItem('voice_ready_to_send');
                
                // Use URL parameter to send the message
                const url = new URL(window.location.href);
                url.searchParams.set('voice_input', encodeURIComponent(voiceMessage));
                url.searchParams.set('timestamp', Date.now().toString());
                
                console.log('Sending voice message:', voiceMessage);
                window.location.href = url.toString();
            } else {
                console.log('No voice message found in storage');
            }
            </script>
            """
            st.components.v1.html(check_voice_script, height=0)

# Voice Message Checker
def check_voice_message():
    """Check for new voice messages from sessionStorage"""
    
    voice_check_html = """
    <script>
    // Check for voice messages in sessionStorage
    function checkForVoiceMessage() {
        try {
            const voiceDataStr = sessionStorage.getItem('voice_message_data');
            if (voiceDataStr) {
                const voiceData = JSON.parse(voiceDataStr);
                if (!voiceData.processed) {
                    console.log('Found unprocessed voice message:', voiceData.message);
                    // Mark as processed
                    voiceData.processed = true;
                    sessionStorage.setItem('voice_message_data', JSON.stringify(voiceData));
                    // Return the message
                    return voiceData.message;
                }
            }
        } catch (error) {
            console.error('Error checking voice message:', error);
        }
        return null;
    }
    
    // Expose function globally
    window.checkForVoiceMessage = checkForVoiceMessage;
    </script>
    """
    
    st.components.v1.html(voice_check_html, height=0)
    
    # Check if there's a voice message ready
    if st.button("🔄 Check for Voice Message", key=f"voice_check_{int(time.time())}", help="Click to process any recorded voice message"):
        # Use JavaScript to check sessionStorage
        voice_check_script = """
        <script>
        const voiceMessage = window.checkForVoiceMessage ? window.checkForVoiceMessage() : null;
        if (voiceMessage) {
            // Store in a way Streamlit can access
            const url = new URL(window.location.href);
            url.searchParams.set('voice_input', encodeURIComponent(voiceMessage));
            url.searchParams.set('timestamp', Date.now().toString());
            window.location.href = url.toString();
        } else {
            console.log('No voice message found');
        }
        </script>
        """
        st.components.v1.html(voice_check_script, height=0)

# Natural Voice with MOBILE SUPPORT - FIXED WITH YOUR VOICE IDS
def natural_voice_component(text, voice_type="professional"):
    """Enhanced voice playback with improved personality matching using your ElevenLabs voices"""
    if not text or st.session_state.get('voice_played', False):
        return
    
    # Mark voice as played to prevent doubles
    st.session_state.voice_played = True
    
    # Get avatar gender for proper voice selection (enhanced)
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
        # Show API key confirmation
        st.info(f"🔑 Using ElevenLabs API Key: {elevenlabs_key[:10]}...{elevenlabs_key[-5:]}")
        # Premium ElevenLabs voice with YOUR actual voice IDs
        create_instant_elevenlabs_voice(text, elevenlabs_key, voice_type, avatar_info)
    else:
        # Show warning about missing API key
        st.warning("⚠️ ElevenLabs API key not found. Using browser voice fallback.")
        # Enhanced browser TTS with improved personality settings
        create_mobile_friendly_voice(text, voice_type, avatar_info['gender'])

def create_mobile_friendly_voice(text, voice_type, gender):
    """Mobile-friendly browser TTS with enhanced personality settings"""
    
    clean_text = enhance_text_for_speech(text, voice_type)
    
    # Simplified voice personality settings (3 types only)
    voice_settings = {
        'caring': {'rate': 0.75, 'pitch': 1.2, 'emphasis': 'gentle'},
        'professional': {'rate': 0.9, 'pitch': 1.0, 'emphasis': 'neutral'},
        'energetic': {'rate': 1.3, 'pitch': 1.4, 'emphasis': 'excited'}
    }
    
    settings = voice_settings.get(voice_type, voice_settings['professional'])
    
    # Strong gender adjustments
    if gender == 'male':
        settings['pitch'] = max(0.4, settings['pitch'] - 0.4)  # Much deeper for males
    else:
        settings['pitch'] = min(1.6, settings['pitch'] + 0.2)  # Higher for females
    
    # Add personality-specific pauses and emphasis (simplified)
    if voice_type == 'caring':
        clean_text = clean_text.replace(',', ', ')    # More deliberate pauses
        clean_text = clean_text.replace('you', 'you... ')  # Gentle emphasis
    elif voice_type == 'energetic':
        clean_text = clean_text.replace('!', '! ')    # Excitement bursts
        clean_text = clean_text.replace('.', '! ')    # Turn periods to exclamation
    elif voice_type == 'professional':
        clean_text = clean_text.replace('.', '. ')    # Clear, firm statements
    
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
            🎭 Your coach is speaking...
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
            // Cancel any existing speech
            speechSynthesis.cancel();
            
            voiceUtterance = new SpeechSynthesisUtterance(`{clean_text}`);
            voiceUtterance.rate = {settings['rate']};
            voiceUtterance.pitch = {settings['pitch']};
            voiceUtterance.volume = 1.0;
            
            // Gender and personality-based voice selection (simplified)
            const voices = speechSynthesis.getVoices();
            let bestVoice;
            
            if ('{gender}' === 'male') {{
                // Male voice selection with personality matching
                if ('{voice_type}' === 'caring') {{
                    bestVoice = voices.find(v => 
                        v.lang.startsWith('en-') && 
                        (v.name.toLowerCase().includes('daniel') ||
                         v.name.toLowerCase().includes('alex') ||
                         v.name.toLowerCase().includes('male'))
                    );
                }} else if ('{voice_type}' === 'professional') {{
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
                voiceUtterance.voice = bestVoice;
                console.log('Selected voice:', bestVoice.name, 'for', '{voice_type}', '{gender}');
            }}
            
            // Personality-specific speech adjustments (enhanced)
            if ('{voice_type}' === 'wise') {{
                voiceUtterance.rate = voiceUtterance.rate * 0.8;  // Even slower for wisdom
            }} else if ('{voice_type}' === 'energetic') {{
                voiceUtterance.rate = voiceUtterance.rate * 1.2;  // Even faster for energy
                voiceUtterance.volume = 1.0;  // Full volume for excitement
            }} else if ('{voice_type}' === 'caring') {{
                voiceUtterance.pitch = voiceUtterance.pitch * 1.1;  // Softer, higher for caring
            }} else if ('{voice_type}' === 'confident') {{
                voiceUtterance.rate = voiceUtterance.rate * 1.0;
                voiceUtterance.pitch = voiceUtterance.pitch * 0.9;  // Slightly lower for confidence
            }} else if ('{voice_type}' === 'executive') {{
                voiceUtterance.rate = voiceUtterance.rate * 0.95;  // Controlled pace
                voiceUtterance.pitch = voiceUtterance.pitch * 0.85; // Authoritative tone
            }}
            
            // Start speech
            speechSynthesis.speak(voiceUtterance);
            console.log('Voice started for {voice_type} {gender}');
        }}
    }}
    
    function playVoiceManually() {{
        const button = document.getElementById('playVoiceButton');
        button.style.display = 'none';
        playVoiceMobileFriendly();
    }}
    
    // Handle mobile autoplay restrictions
    if (isMobileDevice) {{
        // Show manual play button for mobile
        document.getElementById('playVoiceButton').style.display = 'inline-block';
        console.log('Mobile device detected - showing manual play button');
    }} else {{
        // Auto-play for desktop
        if (speechSynthesis.getVoices().length > 0) {{
            setTimeout(playVoiceMobileFriendly, 500);
        }} else {{
            speechSynthesis.onvoiceschanged = function() {{
                setTimeout(playVoiceMobileFriendly, 500);
            }};
        }}
    }}
    
    // Also try auto-play even on mobile (some browsers allow it)
    setTimeout(() => {{
        if (!isMobileDevice || speechSynthesis.speaking) {{
            // Hide manual button if auto-play worked
            document.getElementById('playVoiceButton').style.display = 'none';
        }}
    }}, 1000);
    </script>
    """
    
    st.components.v1.html(voice_html, height=120)

def create_instant_elevenlabs_voice(text, api_key, voice_type, avatar_info):
    """Instant ElevenLabs voice with avatar-based voice selection and personality-based tone adjustments"""
    
    # Validate API key format
    if not api_key or not api_key.startswith("sk_") or len(api_key) < 20:
        st.error(f"❌ Invalid ElevenLabs API key format: {api_key[:10] if api_key else 'None'}...")
        return
    
    # Get voice ID from avatar (same voice per avatar, personality only affects tone/speed/energy)
    voice_id = avatar_info['voice_id']
    voice_name = f"{avatar_info['name']} ({avatar_info['gender']})"
    
    # Personality-based voice settings (only tone, speed, energy - NOT voice selection)
    personality_settings = {
        'caring': {
            'stability': 0.8,        # Calm and steady
            'similarity_boost': 0.9, # Clear and warm
            'style': 0.2,           # Gentle style
            'speed': 0.9,           # Slower, more thoughtful pace
            'description': 'Calm & Empathetic'
        },
        'professional': {
            'stability': 0.9,        # Very stable and controlled
            'similarity_boost': 0.8, # Clear and authoritative  
            'style': 0.4,           # Neutral, business-like
            'speed': 1.0,           # Normal, clear pace
            'description': 'Formal & Direct'
        },
        'energetic': {
            'stability': 0.5,        # More dynamic and variable
            'similarity_boost': 0.7, # Expressive and lively
            'style': 0.8,           # High energy style
            'speed': 1.2,           # Faster, more excited pace
            'description': 'High Energy & Happy'
        }
    }
    
    # Get settings for current personality
    settings = personality_settings.get(voice_type, personality_settings['professional'])
    
    # Clean text for speech
    clean_text = enhance_text_for_speech(text, voice_type)
    
    # VISIBLE STATUS VERSION - Shows exactly what's happening
    voice_html = f"""
    <div style="
        padding: 20px;
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        border-radius: 15px;
        border: 2px solid rgba(138, 43, 226, 0.3);
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.2);
    ">
        <div style="margin-bottom: 15px; color: #8A2BE2; font-weight: bold; font-size: 18px;">
            🎤 Voice System Status
        </div>
        
        <div id="voiceSystemStatus" style="
            padding: 15px; 
            background: white; 
            border-radius: 10px; 
            margin: 10px 0;
            color: #333;
            font-weight: bold;
            border: 2px solid #ddd;
        ">
            🔄 Initializing voice system...
        </div>
        
        <div id="voiceDetails" style="
            padding: 10px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            margin: 10px 0;
            color: #666;
            font-size: 14px;
            font-family: monospace;
        ">
            Voice: {voice_name}<br>
            Voice ID: {voice_id}<br>
            Personality: {voice_type} ({settings['description']})<br>
            Speed: {settings['speed']}x | Energy: {settings['style']} | Stability: {settings['stability']}<br>
            API Key: {api_key[:10]}...{api_key[-5:]}
        </div>
        
        <div id="errorDetails" style="
            padding: 10px; 
            background: #fff5f5; 
            border-radius: 8px; 
            margin: 10px 0;
            color: #dc3545;
            font-size: 12px;
            font-family: monospace;
            border: 1px solid #dc3545;
            display: none;
        ">
            Error details will appear here...
        </div>
        
        <button onclick="retryVoice()" style="
            background: linear-gradient(135deg, #8A2BE2, #9370DB);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 10px 20px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3);
            margin: 5px;
        ">🔄 Retry Voice</button>
        
        <button onclick="forceBrowserVoice()" style="
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 10px 20px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
            margin: 5px;
        ">🔊 Force Browser Voice</button>
    </div>
    
    <script>
    // Prevent multiple simultaneous voices
    if (window.speechSynthesis) {{
        window.speechSynthesis.cancel();
    }}
    
    function updateVoiceStatus(message, color = '#333', bgColor = 'white') {{
        const statusDiv = document.getElementById('voiceSystemStatus');
        statusDiv.innerHTML = message;
        statusDiv.style.color = color;
        statusDiv.style.backgroundColor = bgColor;
        statusDiv.style.borderColor = color;
    }}
    
    function showErrorDetails(error) {{
        const errorDiv = document.getElementById('errorDetails');
        errorDiv.innerHTML = error;
        errorDiv.style.display = 'block';
    }}
    
    function hideErrorDetails() {{
        const errorDiv = document.getElementById('errorDetails');
        errorDiv.style.display = 'none';
    }}
    
    function retryVoice() {{
        playInstantVoice();
    }}
    
    function forceBrowserVoice() {{
        updateVoiceStatus('🔊 FORCING BROWSER VOICE (for comparison)', '#28a745', '#f8fff8');
        fallbackToBrowserTTS();
    }}
    
    async function playInstantVoice() {{
        updateVoiceStatus('🔄 ATTEMPTING ELEVENLABS...', '#4169e1', '#f0f8ff');
        hideErrorDetails();
        
        try {{
            console.log('=== ELEVENLABS DEBUG INFO ===');
            console.log('API Key:', '{api_key[:10]}...{api_key[-5:]}');
            console.log('Voice ID:', '{voice_id}');
            console.log('Voice Name:', '{voice_name}');
            console.log('Personality:', '{voice_type}');
            console.log('Settings:', {settings});
            console.log('Text to speak:', `{clean_text}`);
            
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
            
            console.log('Request body:', JSON.stringify(requestBody, null, 2));
            
            updateVoiceStatus('📡 Sending request to ElevenLabs...', '#4169e1', '#f0f8ff');
            
            const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/{voice_id}', {{
                method: 'POST',
                headers: {{
                    'Accept': 'audio/mpeg',
                    'Content-Type': 'application/json',
                    'xi-api-key': '{api_key}'
                }},
                body: JSON.stringify(requestBody)
            }});
            
            console.log('ElevenLabs response status:', response.status);
            console.log('ElevenLabs response headers:', Object.fromEntries(response.headers.entries()));
            
            if (response.ok) {{
                updateVoiceStatus('✅ ELEVENLABS SUCCESS! Processing audio...', '#28a745', '#f8fff8');
                
                const audioBlob = await response.blob();
                console.log('Audio blob size:', audioBlob.size, 'bytes');
                console.log('Audio blob type:', audioBlob.type);
                
                if (audioBlob.size === 0) {{
                    throw new Error('Received empty audio blob from ElevenLabs');
                }}
                
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                audio.play().then(() => {{
                    updateVoiceStatus('🎵 ELEVENLABS PLAYING: {voice_name} ({settings["description"]})', '#28a745', '#f8fff8');
                    console.log('ElevenLabs audio playing successfully!');
                }}).catch(error => {{
                    console.log('Audio play blocked/failed:', error);
                    showErrorDetails('Audio play blocked: ' + error.message + '<br>This is usually due to browser autoplay restrictions.');
                    updateVoiceStatus('⚠️ ELEVENLABS AUDIO BLOCKED - Using browser fallback', '#ff8c00', '#fff8dc');
                    setTimeout(fallbackToBrowserTTS, 500);
                }});
                
                audio.onended = function() {{
                    URL.revokeObjectURL(audioUrl);
                    updateVoiceStatus('✅ ELEVENLABS COMPLETED: {voice_name} ({settings["description"]})', '#28a745', '#f8fff8');
                }};
                
                audio.onerror = function(error) {{
                    console.error('Audio playback error:', error);
                    showErrorDetails('Audio playback error: ' + JSON.stringify(error));
                    updateVoiceStatus('❌ ELEVENLABS AUDIO ERROR - Using browser fallback', '#dc3545', '#fff5f5');
                    setTimeout(fallbackToBrowserTTS, 500);
                }};
                
            }} else {{
                // Get detailed error information
                let errorText = '';
                try {{
                    errorText = await response.text();
                }} catch (e) {{
                    errorText = 'Could not read error response';
                }}
                
                console.error('ElevenLabs API error:', response.status, errorText);
                
                let errorMessage = '';
                let errorDetails = '';
                
                if (response.status === 401) {{
                    errorMessage = '❌ ELEVENLABS: INVALID API KEY';
                    errorDetails = 'API Key is invalid or expired.<br>Status: 401<br>Response: ' + errorText;
                }} else if (response.status === 403) {{
                    errorMessage = '❌ ELEVENLABS: ACCESS FORBIDDEN';
                    errorDetails = 'API Key lacks permissions or voice access.<br>Status: 403<br>Response: ' + errorText;
                }} else if (response.status === 429) {{
                    errorMessage = '❌ ELEVENLABS: RATE LIMIT EXCEEDED';
                    errorDetails = 'Too many requests or out of credits.<br>Status: 429<br>Response: ' + errorText;
                }} else if (response.status === 422) {{
                    errorMessage = '❌ ELEVENLABS: INVALID REQUEST';
                    errorDetails = 'Request format or voice ID invalid.<br>Status: 422<br>Response: ' + errorText;
                }} else {{
                    errorMessage = '❌ ELEVENLABS: API ERROR (' + response.status + ')';
                    errorDetails = 'Unknown API error.<br>Status: ' + response.status + '<br>Response: ' + errorText;
                }}
                
                updateVoiceStatus(errorMessage, '#dc3545', '#fff5f5');
                showErrorDetails(errorDetails);
                setTimeout(fallbackToBrowserTTS, 2000);
            }}
            
        }} catch (error) {{
            console.error('ElevenLabs network/fetch error:', error);
            
            let errorMessage = '❌ ELEVENLABS: NETWORK ERROR';
            let errorDetails = 'Network request failed.<br>Error: ' + error.message + '<br>';
            
            if (error.message.includes('CORS')) {{
                errorDetails += 'This is likely a CORS (Cross-Origin) policy issue.<br>Try running in a different browser or environment.';
            }} else if (error.message.includes('Failed to fetch')) {{
                errorDetails += 'Network connection failed.<br>Check your internet connection and firewall settings.';
            }} else {{
                errorDetails += 'Unexpected network error occurred.';
            }}
            
            updateVoiceStatus(errorMessage, '#dc3545', '#fff5f5');
            showErrorDetails(errorDetails);
            setTimeout(fallbackToBrowserTTS, 2000);
        }}
    }}
    
    function fallbackToBrowserTTS() {{
        updateVoiceStatus('🤖 USING BROWSER VOICE (robotic fallback)', '#ff8c00', '#fff8dc');
        
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(`{clean_text}`);
            
            // Personality-based settings for browser TTS
            if ('{voice_type}' === 'caring') {{
                utterance.rate = 0.75;
                utterance.pitch = {0.6 if avatar_info['gender'] == 'male' else 1.2};
            }} else if ('{voice_type}' === 'energetic') {{
                utterance.rate = 1.4;
                utterance.pitch = {0.8 if avatar_info['gender'] == 'male' else 1.6};
            }} else {{ // professional
                utterance.rate = 0.9;
                utterance.pitch = {0.7 if avatar_info['gender'] == 'male' else 1.0};
            }}
            
            utterance.volume = 1.0;
            
            // Gender-based voice selection for fallback
            const voices = speechSynthesis.getVoices();
            let bestVoice;
            
            if ('{avatar_info['gender']}' === 'male') {{
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
            
            if (bestVoice) {{
                utterance.voice = bestVoice;
                console.log('Using browser voice:', bestVoice.name);
            }}
            
            utterance.onstart = function() {{
                updateVoiceStatus('🤖 BROWSER VOICE PLAYING: ' + (bestVoice ? bestVoice.name : 'Default'), '#ff8c00', '#fff8dc');
            }};
            
            utterance.onend = function() {{
                updateVoiceStatus('✅ BROWSER VOICE COMPLETED (robotic)', '#ff8c00', '#fff8dc');
            }};
            
            utterance.onerror = function(error) {{
                updateVoiceStatus('❌ BROWSER VOICE ERROR: ' + error.error, '#dc3545', '#fff5f5');
            }};
            
            speechSynthesis.speak(utterance);
            
        }} else {{
            updateVoiceStatus('❌ NO VOICE SUPPORT AVAILABLE', '#dc3545', '#fff5f5');
        }}
    }}
    
    // Start playing immediately
    setTimeout(playInstantVoice, 500);
    </script>
    """
    
    st.components.v1.html(voice_html, height=300)

def enhance_text_for_speech(text, voice_type):
    """Make text more expressive for the 3 personality types"""
    
    # Remove markdown and clean
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = text.replace('\n', ' ').strip()
    
    # Personality-based text enhancements (simplified to 3 types)
    if voice_type == 'caring':
        # Gentle, nurturing speech patterns
        text = re.sub(r'\byou\b', 'you, dear', text, flags=re.IGNORECASE, count=1)
        text = re.sub(r'\.', '. Take your time with this.', text, count=1)
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
        
    elif voice_type == 'professional':
        # Clear, direct, business-like speech
        text = re.sub(r'\.', '. Let me be clear on this point.', text, count=1)
        text = re.sub(r'\bI think\b', 'Based on my analysis', text, flags=re.IGNORECASE)
        text = text.replace(' should ', ' must strategically ')
        text = text.replace(' can ', ' should systematically ')
    
    # Add natural speech patterns
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
        
        # Voice personality (simplified to 3 options)
        st.subheader("🎤 Voice Personality")
        voice_type = st.selectbox(
            "Coach Personality",
            ["caring", "professional", "energetic"],
            index=["caring", "professional", "energetic"].index(
                st.session_state.user_profile.get('voice_type', 'caring')
            ),
            format_func=lambda x: {
                'caring': '💝 Caring & Supportive (Calm, Empathetic)',
                'professional': '💼 Professional & Direct (Formal, Business-like)', 
                'energetic': '⚡ Energetic & Motivating (High Energy, Happy Vibes)'
            }[x]
        )
        
        # Show which voices will be used
        st.info("🎤 **Your Voice Mapping:**\n\n"
                "**Each avatar has their own unique voice:**\n"
                "• Sophia → Emily (Female)\n"
                "• Marcus → Adam (Male)\n"
                "• Elena → Freya (Female)\n"
                "• David → Arnold (Male)\n"
                "• Maya → Glinda (Female)\n"
                "• James → Antoni (Male)\n\n"
                "**Personality affects tone/speed/energy only!**\n"
                "• Caring: Calm & slow (0.8x speed)\n"
                "• Professional: Clear & normal (1.0x speed)\n"
                "• Energetic: Fast & exciting (1.2x speed)")
        
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

# Process voice input from URL parameters
def process_voice_input():
    """Process voice input from URL parameters"""
    if 'voice_input' in st.query_params and 'timestamp' in st.query_params:
        voice_message = st.query_params['voice_input']
        timestamp = st.query_params['timestamp']
        
        # Clear the parameters immediately to prevent reprocessing
        del st.query_params['voice_input']
        del st.query_params['timestamp']
        
        if voice_message.strip():
            # Reset voice flag for new conversation
            st.session_state.voice_played = False
            
            # Add user message to conversation
            st.session_state.chat_history.append({
                'role': 'user',
                'content': voice_message.strip(),
                'timestamp': datetime.now()
            })
            
            # Get coach response
            with st.spinner("Your coach is responding to your voice message..."):
                coach_response = get_coach_response(voice_message, st.session_state.chat_history)
            
            # Add coach response to conversation
            st.session_state.chat_history.append({
                'role': 'coach',
                'content': coach_response,
                'timestamp': datetime.now()
            })
            
            # Enable voice response
            st.session_state.is_speaking = True
            
            # Show success message
            st.success(f"🎤 Voice message processed: \"{voice_message}\"")
            
            # Force rerun to show the updated conversation
            st.rerun()

def main():
    load_css()
    init_session_state()
    
    # Check for voice messages from sessionStorage FIRST
    voice_check_script = """
    <script>
    const voiceMessage = sessionStorage.getItem('streamlit_voice_message');
    if (voiceMessage) {
        try {
            const data = JSON.parse(voiceMessage);
            if (data.message) {
                console.log('Processing voice message:', data.message);
                // Clear the storage
                sessionStorage.removeItem('streamlit_voice_message');
                // Set URL parameter to trigger processing
                const url = new URL(window.location.href);
                url.searchParams.set('voice_input', encodeURIComponent(data.message));
                url.searchParams.set('timestamp', data.timestamp.toString());
                window.location.href = url.toString();
            }
        } catch (error) {
            console.error('Error processing voice message:', error);
            sessionStorage.removeItem('streamlit_voice_message');
        }
    }
    </script>
    """
    
    st.components.v1.html(voice_check_script, height=0)
    
    # Process voice input AFTER checking storage
    process_voice_input()
    
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
        
        # Voice recording section
        st.markdown("---")
        st.markdown("### 🎤 Voice Message")
        st.info("💡 **BIG BUTTON:** Click to record → speak your message → automatically stops when you finish → click send!")
        
        # Big button auto-detecting voice recorder
        enhanced_voice_recorder()
        
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.is_speaking = False
            st.session_state.voice_played = False
            st.rerun()

    # DEBUG SECTION - Add this at the bottom
    st.markdown("---")
    
    with st.expander("🔧 **DEBUG VOICE ISSUES** - Click to troubleshoot voice problems"):
        st.markdown("### 🔧 Voice Debug Center")
        st.info("Use this section to test and fix voice issues")
        
        # Test 1: API Key Test
        st.subheader("1️⃣ API Key Test")
        
        # Get API key from secrets or allow manual input
        current_api_key = setup_elevenlabs()
        
        # Let user override for testing
        test_api_key = st.text_input(
            "Test with different API Key (optional):", 
            type="password", 
            help="Leave empty to use your configured key",
            placeholder="sk_xxxxxxxxxxxxxxx"
        )
        
        api_key_to_test = test_api_key if test_api_key else current_api_key
        
        if api_key_to_test:
            if api_key_to_test.startswith("sk_"):
                st.success(f"✅ API key format looks correct: {api_key_to_test[:10]}...{api_key_to_test[-5:]}")
                
                # Test API connection
                if st.button("🔍 Test API Connection", key="test_api_connection"):
                    try:
                        import requests
                        headers = {'xi-api-key': api_key_to_test}
                        response = requests.get('https://api.elevenlabs.io/v1/voices', headers=headers)
                        
                        if response.status_code == 200:
                            voices = response.json()['voices']
                            st.success(f"✅ API Connected! Found {len(voices)} voices")
                            
                            # Show available voices
                            st.markdown("**Your Available Voices:**")
                            for voice in voices:
                                st.write(f"• **{voice['name']}** - ID: `{voice['voice_id']}`")
                                
                        elif response.status_code == 401:
                            st.error("❌ API Key Invalid - Check your ElevenLabs API key")
                        elif response.status_code == 403:
                            st.error("❌ API Key Forbidden - Check your account permissions")
                        else:
                            st.error(f"❌ API Error: {response.status_code} - {response.text}")
                            
                    except Exception as e:
                        st.error(f"❌ Connection Error: {str(e)}")
            else:
                st.error("❌ API key should start with 'sk_'")
        else:
            st.warning("⚠️ No API key found. Please set ELEVENLABS_API_KEY in your secrets.")

        # Test 2: Voice Generation Test
        st.subheader("2️⃣ Voice Generation Test")
        
        if api_key_to_test and api_key_to_test.startswith("sk_"):
            
            debug_col1, debug_col2 = st.columns(2)
            
            with debug_col1:
                test_voice_id = st.selectbox("Select Voice ID to Test:", [
                    "LcfcDJNUP1GQjkzn1xUU",  # Emily (Sophia)
                    "pNInz6obpgDQGcFmaJgB",  # Adam (Marcus)
                    "jsCqWAovK2LkecY7zXl4",  # Freya (Elena)
                    "VR6AewLTigWG4xSOukaG",  # Arnold (David)
                    "z9fAnlkpzviPz146aGWa",  # Glinda (Maya)
                    "ErXwobaYiN019PkySvjV",  # Antoni (James)
                ], key="debug_voice_select")
            
            with debug_col2:
                test_message = st.text_input("Test Message:", 
                                           value="Hello! This is a debug voice test.", 
                                           key="debug_message")
            
            if st.button("🎤 Generate & Test Voice", key="test_voice_generation"):
                if test_message.strip():
                    
                    # Show detailed debug info
                    st.markdown("**Debug Info:**")
                    st.code(f"""
API Key: {api_key_to_test[:10]}...{api_key_to_test[-5:]}
Voice ID: {test_voice_id}
Message: {test_message}
                    """)
                    
                    # Create enhanced debug voice test
                    voice_debug_html = f"""
                    <div style="
                        padding: 20px; 
                        background: linear-gradient(135deg, #f0f8ff, #e6f3ff); 
                        border: 2px solid #4169e1; 
                        border-radius: 15px;
                        margin: 10px 0;
                        box-shadow: 0 4px 15px rgba(65, 105, 225, 0.3);
                    ">
                        <h3 style="color: #4169e1;">🎤 Voice Debug Test</h3>
                        <div id="debugStatus" style="
                            padding: 10px; 
                            background: white; 
                            border-radius: 8px; 
                            margin: 10px 0;
                            font-weight: bold;
                        ">Starting voice test...</div>
                        
                        <button id="testBtn" onclick="testVoice()" style="
                            background: linear-gradient(135deg, #4169e1, #1e90ff); 
                            color: white; 
                            border: none; 
                            padding: 12px 24px; 
                            border-radius: 25px;
                            cursor: pointer;
                            font-weight: bold;
                            box-shadow: 0 4px 15px rgba(65, 105, 225, 0.3);
                            margin: 10px 5px;
                        ">🔄 Test Voice Again</button>
                        
                        <button onclick="testBrowserFallback()" style="
                            background: linear-gradient(135deg, #28a745, #20c997); 
                            color: white; 
                            border: none; 
                            padding: 12px 24px; 
                            border-radius: 25px;
                            cursor: pointer;
                            font-weight: bold;
                            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
                            margin: 10px 5px;
                        ">🔊 Test Browser Voice</button>
                        
                        <div id="debugDetails" style="
                            margin-top: 15px; 
                            padding: 15px; 
                            background: #f8f9fa; 
                            border-radius: 8px;
                            font-family: 'Courier New', monospace;
                            font-size: 12px;
                            max-height: 300px;
                            overflow-y: auto;
                            border: 1px solid #dee2e6;
                        "></div>
                    </div>

                    <script>
                    function updateStatus(message, color = '#4169e1') {{
                        const statusDiv = document.getElementById('debugStatus');
                        statusDiv.innerHTML = message;
                        statusDiv.style.color = color;
                    }}
                    
                    function updateDetails(message) {{
                        const details = document.getElementById('debugDetails');
                        const timestamp = new Date().toLocaleTimeString();
                        details.innerHTML += `[${{timestamp}}] ${{message}}<br>`;
                        details.scrollTop = details.scrollHeight;
                    }}
                    
                    function testBrowserFallback() {{
                        updateStatus('🔊 Testing Browser Voice...', '#28a745');
                        updateDetails('=== BROWSER VOICE TEST ===');
                        
                        if ('speechSynthesis' in window) {{
                            speechSynthesis.cancel();
                            
                            const utterance = new SpeechSynthesisUtterance('{test_message}');
                            utterance.rate = 0.9;
                            utterance.pitch = 1.0;
                            utterance.volume = 1.0;
                            
                            const voices = speechSynthesis.getVoices();
                            updateDetails(`Available voices: ${{voices.length}}`);
                            
                            if (voices.length > 0) {{
                                const englishVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
                                utterance.voice = englishVoice;
                                updateDetails(`Using voice: ${{englishVoice.name}}`);
                            }}
                            
                            utterance.onstart = function() {{
                                updateStatus('🎵 Browser voice playing...', '#28a745');
                                updateDetails('Browser voice started playing');
                            }};
                            
                            utterance.onend = function() {{
                                updateStatus('✅ Browser voice completed!', '#28a745');
                                updateDetails('Browser voice playback completed');
                            }};
                            
                            utterance.onerror = function(error) {{
                                updateStatus('❌ Browser voice error: ' + error.error, '#dc3545');
                                updateDetails('Browser voice error: ' + error.error);
                            }};
                            
                            speechSynthesis.speak(utterance);
                            updateDetails('Browser voice command sent');
                            
                        }} else {{
                            updateStatus('❌ Browser voice not supported', '#dc3545');
                            updateDetails('speechSynthesis not available in this browser');
                        }}
                    }}
                    
                    async function testVoice() {{
                        updateStatus('🔄 Testing ElevenLabs voice...', '#4169e1');
                        updateDetails('=== ELEVENLABS VOICE TEST ===');
                        updateDetails('API Key: {api_key_to_test[:10]}...{api_key_to_test[-5:]}');
                        updateDetails('Voice ID: {test_voice_id}');
                        updateDetails('Message: {test_message}');
                        
                        try {{
                            updateDetails('Making API request to ElevenLabs...');
                            updateStatus('📡 Connecting to ElevenLabs...', '#4169e1');
                            
                            const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/{test_voice_id}', {{
                                method: 'POST',
                                headers: {{
                                    'Accept': 'audio/mpeg',
                                    'Content-Type': 'application/json',
                                    'xi-api-key': '{api_key_to_test}'
                                }},
                                body: JSON.stringify({{
                                    text: `{test_message}`,
                                    model_id: 'eleven_monolingual_v1',
                                    voice_settings: {{
                                        stability: 0.5,
                                        similarity_boost: 0.5,
                                        style: 0.5,
                                        use_speaker_boost: true,
                                        speed: 1.0
                                    }}
                                }})
                            }});
                            
                            updateDetails('Response received - Status: ' + response.status);
                            
                            if (response.ok) {{
                                updateStatus('✅ API Success! Processing audio...', '#28a745');
                                updateDetails('Audio blob received, creating audio player...');
                                
                                const audioBlob = await response.blob();
                                updateDetails(`Audio blob size: ${{audioBlob.size}} bytes`);
                                
                                const audioUrl = URL.createObjectURL(audioBlob);
                                const audio = new Audio(audioUrl);
                                
                                updateDetails('Attempting to play audio...');
                                
                                audio.play().then(() => {{
                                    updateStatus('🎵 ElevenLabs voice playing successfully!', '#28a745');
                                    updateDetails('Audio playing successfully!');
                                }}).catch(error => {{
                                    updateStatus('❌ Audio play blocked: ' + error.message, '#dc3545');
                                    updateDetails('Audio play error: ' + error.message);
                                    updateDetails('This might be due to browser autoplay restrictions');
                                }});
                                
                                audio.onended = function() {{
                                    URL.revokeObjectURL(audioUrl);
                                    updateStatus('✅ ElevenLabs voice test completed!', '#28a745');
                                    updateDetails('Audio playback completed successfully');
                                }};
                                
                                audio.onerror = function(error) {{
                                    updateStatus('❌ Audio playback error', '#dc3545');
                                    updateDetails('Audio element error: ' + error);
                                }};
                                
                            }} else {{
                                const errorText = await response.text();
                                updateStatus('❌ API Error: ' + response.status, '#dc3545');
                                updateDetails('API Error Details: ' + errorText);
                                
                                if (response.status === 401) {{
                                    updateDetails('ERROR: Invalid API key - check your ElevenLabs account');
                                }} else if (response.status === 403) {{
                                    updateDetails('ERROR: Access forbidden - check API key permissions');
                                }} else if (response.status === 429) {{
                                    updateDetails('ERROR: Rate limit exceeded - wait a moment and try again');
                                }}
                            }}
                            
                        }} catch (error) {{
                            updateStatus('❌ Network Error: ' + error.message, '#dc3545');
                            updateDetails('JavaScript/Network Error: ' + error.message);
                            updateDetails('Check your internet connection and CORS settings');
                        }}
                    }}
                    
                    // Auto-run the test
                    setTimeout(testVoice, 1000);
                    </script>
                    """
                    
                    st.components.v1.html(voice_debug_html, height=500)

        # Test 3: Current Configuration Check
        st.subheader("3️⃣ Current Configuration Check")
        
        config_info = f"""
**Current Settings:**
- Avatar: {st.session_state.user_profile.get('avatar', 'Not set')}
- Voice Type: {st.session_state.user_profile.get('voice_type', 'Not set')}
- API Key Status: {'✅ Set' if setup_elevenlabs() else '❌ Not set'}
- Chat History: {len(st.session_state.chat_history)} messages
- Voice Played Flag: {st.session_state.get('voice_played', 'Not set')}
        """
        
        st.code(config_info)
        
        # Test 4: Troubleshooting Guide
        st.subheader("4️⃣ Common Issues & Solutions")
        
        st.markdown("""
        **🔑 API Key Issues:**
        - Make sure your API key starts with `sk_`
        - Check that you have credits in your ElevenLabs account
        - Verify the API key has access to voice generation
        
        **🌐 Browser Issues:**
        - Use Chrome or Edge (best compatibility)
        - Check if audio is muted in browser/system
        - Try refreshing the page completely
        - Allow audio permissions if prompted
        
        **🎤 Voice ID Issues:**
        - Make sure the voice IDs match exactly from your account
        - Check if you have access to those specific voices
        - Try with a different voice ID
        
        **📱 Mobile Issues:**
        - Mobile browsers often block autoplay
        - User interaction might be required first
        - Try the manual play button
        
        **🔄 Cache Issues:**
        - Try hard refresh (Ctrl+F5 or Cmd+Shift+R)
        - Clear browser cache
        - Try in incognito/private mode
        """)
        
        # Reset function
        if st.button("🔄 Reset All Voice Settings", key="reset_voice_settings"):
            st.session_state.voice_played = False
            st.session_state.is_speaking = False
            st.success("✅ Voice settings reset! Try voice generation again.")
            st.rerun()

if __name__ == "__main__":
    main()
