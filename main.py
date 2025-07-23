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
   
    .avatar-speaking .avatar-emoji {
        animation: talking 0.5s ease-in-out infinite alternate;
        transform: scale(1.1);
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
    
    .voice-recording-container {
        background: linear-gradient(135deg, #fff8f0, #fff0e6);
        border: 2px solid #ff6b35;
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
    }
    
    .voice-ready-container {
        background: linear-gradient(135deg, #f0fff4, #e6ffed);
        border: 2px solid #4CAF50;
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
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
    if 'recording_state' not in st.session_state:
        st.session_state.recording_state = 'ready'

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
        </div>
        <div class="avatar-status">{status_text}</div>
    </div>
    """
   
    st.markdown(avatar_html, unsafe_allow_html=True)

# Enhanced Voice Recording with Auto-Send
def enhanced_voice_recording():
    """Enhanced voice recording system with automatic sending"""
    
    st.markdown("### 🎤 Voice Message (Auto-Send)")
    
    # Instructions
    st.info("**How to use voice recording:**\n1. Click 'Start Recording'\n2. Speak your message clearly\n3. Click 'Stop & Auto-Send' to send directly to your coach")
    
    # Voice recording interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Status display
        if st.session_state.recording_state == 'ready':
            st.markdown('<div class="voice-ready-container">🎤 Ready to record your voice message</div>', unsafe_allow_html=True)
        elif st.session_state.recording_state == 'recording':
            st.markdown('<div class="voice-recording-container">🔴 <strong>Recording...</strong> Speak now!</div>', unsafe_allow_html=True)
        elif st.session_state.recording_state == 'processing':
            st.markdown('<div class="voice-recording-container">⏳ Processing and auto-sending your message...</div>', unsafe_allow_html=True)
    
    with col2:
        # Control buttons
        if st.session_state.recording_state == 'ready':
            if st.button("🎤 Start Recording", type="primary", key="start_recording"):
                st.session_state.recording_state = 'recording'
                st.rerun()
        elif st.session_state.recording_state == 'recording':
            if st.button("⏹️ Stop & Auto-Send", type="secondary", key="stop_recording"):
                st.session_state.recording_state = 'processing'
                st.rerun()
    
    # Voice recording JavaScript for when recording is active
    if st.session_state.recording_state == 'recording':
        voice_html = """
        <div style="padding: 20px; text-align: center;">
            <div id="transcriptionDisplay" style="
                margin: 15px 0;
                padding: 15px;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                border: 2px solid #ff6b35;
                min-height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: #333;
            ">
                🎤 Listening...
            </div>
        </div>

        <script>
        let recognition = null;
        let finalTranscript = '';

        function startRecording() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'en-US';
                
                recognition.onstart = function() {
                    console.log('Voice recognition started');
                    document.getElementById('transcriptionDisplay').innerHTML = '🎤 <strong>Listening...</strong> Speak clearly!';
                };
                
                recognition.onresult = function(event) {
                    let interimTranscript = '';
                    finalTranscript = '';
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript + ' ';
                        } else {
                            interimTranscript += transcript;
                        }
                    }
                    
                    const displayText = (finalTranscript + interimTranscript).trim();
                    if (displayText) {
                        document.getElementById('transcriptionDisplay').innerHTML = 
                            '📝 <strong>Hearing:</strong> "' + displayText + '"';
                    }
                    
                    // Store in sessionStorage
                    if (finalTranscript.trim()) {
                        sessionStorage.setItem('voice_transcript', finalTranscript.trim());
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('Voice recognition error:', event.error);
                    let errorMsg = 'Error: ';
                    switch(event.error) {
                        case 'no-speech':
                            errorMsg += 'No speech detected. Please speak louder.';
                            break;
                        case 'not-allowed':
                            errorMsg += 'Microphone access denied. Please allow microphone access.';
                            break;
                        default:
                            errorMsg += event.error;
                    }
                    document.getElementById('transcriptionDisplay').innerHTML = '❌ ' + errorMsg;
                };
                
                recognition.onend = function() {
                    console.log('Voice recognition ended');
                };
                
                try {
                    recognition.start();
                } catch (error) {
                    console.error('Failed to start recognition:', error);
                    document.getElementById('transcriptionDisplay').innerHTML = 
                        '❌ Failed to start recording. Please check microphone permissions.';
                }
                
            } else {
                document.getElementById('transcriptionDisplay').innerHTML = 
                    '❌ Voice recognition not supported. Please use Chrome, Safari, or Edge browser.';
            }
        }
        
        // Start recording when page loads
        startRecording();
        </script>
        """
        st.components.v1.html(voice_html, height=150)
    
    # Process voice when user clicks stop and auto-send
    if st.session_state.recording_state == 'processing':
        # Check for transcript via JavaScript and auto-send
        auto_send_html = """
        <script>
        const transcript = sessionStorage.getItem('voice_transcript');
        if (transcript && transcript.trim()) {
            // Auto-send to Streamlit via URL parameters
            const url = new URL(window.location.href);
            url.searchParams.set('voice_auto_send', encodeURIComponent(transcript.trim()));
            url.searchParams.set('voice_timestamp', Date.now().toString());
            sessionStorage.removeItem('voice_transcript');
            window.location.href = url.toString();
        } else {
            // No transcript, redirect with error
            setTimeout(() => {
                const url = new URL(window.location.href);
                url.searchParams.set('voice_error', 'No speech detected');
                window.location.href = url.toString();
            }, 2000);
        }
        </script>
        """
        st.components.v1.html(auto_send_html, height=0)

# FIXED Mobile-Friendly Voice Component with DISTINCT Voices
def enhanced_natural_voice_component(text, voice_type="professional"):
    """FIXED voice playback with distinct personalities and mobile support"""
    if not text or st.session_state.get('voice_played', False):
        return
   
    st.session_state.voice_played = True
   
    # Get avatar gender for voice selection
    profile = st.session_state.user_profile
    avatar_choice = profile.get('avatar', 'sophia')
    avatar_configs = {
        'sophia': {'gender': 'female'},
        'marcus': {'gender': 'male'},
        'elena': {'gender': 'female'},
        'david': {'gender': 'male'},
        'maya': {'gender': 'female'},
        'james': {'gender': 'male'}
    }
    avatar_gender = avatar_configs.get(avatar_choice, {}).get('gender', 'female')
   
    # Enhanced text processing for distinct personalities
    clean_text = enhance_text_for_distinct_speech(text, voice_type)
   
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
            🎭 Your {voice_type} coach is speaking...
        </div>
       
        <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
            <!-- Manual play button for mobile and desktop -->
            <button id="playButton_{voice_id}" onclick="playVoice_{voice_id}()" style="
                background: linear-gradient(135deg, #8A2BE2, #9370DB);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 12px 20px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3);
                font-size: 14px;
                margin: 0 5px;
            ">
                🔊 Play Voice ({voice_type})
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
    let voiceUtterance_{voice_id} = null;
    let isPlaying_{voice_id} = false;
   
    function playVoice_{voice_id}() {{
        if ('speechSynthesis' in window) {{
            // Cancel any existing speech
            speechSynthesis.cancel();
           
            voiceUtterance_{voice_id} = new SpeechSynthesisUtterance(`{clean_text}`);
            isPlaying_{voice_id} = true;
            
            // DISTINCT voice settings for each personality and gender
            {get_voice_settings(voice_type, avatar_gender)}
           
            // Update UI for playing state
            document.getElementById('voiceMessage_{voice_id}').innerHTML = '🎤 Your {voice_type} coach is now speaking...';
            document.getElementById('playButton_{voice_id}').style.display = 'none';
            document.getElementById('stopButton_{voice_id}').style.display = 'inline-block';
            document.getElementById('voiceStatus_{voice_id}').style.display = 'block';
            document.getElementById('voiceStatus_{voice_id}').innerHTML = '🔊 Voice playing...';
           
            // ADVANCED voice selection with specific voice names
            const voices = speechSynthesis.getVoices();
            let bestVoice = selectBestVoice_{voice_id}(voices, '{avatar_gender}', '{voice_type}');
           
            if (bestVoice) {{
                voiceUtterance_{voice_id}.voice = bestVoice;
                console.log('Selected voice:', bestVoice.name, 'for', '{voice_type}', '{avatar_gender}');
            }}
           
            // Voice event handlers
            voiceUtterance_{voice_id}.onstart = function() {{
                console.log('Voice started playing');
                document.getElementById('voiceStatus_{voice_id}').innerHTML = '🎵 {voice_type} voice playing...';
            }};
           
            voiceUtterance_{voice_id}.onend = function() {{
                console.log('Voice finished playing');
                isPlaying_{voice_id} = false;
                document.getElementById('voiceMessage_{voice_id}').innerHTML = '✅ Voice message completed!';
                document.getElementById('playButton_{voice_id}').style.display = 'inline-block';
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
                document.getElementById('playButton_{voice_id}').style.display = 'inline-block';
                document.getElementById('stopButton_{voice_id}').style.display = 'none';
                document.getElementById('voiceStatus_{voice_id}').innerHTML = '❌ Playback error: ' + event.error;
            }};
           
            // Start speech
            speechSynthesis.speak(voiceUtterance_{voice_id});
            console.log('Voice started for {voice_type} {avatar_gender}');
        }} else {{
            document.getElementById('voiceMessage_{voice_id}').innerHTML = '❌ Voice not supported in this browser';
            document.getElementById('voiceStatus_{voice_id}').innerHTML = 'Please use Chrome, Safari, or Edge';
            document.getElementById('voiceStatus_{voice_id}').style.display = 'block';
        }}
    }}
   
    function stopVoice_{voice_id}() {{
        console.log('Stopping voice playback');
        if (speechSynthesis) {{
            speechSynthesis.cancel();
        }}
        isPlaying_{voice_id} = false;
       
        document.getElementById('voiceMessage_{voice_id}').innerHTML = '⏹️ Voice stopped';
        document.getElementById('playButton_{voice_id}').style.display = 'inline-block';
        document.getElementById('stopButton_{voice_id}').style.display = 'none';
        document.getElementById('voiceStatus_{voice_id}').innerHTML = '⏹️ Playback stopped';
       
        setTimeout(() => {{
            document.getElementById('voiceStatus_{voice_id}').style.display = 'none';
        }}, 2000);
    }}
    
    function selectBestVoice_{voice_id}(voices, gender, voiceType) {{
        console.log('Available voices:', voices.map(v => v.name));
        
        let bestVoice = null;
        
        if (gender === 'male') {{
            // SPECIFIC male voice selection
            if (voiceType === 'wise') {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.includes('Daniel') || v.name.includes('Arthur') || v.name.includes('Albert'))
                );
            }} else if (voiceType === 'confident' || voiceType === 'executive') {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.includes('David') || v.name.includes('Mark') || v.name.includes('Aaron'))
                );
            }} else if (voiceType === 'energetic') {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.includes('Fred') || v.name.includes('Bruce') || v.name.includes('Junior'))
                );
            }}
            
            // Fallback to any clear male voice
            if (!bestVoice) {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.toLowerCase().includes('male') || 
                     v.name.includes('David') || 
                     v.name.includes('Mark') ||
                     v.name.includes('Alex') ||
                     v.voiceURI.includes('male'))
                );
            }}
        }} else {{
            // SPECIFIC female voice selection
            if (voiceType === 'caring') {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.includes('Samantha') || v.name.includes('Susan') || v.name.includes('Moira'))
                );
            }} else if (voiceType === 'energetic') {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.includes('Victoria') || v.name.includes('Kate') || v.name.includes('Princess'))
                );
            }} else if (voiceType === 'professional') {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.includes('Alex') || v.name.includes('Allison') || v.name.includes('Ava'))
                );
            }}
            
            // Fallback to any clear female voice
            if (!bestVoice) {{
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.toLowerCase().includes('female') || 
                     v.name.includes('Samantha') || 
                     v.name.includes('Susan') ||
                     v.name.includes('Victoria') ||
                     v.voiceURI.includes('female'))
                );
            }}
        }}
        
        // Final fallback to any English voice
        if (!bestVoice) {{
            bestVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
        }}
        
        console.log('Selected voice for', gender, voiceType, ':', bestVoice?.name || 'default');
        return bestVoice;
    }}
   
    // Auto-play attempt after voices are loaded
    if (speechSynthesis.getVoices().length > 0) {{
        setTimeout(() => {{
            // Try auto-play for desktop, require tap for mobile
            const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            if (!isMobile) {{
                playVoice_{voice_id}();
            }}
        }}, 500);
    }} else {{
        speechSynthesis.onvoiceschanged = function() {{
            setTimeout(() => {{
                const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                if (!isMobile) {{
                    playVoice_{voice_id}();
                }}
            }}, 500);
        }};
    }}
    </script>
    """
   
    st.components.v1.html(voice_html, height=180)

def get_voice_settings(voice_type, gender):
    """Generate JavaScript voice settings for distinct personalities"""
    
    # Base settings for each personality type
    if voice_type == 'caring':
        rate = "0.75"
        pitch = "1.4" if gender == 'female' else "0.65"
        volume = "0.9"
    elif voice_type == 'professional':
        rate = "0.85"
        pitch = "1.1" if gender == 'female' else "0.7"
        volume = "1.0"
    elif voice_type == 'energetic':
        # FIXED: Moderate but still fast, more energetic for males
        rate = "1.15" if gender == 'female' else "1.25"  # Faster for energetic males
        pitch = "1.5" if gender == 'female' else "0.8"   # Higher pitch for energetic males
        volume = "1.0"
    elif voice_type == 'wise':
        rate = "0.65"
        pitch = "0.9" if gender == 'female' else "0.5"
        volume = "0.95"
    elif voice_type == 'confident':
        rate = "1.0"
        pitch = "1.0" if gender == 'female' else "0.6"
        volume = "1.0"
    elif voice_type == 'executive':
        rate = "0.9"
        pitch = "0.95" if gender == 'female' else "0.65"
        volume = "1.0"
    else:
        rate = "0.9"
        pitch = "1.0" if gender == 'female' else "0.7"
        volume = "1.0"
    
    return f"""
            voiceUtterance_{voice_type}_id.rate = {rate};
            voiceUtterance_{voice_type}_id.pitch = {pitch};
            voiceUtterance_{voice_type}_id.volume = {volume};
    """.replace(f'{voice_type}_id', f'{int(time.time() * 1000)}')

def enhance_text_for_distinct_speech(text, voice_type):
    """Enhance text to make each personality VERY distinct"""
   
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
        text = text.replace(' can ', ' absolutely can ')
        text = text.replace(' will ', ' will surely ')
        text = text.replace(' are ', ' are truly ')
       
    elif voice_type == 'energetic':
        # Excited, motivational speech with controlled speed
        text = re.sub(r'\bgreat\b', 'absolutely AMAZING', text, flags=re.IGNORECASE)
        text = re.sub(r'\bgood\b', 'fantastic', text, flags=re.IGNORECASE)
        text = re.sub(r'\.', '! This is exciting!', text, count=1)
        text = re.sub(r'\byes\b', 'YES! Absolutely!', text, flags=re.IGNORECASE)
        text = text.replace(' can ', ' can totally ')
        text = text.replace(' will ', ' will definitely ')
        text += ' I am SO pumped for your success!'
       
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
        text = re.sub(r'\.', '. I am absolutely certain of this.', text, count=1)
        text = re.sub(r'\bI believe\b', 'I KNOW', text, flags=re.IGNORECASE)
        text = text.replace(' might ', ' WILL ')
        text = text.replace(' could ', ' WILL ')
        text = 'Listen up! ' + text
       
    elif voice_type == 'executive':
        # Authoritative, commanding, leadership speech
        text = re.sub(r'\.', '. This is exactly what successful leaders do.', text, count=1)
        text = re.sub(r'\bwe should\b', 'we MUST execute', text, flags=re.IGNORECASE)
        text = text.replace(' need to ', ' must immediately ')
        text = 'Here is the strategic approach: ' + text
   
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
        st.header("Your Coach Settings")
       
        # Basic info
        name = st.text_input("Your Name", value=st.session_state.user_profile.get('name', ''))
        goals = st.text_area("Your Goals", value=st.session_state.user_profile.get('goals', ''))
       
        # Enhanced avatar choices
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
        st.subheader("Voice Style")
        voice_type = st.selectbox(
            "Coach Personality",
            ["caring", "professional", "energetic", "wise"],
            index=["caring", "professional", "energetic", "wise"].index(
                st.session_state.user_profile.get('voice_type', 'caring')
            ),
            format_func=lambda x: {
                'caring': 'Caring & Supportive',
                'professional': 'Professional & Direct',
                'energetic': 'Energetic & Motivating',
                'wise': 'Wise & Thoughtful'
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
        <h1>Avatar Success Coach</h1>
        <p>Your AI-powered success mentor with FIXED voice auto-send</p>
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
   
    # Handle auto-send voice message from URL parameters - FIXED
    if 'voice_auto_send' in st.query_params and 'voice_timestamp' in st.query_params:
        voice_message = st.query_params.get('voice_auto_send', '').strip()
        
        # Clear parameters immediately
        del st.query_params['voice_auto_send']
        del st.query_params['voice_timestamp']
        
        if voice_message:
            # Reset recording state
            st.session_state.recording_state = 'ready'
            
            # Add to chat automatically
            st.session_state.voice_played = False
            st.session_state.chat_history.append({
                'role': 'user',
                'content': voice_message,
                'timestamp': datetime.now()
            })
            
            # Get coach response automatically
            with st.spinner("Your coach is responding to your voice message..."):
                coach_response = get_coach_response(voice_message, st.session_state.chat_history)
            
            st.session_state.chat_history.append({
                'role': 'coach',
                'content': coach_response,
                'timestamp': datetime.now()
            })
            
            st.session_state.is_speaking = True
            st.success(f"🎤 Voice message auto-sent: \"{voice_message}\"")
            st.rerun()
    
    # Handle voice error
    if 'voice_error' in st.query_params:
        st.session_state.recording_state = 'ready'
        del st.query_params['voice_error']
        st.error("❌ No speech detected. Please try recording again.")
        st.rerun()
   
    # Main layout
    col1, col2 = st.columns([1, 2])
   
    with col1:
        # Avatar display
        avatar_component(st.session_state.is_speaking)
       
        # Play voice for new coach messages with FIXED voice system
        if (st.session_state.chat_history and
            st.session_state.chat_history[-1]['role'] == 'coach' and
            st.session_state.is_speaking and
            not st.session_state.voice_played):
           
            latest_response = st.session_state.chat_history[-1]['content']
            voice_type = st.session_state.user_profile.get('voice_type', 'professional')
            enhanced_natural_voice_component(latest_response, voice_type)
       
        # Reset speaking state
        if st.session_state.is_speaking:
            st.session_state.is_speaking = False
   
    with col2:
        # Chat interface
        chat_interface()
       
        # Text input form
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
                # Reset voice flag
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
       
        # Enhanced voice recording with auto-send - FIXED
        enhanced_voice_recording()
       
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.is_speaking = False
            st.session_state.voice_played = False
            st.session_state.recording_state = 'ready'
            st.rerun()

if __name__ == "__main__":
    main()
