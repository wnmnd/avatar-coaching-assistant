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

# Fixed Natural Voice with NO DOUBLE PLAYBACK
def natural_voice_component(text, voice_type="professional"):
    """Single voice playback - prevents doubles"""
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
        # Enhanced browser TTS with gender matching
        create_instant_browser_voice(text, voice_type, avatar_gender)

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
                        stability: 0.8,
                        similarity_boost: 0.9,
                        style: 0.8,
                        use_speaker_boost: true
                    }}
                }})
            }});
            
            if (response.ok) {{
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                // Play immediately
                audio.play().catch(e => {{
                    console.log('Autoplay blocked, using browser TTS fallback');
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
            utterance.rate = 0.9;
            utterance.pitch = {1.0 if gender == 'female' else 0.7};
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
    """Instant browser TTS with gender and personality matching"""
    
    clean_text = enhance_text_for_speech(text, voice_type)
    
    # Voice personality settings
    voice_settings = {
        'professional': {'rate': 0.9, 'pitch': 1.0},
        'confident': {'rate': 1.0, 'pitch': 0.9},
        'caring': {'rate': 0.85, 'pitch': 1.1},
        'wise': {'rate': 0.8, 'pitch': 0.8},
        'energetic': {'rate': 1.1, 'pitch': 1.2},
        'executive': {'rate': 0.95, 'pitch': 0.9}
    }
    
    settings = voice_settings.get(voice_type, voice_settings['professional'])
    
    # Adjust pitch for gender
    if gender == 'male':
        settings['pitch'] = max(0.5, settings['pitch'] - 0.3)  # Lower pitch for males
    else:
        settings['pitch'] = min(1.5, settings['pitch'] + 0.1)  # Slightly higher pitch for females
    
    voice_html = f"""
    <script>
    function playInstantBrowserVoice() {{
        if ('speechSynthesis' in window) {{
            speechSynthesis.cancel(); // Clear any previous speech
            
            const utterance = new SpeechSynthesisUtterance(`{clean_text}`);
            utterance.rate = {settings['rate']};
            utterance.pitch = {settings['pitch']};
            utterance.volume = 1.0;
            
            // Gender-based voice selection
            const voices = speechSynthesis.getVoices();
            let bestVoice;
            
            if ('{gender}' === 'male') {{
                // Prefer male voices
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.toLowerCase().includes('male') || 
                     v.name.toLowerCase().includes('david') ||
                     v.name.toLowerCase().includes('mark') ||
                     v.name.toLowerCase().includes('alex') ||
                     v.name.toLowerCase().includes('daniel'))
                ) || voices.find(v => v.lang.startsWith('en-') && v.localService);
            }} else {{
                // Prefer female voices  
                bestVoice = voices.find(v => 
                    v.lang.startsWith('en-') && 
                    (v.name.toLowerCase().includes('female') || 
                     v.name.toLowerCase().includes('samantha') ||
                     v.name.toLowerCase().includes('victoria') ||
                     v.name.toLowerCase().includes('susan') ||
                     v.name.toLowerCase().includes('karen'))
                ) || voices.find(v => v.lang.startsWith('en-') && v.localService);
            }}
            
            // Fallback to any English voice
            if (!bestVoice) {{
                bestVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
            }}
            
            if (bestVoice) {{
                utterance.voice = bestVoice;
                console.log('Selected voice:', bestVoice.name, 'for gender:', '{gender}');
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
    """Make text more natural and human-like for speech"""
    
    # Remove markdown and clean
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = text.replace('\n', ' ').strip()
    
    # Add natural speech patterns
    text = re.sub(r'([.!?])', r'\1 ', text)
    text = re.sub(r'([,:])', r'\1 ', text)
    
    # Personality-based enhancements
    if voice_type == 'caring':
        text = re.sub(r'\byou\b', 'you', text, flags=re.IGNORECASE)
    elif voice_type == 'energetic':
        text = re.sub(r'\bgreat\b', 'absolutely amazing', text, flags=re.IGNORECASE)
    elif voice_type == 'wise':
        text = re.sub(r'\bremember\b', 'keep in mind', text, flags=re.IGNORECASE)
    
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
        
        # WhatsApp voice input
        whatsapp_voice_note()
    
    with col2:
        # Chat interface
        chat_interface()
        
        # Text input form
        st.markdown("### ✍️ Type Your Message")
        
        with st.form("message_form", clear_on_submit=True):
            user_input = st.text_area(
                "What would you like to discuss?",
                height=100,
                placeholder="Ask about your goals, challenges, or anything related to success and wealth building..."
            )
            
            submitted = st.form_submit_button("Send Message", type="primary")
            
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
                    st.write(f"Testing voice for: {avatar_choice}")
                    
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
                    test_text = f"Hello, this is a voice test for {avatar_choice}, your {test_gender} avatar coach."
                    
                    # Test with actual gender
                    elevenlabs_key = setup_elevenlabs()
                    if elevenlabs_key and elevenlabs_key != "your_elevenlabs_api_key_here":
                        create_instant_elevenlabs_voice(test_text, elevenlabs_key, "professional", test_gender)
                    else:
                        create_instant_browser_voice(test_text, "professional", test_gender)
                
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
