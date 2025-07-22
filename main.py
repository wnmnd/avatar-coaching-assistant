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
    }
    
    .avatar-video {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(138, 43, 226, 0.4);
        border: 3px solid #8A2BE2;
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
    
    /* WhatsApp Voice Note Styling */
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
    if 'avatar_video_url' not in st.session_state:
        st.session_state.avatar_video_url = None

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
    """Setup HeyGen API for real avatars"""
    return st.secrets.get("HEYGEN_API_KEY") or os.getenv("HEYGEN_API_KEY")

def setup_elevenlabs():
    """Setup ElevenLabs for natural voice"""
    return st.secrets.get("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY")

def get_available_heygen_avatars(api_key):
    """Fetch current available HeyGen avatars"""
    try:
        url = "https://api.heygen.com/v2/avatars"
        headers = {
            "Accept": "application/json",
            "X-API-KEY": api_key
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            avatars = data.get("data", {}).get("avatars", [])
            
            # Filter for available avatars and separate by gender
            female_avatars = []
            male_avatars = []
            
            for avatar in avatars:
                if avatar.get("gender") == "female":
                    female_avatars.append(avatar)
                elif avatar.get("gender") == "male":
                    male_avatars.append(avatar)
            
            return {
                "female": female_avatars[:3],  # Get first 3 female
                "male": male_avatars[:3]       # Get first 3 male
            }
        else:
            st.error(f"❌ Failed to fetch avatars: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error fetching avatars: {str(e)}")
        return None

# HeyGen Avatar Integration  
def generate_avatar_video(text, avatar_choice, debug_mode=False):
    """Generate real talking avatar video using HeyGen with dynamic avatar selection"""
    heygen_key = setup_heygen()
    if not heygen_key or heygen_key == "your_heygen_api_key_here":
        if debug_mode:
            st.warning("⚠️ HeyGen API key not set. Using emoji avatar.")
        return None
    
    try:
        # First, get available avatars (quiet mode unless debug)
        if debug_mode:
            st.info("📋 Fetching available avatars...")
        
        available_avatars = get_available_heygen_avatars(heygen_key)
        
        if not available_avatars:
            if debug_mode:
                st.error("❌ Could not fetch available avatars")
            return None
        
        # Map our avatar choices to available avatars
        avatar_mapping = {
            'sophia': None,
            'marcus': None,
            'elena': None,
            'david': None,
            'maya': None,
            'james': None
        }
        
        # Assign available avatars to our choices
        female_avatars = available_avatars.get("female", [])
        male_avatars = available_avatars.get("male", [])
        
        if len(female_avatars) >= 3:
            avatar_mapping['sophia'] = female_avatars[0]
            avatar_mapping['elena'] = female_avatars[1]
            avatar_mapping['maya'] = female_avatars[2]
        
        if len(male_avatars) >= 3:
            avatar_mapping['marcus'] = male_avatars[0]
            avatar_mapping['david'] = male_avatars[1]
            avatar_mapping['james'] = male_avatars[2]
        
        # Get the selected avatar
        selected_avatar = avatar_mapping.get(avatar_choice)
        if not selected_avatar:
            # Fallback to first available avatar
            all_avatars = female_avatars + male_avatars
            if all_avatars:
                selected_avatar = all_avatars[0]
            else:
                if debug_mode:
                    st.error("❌ No avatars available")
                return None
        
        avatar_id = selected_avatar.get("avatar_id")
        avatar_name = selected_avatar.get("avatar_name", "Unknown")
        
        if debug_mode:
            st.success(f"✅ Using avatar: {avatar_name} (ID: {avatar_id})")
        
        # Get available voices (quiet unless debug)
        voices_url = "https://api.heygen.com/v2/voices"
        voices_response = requests.get(voices_url, headers={"Accept": "application/json", "X-API-KEY": heygen_key})
        
        voice_id = "1bd001e7e50f421d891986aad5158bc8"  # Default voice
        if voices_response.status_code == 200:
            voices_data = voices_response.json()
            voices = voices_data.get("data", {}).get("voices", [])
            if voices:
                # Try to match gender
                avatar_gender = selected_avatar.get("gender", "female")
                matching_voices = [v for v in voices if v.get("gender", "").lower() == avatar_gender.lower()]
                if matching_voices:
                    voice_id = matching_voices[0].get("voice_id", voice_id)
        
        # Clean and limit text input
        clean_text = text.strip()[:300]  # HeyGen limit
        clean_text = re.sub(r'[^\w\s\.\,\!\?\;\:\-]', '', clean_text)  # Clean special chars
        if not clean_text:
            clean_text = "Hello, how can I help you today?"
        
        if debug_mode:
            st.write(f"📝 Text: {clean_text}")
        
        # HeyGen API endpoint
        url = "https://api.heygen.com/v2/video/generate"
        headers = {
            "X-API-KEY": heygen_key,
            "Content-Type": "application/json"
        }
        
        # HeyGen request payload with current avatar (lower resolution for free plans)
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id
                },
                "voice": {
                    "type": "text",
                    "input_text": clean_text,
                    "voice_id": voice_id,
                    "speed": 1.0
                }
            }],
            "dimension": {
                "width": 256,  # Lower resolution for free/basic plans
                "height": 256
            },
            "aspect_ratio": "1:1"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if debug_mode:
            st.write(f"📡 HeyGen API Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if debug_mode:
                st.write(f"📋 Response data: {result}")
            
            video_id = result.get("data", {}).get("video_id")
            if video_id:
                if debug_mode:
                    st.success(f"✅ Video ID received: {video_id}")
                return poll_heygen_video_status(video_id, heygen_key, debug_mode)
            else:
                if debug_mode:
                    st.error("❌ No video ID in response")
                return None
        else:
            if debug_mode:
                try:
                    error_details = response.json()
                except:
                    error_details = response.text
                
                st.error(f"❌ HeyGen API Error {response.status_code}: {error_details}")
                
                # Provide helpful error messages
                if response.status_code == 401:
                    st.error("🔑 Authentication failed. Please check your HeyGen API key.")
                elif response.status_code == 402:
                    st.error("💳 Insufficient credits. Please check your HeyGen account balance.")
                elif response.status_code == 429:
                    st.error("⏰ Rate limit exceeded. Please wait and try again.")
            
            return None
        
    except Exception as e:
        if debug_mode:
            st.error(f"❌ Avatar generation error: {str(e)}")
        return None

def poll_heygen_video_status(video_id, api_key, debug_mode=False, max_attempts=40):
    """Poll HeyGen for video completion with longer timeout"""
    headers = {"X-API-KEY": api_key}
    
    if debug_mode:
        progress_placeholder = st.empty()
        st.write(f"🔄 **Polling video status for ID**: {video_id}")
    
    for attempt in range(max_attempts):
        try:
            # HeyGen status endpoint
            response = requests.get(
                f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
                headers=headers,
                timeout=15
            )
            
            if debug_mode:
                progress_placeholder.info(f"🎬 Generating avatar video... {attempt + 1}/{max_attempts} (waiting for completion)")
            
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {})
                status = data.get("status", "")
                
                if debug_mode:
                    st.write(f"📊 **Attempt {attempt + 1}**: Status = `{status}`")
                
                if status == "completed":
                    video_url = data.get("video_url")
                    if video_url:
                        if debug_mode:
                            progress_placeholder.success("✅ Avatar video ready!")
                            st.write(f"🎥 **Video URL**: {video_url}")
                        return video_url
                    else:
                        if debug_mode:
                            st.error("❌ No video URL in completed response")
                            st.write(f"📋 **Full response**: {data}")
                        return None
                elif status == "failed":
                    error_info = data.get("error", {})
                    error_code = error_info.get("code", "Unknown")
                    error_msg = error_info.get("message", "Unknown error")
                    
                    if debug_mode:
                        progress_placeholder.error(f"❌ Video generation failed: {error_msg}")
                        st.write(f"🚨 **Error Code**: {error_code}")
                        st.write(f"📋 **Full error data**: {error_info}")
                        
                        # Provide specific help for common errors
                        if "RESOLUTION_NOT_ALLOWED" in error_code:
                            st.info("💡 Try upgrading your HeyGen plan for higher resolution videos")
                        elif "AVATAR_NOT_ALLOWED" in error_code:
                            st.info("💡 This avatar requires a higher plan subscription")
                        elif "CREDIT" in error_code.upper():
                            st.info("💡 Please check your HeyGen account credits")
                    
                    return None
                elif status in ["pending", "processing", "waiting"]:
                    if debug_mode and attempt % 5 == 0:  # Show progress every 5 attempts
                        st.write(f"⏳ **Still processing** (attempt {attempt + 1}/{max_attempts})...")
                    time.sleep(5)  # Wait 5 seconds (increased from 3)
                    continue
                else:
                    if debug_mode:
                        st.write(f"🔄 **Unknown status**: `{status}` - continuing...")
                    time.sleep(5)
            else:
                if debug_mode:
                    st.error(f"❌ Status check failed: {response.status_code}")
                    st.write(f"📋 **Response**: {response.text}")
                time.sleep(5)
                
        except Exception as e:
            if debug_mode:
                st.error(f"❌ Polling error: {str(e)}")
            time.sleep(5)
    
    if debug_mode:
        progress_placeholder.error(f"⏰ Avatar generation timed out after {max_attempts} attempts ({max_attempts * 5} seconds)")
        st.write(f"🔗 **Try checking video status manually**: https://app.heygen.com/")
    return None

# Enhanced Avatar Component with HeyGen
def avatar_component(is_speaking=False, latest_response=""):
    """Display real talking avatar or fallback emoji"""
    
    # Get avatar selection from profile
    profile = st.session_state.user_profile
    avatar_choice = profile.get('avatar', 'sophia')
    
    # Debug info to see what's happening
    if is_speaking:
        st.write(f"🔍 **Debug**: is_speaking={is_speaking}, has_response={bool(latest_response)}, heygen_key={bool(setup_heygen())}")
    
    # Try to generate real avatar if speaking and we have response
    if is_speaking and latest_response and setup_heygen():
        st.info(f"🎬 Attempting to create {avatar_choice} avatar video...")
        
        # Always show generation details for now
        with st.expander("🔍 Avatar Generation Log", expanded=True):
            video_url = generate_avatar_video(latest_response, avatar_choice, debug_mode=True)
            
        if video_url:
            # Display real talking avatar
            avatar_html = f"""
            <div class="avatar-container">
                <div class="avatar-video">
                    <video width="350" height="350" autoplay muted controls style="border-radius: 15px;">
                        <source src="{video_url}" type="video/mp4">
                        Your browser does not support video.
                    </video>
                </div>
                <div class="avatar-status">
                    ✅ Real HeyGen avatar speaking!
                </div>
            </div>
            """
            st.markdown(avatar_html, unsafe_allow_html=True)
            st.session_state.is_speaking = False  # Reset speaking state
            return
        else:
            st.error("❌ **DETAILED ERROR**: Avatar generation returned None - check logs above")
    elif is_speaking and latest_response:
        st.warning("⚠️ HeyGen API key not configured - using emoji fallback")
    elif is_speaking:
        st.warning("⚠️ No response text available for avatar generation")
    
    # If we get here, show emoji fallback message
    if is_speaking:
        st.warning("⚠️ Avatar generation failed, using emoji fallback")
    
    # Fallback to emoji avatar
    emoji_mapping = {
        'sophia': '👩‍💼',
        'marcus': '👨‍💼', 
        'elena': '👩‍⚕️',
        'david': '👨‍🎓',
        'maya': '👩‍🏫',
        'james': '👨‍💻'
    }
    
    avatar_emoji = emoji_mapping.get(avatar_choice, '👩‍💼')
    avatar_class = "avatar speaking" if is_speaking else "avatar"
    
    status_text = "🎤 Speaking..." if is_speaking else "💭 Ready to help..."
    
    avatar_html = f"""
    <div class="avatar-container">
        <div class="{avatar_class}">
            {avatar_emoji}
        </div>
        <div class="avatar-status">
            {status_text}
        </div>
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
        # This would integrate with the JavaScript voice input
        st.info("Voice input integration ready. Hold the microphone button to record.")

# Enhanced Natural Text-to-Speech
def natural_voice_component(text):
    """Enhanced natural voice with ElevenLabs or improved browser TTS"""
    if not text:
        return
    
    elevenlabs_key = setup_elevenlabs()
    voice_type = st.session_state.user_profile.get('voice_type', 'caring')
    
    if elevenlabs_key:
        # Use ElevenLabs for premium natural voice
        create_elevenlabs_voice(text, elevenlabs_key, voice_type)
    else:
        # Enhanced browser TTS
        create_enhanced_browser_voice(text, voice_type)

def create_elevenlabs_voice(text, api_key, avatar_choice):
    """Create ultra-natural voice using ElevenLabs with proper male/female voices"""
    
    # Updated ElevenLabs voice IDs for each avatar
    avatar_voices = {
        'sophia': {
            'voice_id': 'EXAVITQu4vr4xnSDxMaL',  # Bella - Professional Female
            'name': 'Sophia (Professional Female)'
        },
        'marcus': {
            'voice_id': 'onwK4e9ZLuTAKqWW03F9',  # Daniel - Deep Male
            'name': 'Marcus (Professional Male)'
        },
        'elena': {
            'voice_id': '21m00Tcm4TlvDq8ikWAM',  # Rachel - Warm Female  
            'name': 'Elena (Caring Female)'
        },
        'david': {
            'voice_id': 'TxGEqnHWrfWFTfGW9XjX',  # Josh - Wise Male
            'name': 'David (Wise Male)'
        },
        'maya': {
            'voice_id': 'AZnzlk1XvdvUeBnXmlld',  # Domi - Energetic Female
            'name': 'Maya (Energetic Female)'
        },
        'james': {
            'voice_id': 'VR6AewLTigWG4xSOukaG',  # Arnold - Executive Male
            'name': 'James (Executive Male)'
        }
    }
    
    voice_config = avatar_voices.get(avatar_choice, avatar_voices['sophia'])
    voice_id = voice_config['voice_id']
    voice_name = voice_config['name']
    
    # Enhance text for more natural speech
    enhanced_text = enhance_text_for_speech(text, avatar_choice)
    
    tts_html = f"""
    <script>
    async function speakWithElevenLabs() {{
        try {{
            document.getElementById('speakButton').innerHTML = '🔄 Generating {voice_name}...';
            
            const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/{voice_id}', {{
                method: 'POST',
                headers: {{
                    'Accept': 'audio/mpeg',
                    'Content-Type': 'application/json',
                    'xi-api-key': '{api_key}'
                }},
                body: JSON.stringify({{
                    text: `{enhanced_text}`,
                    model_id: 'eleven_monolingual_v1',
                    voice_settings: {{
                        stability: 0.8,
                        similarity_boost: 0.9,
                        style: 0.7,
                        use_speaker_boost: true
                    }}
                }})
            }});
            
            if (response.ok) {{
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                document.getElementById('speakButton').innerHTML = '🔇 Stop {voice_name}';
                document.getElementById('speakButton').style.background = 'linear-gradient(45deg, #ff4757, #ff3742)';
                
                audio.play();
                
                audio.onended = function() {{
                    document.getElementById('speakButton').innerHTML = '🔊 Play {voice_name}';
                    document.getElementById('speakButton').style.background = 'linear-gradient(45deg, #9370DB, #8A2BE2)';
                }};
                
                document.getElementById('speakButton').onclick = function() {{
                    audio.pause();
                    audio.currentTime = 0;
                    document.getElementById('speakButton').innerHTML = '🔊 Play {voice_name}';
                    document.getElementById('speakButton').style.background = 'linear-gradient(45deg, #9370DB, #8A2BE2)';
                    document.getElementById('speakButton').onclick = speakWithElevenLabs;
                }};
                
            }} else {{
                throw new Error('ElevenLabs API error: ' + response.status);
            }}
        }} catch (error) {{
            console.error('ElevenLabs error:', error);
            document.getElementById('speakButton').innerHTML = '🔊 Use Enhanced Voice (Fallback)';
            enhancedBrowserVoice(); // Fallback
        }}
    }}
    
    // Auto-play if enabled
    setTimeout(speakWithElevenLabs, 1000);
    </script>
    
    <div style="text-align: center; margin: 15px 0;">
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
            🔊 Play {voice_name}
        </button>
    </div>
    """
    
    st.components.v1.html(tts_html, height=80)

def create_enhanced_browser_voice(text, avatar_choice):
    """Enhanced browser TTS with proper male/female voice selection"""
    
    enhanced_text = enhance_text_for_speech(text, avatar_choice)
    voice_speed = st.session_state.user_profile.get('voice_speed', 0.9)
    voice_pitch = st.session_state.user_profile.get('voice_pitch', 1.0)
    
    # Avatar-specific voice preferences
    avatar_voice_prefs = {
        'sophia': {
            'gender': 'female',
            'type': 'professional',
            'pitch': 1.0,
            'name': 'Professional Female Voice'
        },
        'marcus': {
            'gender': 'male', 
            'type': 'professional',
            'pitch': 0.8,
            'name': 'Professional Male Voice'
        },
        'elena': {
            'gender': 'female',
            'type': 'caring',
            'pitch': 1.1,
            'name': 'Caring Female Voice'
        },
        'david': {
            'gender': 'male',
            'type': 'wise', 
            'pitch': 0.7,
            'name': 'Wise Male Voice'
        },
        'maya': {
            'gender': 'female',
            'type': 'energetic',
            'pitch': 1.2,
            'name': 'Energetic Female Voice'
        },
        'james': {
            'gender': 'male',
            'type': 'executive',
            'pitch': 0.9,
            'name': 'Executive Male Voice'
        }
    }
    
    voice_pref = avatar_voice_prefs.get(avatar_choice, avatar_voice_prefs['sophia'])
    adjusted_pitch = voice_pref['pitch']
    voice_name = voice_pref['name']
    
    tts_html = f"""
    <script>
    function enhancedBrowserVoice() {{
        if ('speechSynthesis' in window) {{
            speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(`{enhanced_text}`);
            utterance.rate = {voice_speed * 0.95};
            utterance.pitch = {adjusted_pitch};
            utterance.volume = 1.0;
            
            let voices = speechSynthesis.getVoices();
            if (voices.length === 0) {{
                setTimeout(() => {{
                    voices = speechSynthesis.getVoices();
                    selectVoiceForAvatar();
                }}, 100);
            }} else {{
                selectVoiceForAvatar();
            }}
            
            function selectVoiceForAvatar() {{
                let selectedVoice = null;
                const gender = '{voice_pref["gender"]}';
                const type = '{voice_pref["type"]}';
                
                console.log('Available voices:', voices.map(v => v.name + ' (' + v.gender + ')'));
                
                if (gender === 'female') {{
                    // Find best female voice
                    selectedVoice = voices.find(voice => 
                        voice.lang.startsWith('en-') && 
                        (voice.name.toLowerCase().includes('female') ||
                         voice.name.toLowerCase().includes('woman') ||
                         voice.name.includes('Samantha') ||
                         voice.name.includes('Karen') ||
                         voice.name.includes('Susan') ||
                         voice.name.includes('Victoria') ||
                         voice.name.includes('Zira'))
                    );
                    
                    // Fallback for female
                    if (!selectedVoice) {{
                        selectedVoice = voices.find(voice => 
                            voice.lang.startsWith('en-') && 
                            !voice.name.toLowerCase().includes('male') &&
                            !voice.name.toLowerCase().includes('man')
                        );
                    }}
                    
                }} else if (gender === 'male') {{
                    // Find best male voice
                    selectedVoice = voices.find(voice => 
                        voice.lang.startsWith('en-') && 
                        (voice.name.toLowerCase().includes('male') ||
                         voice.name.toLowerCase().includes('man') ||
                         voice.name.includes('David') ||
                         voice.name.includes('Mark') ||
                         voice.name.includes('Daniel') ||
                         voice.name.includes('Alex') ||
                         voice.name.includes('Bruce') ||
                         voice.name.includes('James'))
                    );
                    
                    // Fallback for male - look for deeper voices
                    if (!selectedVoice) {{
                        selectedVoice = voices.find(voice => 
                            voice.lang.startsWith('en-') && 
                            (voice.name.includes('Google') || voice.localService === true)
                        );
                    }}
                }}
                
                // Final fallback
                if (!selectedVoice) {{
                    selectedVoice = voices.find(v => v.lang.startsWith('en-')) || voices[0];
                }}
                
                if (selectedVoice) {{
                    utterance.voice = selectedVoice;
                    console.log('Selected voice:', selectedVoice.name, 'for', gender, type);
                }}
                
                utterance.onstart = function() {{
                    document.getElementById('speakButton').innerHTML = '🔇 Stop {voice_name}';
                }};
                
                utterance.onend = function() {{
                    document.getElementById('speakButton').innerHTML = '🔊 Play {voice_name}';
                }};
                
                utterance.onerror = function(event) {{
                    console.error('Speech error:', event.error);
                    document.getElementById('speakButton').innerHTML = '🔊 Try Again';
                }};
                
                speechSynthesis.speak(utterance);
            }}
        }}
    }}
    
    // Auto-play
    setTimeout(enhancedBrowserVoice, 1000);
    </script>
    
    <div style="text-align: center; margin: 15px 0;">
        <button id="speakButton" onclick="enhancedBrowserVoice()" style="
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
            🔊 Play {voice_name}
        </button>
    </div>
    """
    
    st.components.v1.html(tts_html, height=80)

def enhance_text_for_speech(text, voice_type):
    """Make text more natural and human-like for speech"""
    
    # Remove markdown and clean
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = text.replace('\n', ' ').strip()
    
    # Add natural speech patterns
    text = re.sub(r'([.!?])', r'\1 ', text)  # Natural pauses
    text = re.sub(r'([,:])', r'\1 ', text)   # Slight pauses
    
    # Personality-based enhancements
    if voice_type == 'caring':
        text = re.sub(r'\byou\b', 'you', text, flags=re.IGNORECASE)
        text = re.sub(r'!', '!', text)  # Keep excitement but not overwhelming
    elif voice_type == 'energetic':
        text = re.sub(r'\bgreat\b', 'absolutely amazing', text, flags=re.IGNORECASE)
        text = re.sub(r'\bgood\b', 'fantastic', text, flags=re.IGNORECASE)
    elif voice_type == 'wise':
        text = re.sub(r'\bremember\b', 'keep in mind', text, flags=re.IGNORECASE)
        text = text.replace('.', '. Take a moment to consider this.')[:1] + text[1:]  # Add wisdom pause
    
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

# Enhanced user profile sidebar with new D-ID avatars
def user_profile_sidebar():
    with st.sidebar:
        st.header("👤 Your Coach Settings")
        
        # Basic info
        name = st.text_input("Your Name", value=st.session_state.user_profile.get('name', ''))
        goals = st.text_area("Your Goals", value=st.session_state.user_profile.get('goals', ''))
        
        # Enhanced avatar choices (6 realistic options)
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
                'voice_speed': 0.9,  # Default natural speed
                'voice_pitch': 1.0   # Default pitch
            }
            st.success("✅ Settings saved!")
            st.rerun()

# Main app
def main():
    load_css()
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Avatar Success Coach</h1>
        <p>Your AI-powered success mentor with realistic HeyGen talking avatars</p>
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
        # Real avatar display
        latest_response = ""
        if st.session_state.chat_history:
            latest_msg = st.session_state.chat_history[-1]
            if latest_msg['role'] == 'coach':
                latest_response = latest_msg['content']
        
        avatar_component(st.session_state.is_speaking, latest_response)
        
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
            st.rerun()
        
        # Show latest response with natural voice
        if st.session_state.chat_history:
            latest_message = st.session_state.chat_history[-1]
            if latest_message['role'] == 'coach':
                st.markdown("### 🔊 Coach Response")
                st.info(latest_message['content'])
                natural_voice_component(latest_message['content'])
        
        # Debug and test section - MOVED TO BOTTOM
        st.markdown("---")
        st.markdown("### 🔧 Debug & API Tests")
        
        with st.expander("Debug Tools", expanded=False):
            col_debug1, col_debug2 = st.columns(2)
            
            with col_debug1:
                st.subheader("🤖 HeyGen Avatar Test")
                if st.button("🎬 Test HeyGen API"):
                    heygen_key = setup_heygen()
                    if heygen_key and heygen_key != "your_heygen_api_key_here":
                        st.info("Testing HeyGen with current available avatars...")
                        test_video = generate_avatar_video("Hello, this is a test message!", 'sophia', debug_mode=True)
                        if test_video:
                            st.success("✅ HeyGen API working!")
                            st.video(test_video)
                        else:
                            st.error("❌ HeyGen API test failed")
                    else:
                        st.error("❌ HeyGen API key not set")
            
            with col_debug2:
                st.subheader("🎤 Voice Test")
                if st.button("🔊 Test Voice System"):
                    avatar_choice = st.session_state.user_profile.get('avatar', 'sophia')
                    st.write(f"Testing voice for: {avatar_choice}")
                    natural_voice_component("Hello, this is a voice test for the avatar coaching system.")
                
                st.subheader("📋 Available Avatars")
                if st.button("👀 Show Available Avatars"):
                    heygen_key = setup_heygen()
                    if heygen_key:
                        available_avatars = get_available_heygen_avatars(heygen_key)
                        if available_avatars:
                            st.write("**Female Avatars:**")
                            for avatar in available_avatars.get("female", []):
                                st.write(f"- {avatar.get('avatar_name')} (ID: {avatar.get('avatar_id')})")
                            
                            st.write("**Male Avatars:**")
                            for avatar in available_avatars.get("male", []):
                                st.write(f"- {avatar.get('avatar_name')} (ID: {avatar.get('avatar_id')})")
                        else:
                            st.error("❌ Could not fetch avatars")
                    else:
                        st.error("❌ HeyGen API key not set")
            
            # Show current settings
            st.subheader("⚙️ Current Settings")
            st.json({
                'avatar_choice': st.session_state.user_profile.get('avatar', 'none'),
                'heygen_key_set': bool(setup_heygen() and setup_heygen() != "your_heygen_api_key_here"),
                'elevenlabs_key_set': bool(setup_elevenlabs() and setup_elevenlabs() != "your_elevenlabs_api_key_here"),
                'gemini_key_set': bool(st.secrets.get("GEMINI_API_KEY")),
                'chat_history_length': len(st.session_state.chat_history),
                'is_speaking': st.session_state.is_speaking
            })

if __name__ == "__main__":
    main()
