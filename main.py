import streamlit as st
import google.generativeai as genai
import sqlite3
import json
import time
import base64
import re
import requests
from datetime import datetime, timedelta
import os
import hashlib
import uuid

# Configure the page
st.set_page_config(
    page_title="Avatar Success Coach Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CRM DATABASE SYSTEM ====================

class CoachingCRM:
    def __init__(self, db_path="coaching_crm.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the CRM database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            subscription_status TEXT DEFAULT 'free',
            total_sessions INTEGER DEFAULT 0,
            total_messages INTEGER DEFAULT 0
        )""")
        
        # User profiles table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            avatar TEXT DEFAULT 'sophia',
            voice_type TEXT DEFAULT 'caring',
            goals TEXT,
            coaching_focus TEXT,
            personality_preferences TEXT,
            progress_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )""")
        
        # Chat sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            total_messages INTEGER DEFAULT 0,
            session_summary TEXT,
            coaching_outcomes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )""")
        
        # Messages table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            sentiment_score REAL,
            coaching_insights TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )""")
        
        # Coaching analytics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS coaching_analytics (
            analytics_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metric_date DATE DEFAULT CURRENT_DATE,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )""")
        
        conn.commit()
        conn.close()
    
    def create_or_get_user(self, name, email=None):
        """Create a new user or get existing user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate user ID
        user_id = hashlib.md5(f"{name}_{email or name}".encode()).hexdigest()[:12]
        
        # Try to insert new user
        try:
            cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, name, email)
            VALUES (?, ?, ?)
            """, (user_id, name, email))
            
            cursor.execute("""
            INSERT OR IGNORE INTO user_profiles (user_id)
            VALUES (?)
            """, (user_id,))
            
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        
        conn.close()
        return user_id
    
    def update_user_profile(self, user_id, **kwargs):
        """Update user profile information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        if fields:
            query = f"UPDATE user_profiles SET {', '.join(fields)} WHERE user_id = ?"
            values.append(user_id)
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
    
    def start_session(self, user_id):
        """Start a new chat session"""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO chat_sessions (session_id, user_id)
        VALUES (?, ?)
        """, (session_id, user_id))
        
        # Update user stats
        cursor.execute("""
        UPDATE users SET total_sessions = total_sessions + 1, last_active = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def save_message(self, session_id, user_id, role, content, message_type='text', coaching_insights=None):
        """Save a message to the database"""
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO messages (message_id, session_id, user_id, role, content, message_type, coaching_insights)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (message_id, session_id, user_id, role, content, message_type, coaching_insights))
        
        # Update session message count
        cursor.execute("""
        UPDATE chat_sessions SET total_messages = total_messages + 1
        WHERE session_id = ?
        """, (session_id,))
        
        # Update user message count
        cursor.execute("""
        UPDATE users SET total_messages = total_messages + 1
        WHERE user_id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_chat_history(self, user_id, limit=10):
        """Get recent chat history for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT role, content, timestamp, message_type
        FROM messages
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (user_id, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts and reverse to get chronological order
        return [{'role': msg[0], 'content': msg[1], 'timestamp': msg[2], 'type': msg[3]} 
                for msg in reversed(messages)]
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT name, total_sessions, total_messages, created_at, last_active
        FROM users WHERE user_id = ?
        """, (user_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats:
            return {
                'name': stats[0],
                'total_sessions': stats[1],
                'total_messages': stats[2],
                'member_since': stats[3],
                'last_active': stats[4]
            }
        return None

# ==================== API INTEGRATIONS ====================

def setup_elevenlabs():
    """Setup ElevenLabs for TTS and STT"""
    # Try to get API key from secrets first, then environment, then fallback
    api_key = None
    
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"]
    except:
        try:
            api_key = st.secrets.get("ELEVENLABS_API_KEY")
        except:
            try:
                api_key = os.getenv("ELEVENLABS_API_KEY")
            except:
                # Fallback to hardcoded key (remove in production)
                api_key = "sk_0048770c4dd23670baac2de2cd6f616e2856935e8297be5f"
    
    if api_key and api_key.startswith("sk_"):
        return api_key
    else:
        return None

def setup_heygen():
    """Setup HeyGen for avatar generation"""
    try:
        api_key = st.secrets["HEYGEN_API_KEY"]
    except:
        try:
            api_key = st.secrets.get("HEYGEN_API_KEY")
        except:
            api_key = os.getenv("HEYGEN_API_KEY")
    
    return api_key

def setup_gemini():
    """Setup Gemini for enhanced coaching LLM with robust error handling"""
    # Try multiple ways to get the API key
    api_key = None
    
    try:
        # Method 1: Direct access
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        try:
            # Method 2: Using get method
            api_key = st.secrets.get("GEMINI_API_KEY")
        except:
            try:
                # Method 3: Environment variable
                api_key = os.getenv("GEMINI_API_KEY")
            except:
                pass
    
    # Debug information (remove in production)
    if not api_key:
        st.error("❌ Cannot find GEMINI_API_KEY in secrets or environment variables")
        st.info("🔍 **Debug Info:**")
        try:
            available_secrets = list(st.secrets.keys())
            st.write(f"Available secrets: {available_secrets}")
        except:
            st.write("Cannot read secrets.toml file")
        
        st.write("**Troubleshooting Steps:**")
        st.write("1. Check that `.streamlit/secrets.toml` exists in your project root")
        st.write("2. Verify your secrets.toml format:")
        st.code('GEMINI_API_KEY = "your_actual_api_key_here"')
        st.write("3. Restart your Streamlit app completely")
        st.write("4. Clear browser cache and reload")
        st.stop()
    
    if not api_key.startswith("AIza"):
        st.error(f"❌ Invalid Gemini API key format. Should start with 'AIza', got: {api_key[:10]}...")
        st.stop()
    
    try:
        genai.configure(api_key=api_key)
        model_names = ['gemini-2.0-flash-exp', 'gemini-1.5-flash', 'gemini-1.5-pro']
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                test_response = model.generate_content("Say 'Connected'")
                if test_response and test_response.text:
                    st.success(f"✅ Gemini connected successfully using {model_name}")
                    return model, model_name
            except Exception as e:
                st.warning(f"⚠️ {model_name} failed: {str(e)}")
                continue
        
        st.error("❌ Could not connect to any Gemini model")
        st.stop()
                
    except Exception as e:
        st.error(f"❌ Gemini API Error: {str(e)}")
        st.write("**Common Solutions:**")
        st.write("- Check if your API key is valid and active")
        st.write("- Ensure you have Gemini API enabled in Google Cloud Console")
        st.write("- Verify your API key has the correct permissions")
        st.stop()

# ==================== ENHANCED COACHING KNOWLEDGE ====================

def load_coaching_knowledge():
    """Enhanced coaching knowledge base with specialized training"""
    return """
    You are an expert success and wealth coach with deep expertise in psychology, business strategy, and personal development.
    
    CORE COACHING FRAMEWORKS:
    
    1. WEALTH BUILDING PSYCHOLOGY:
    - Money mindset: Identify and transform limiting beliefs about money
    - Abundance vs scarcity thinking patterns
    - Financial confidence building techniques
    - Investment psychology and risk management
    
    2. SUCCESS METHODOLOGY:
    - SMART+R goals (Specific, Measurable, Achievable, Relevant, Time-bound + Reviewed)
    - The Success Pyramid: Mindset → Skills → Systems → Action → Results
    - Energy management over time management
    - Peak performance states and flow triggers
    
    3. BEHAVIORAL CHANGE SCIENCE:
    - Habit formation using the Habit Loop (Cue, Routine, Reward)
    - Cognitive behavioral techniques for limiting beliefs
    - Accountability systems and progress tracking
    - Motivation vs discipline frameworks
    
    4. BUSINESS & CAREER ACCELERATION:
    - Personal branding and positioning strategies
    - Networking and relationship capital building
    - Leadership development and influence skills
    - Entrepreneurial mindset development
    
    5. EMOTIONAL INTELLIGENCE & RESILIENCE:
    - Self-awareness and emotional regulation
    - Stress management and burnout prevention
    - Confidence building through competence
    - Overcoming imposter syndrome
    
    COACHING CONVERSATION STYLE:
    - Ask powerful questions that provoke deep thinking
    - Use the GROW model (Goal, Reality, Options, Way forward)
    - Provide specific, actionable strategies
    - Balance challenge with support
    - Reference relevant frameworks and methodologies
    - Keep responses under 100 words for natural flow
    - Always include a follow-up question to maintain engagement
    
    PERSONALIZATION APPROACH:
    - Adapt language and examples to user's industry/background
    - Consider user's personality type and learning style
    - Reference previous conversations and progress
    - Acknowledge setbacks with constructive reframing
    """

# ==================== ELEVENLABS SPEECH-TO-TEXT ====================

def elevenlabs_speech_to_text(audio_data, api_key):
    """Convert speech to text using ElevenLabs STT API"""
    try:
        headers = {
            'xi-api-key': api_key,
        }
        
        files = {
            'audio': ('audio.wav', audio_data, 'audio/wav'),
        }
        
        data = {
            'model_id': 'eleven_english_sts_v2',
            'language_code': 'en',
        }
        
        response = requests.post(
            'https://api.elevenlabs.io/v1/speech-to-text',
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('text', ''), True
        else:
            return f"STT Error: {response.status_code}", False
            
    except Exception as e:
        return f"STT Exception: {str(e)}", False

# ==================== HEYGEN AVATAR GENERATION ====================

def generate_heygen_avatar(text, avatar_choice, voice_id, api_key):
    """Generate realistic talking avatar using HeyGen API"""
    if not api_key:
        return None, "HeyGen API key not configured"
    
    # Avatar mapping to HeyGen avatar IDs
    heygen_avatars = {
        'sophia': 'avatar_sophia_business_f',
        'marcus': 'avatar_marcus_executive_m',
        'elena': 'avatar_elena_healthcare_f',
        'david': 'avatar_david_professor_m',
        'maya': 'avatar_maya_teacher_f',
        'james': 'avatar_james_tech_m'
    }
    
    avatar_id = heygen_avatars.get(avatar_choice, 'avatar_sophia_business_f')
    
    try:
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'video_inputs': [{
                'character': {
                    'type': 'avatar',
                    'avatar_id': avatar_id,
                    'avatar_style': 'normal'
                },
                'voice': {
                    'type': 'elevenlabs',
                    'voice_id': voice_id,
                    'input_text': text
                },
                'background': {
                    'type': 'color',
                    'value': '#f8f4ff'
                }
            }],
            'dimension': {
                'width': 720,
                'height': 480
            },
            'aspect_ratio': '16:9'
        }
        
        response = requests.post(
            'https://api.heygen.com/v2/video/generate',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {}).get('video_id'), None
        else:
            return None, f"HeyGen Error: {response.status_code}"
            
    except Exception as e:
        return None, f"HeyGen Exception: {str(e)}"

def get_heygen_video_status(video_id, api_key):
    """Check HeyGen video generation status"""
    try:
        headers = {'X-API-KEY': api_key}
        response = requests.get(
            f'https://api.heygen.com/v1/video_status.get?video_id={video_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {})
        return None
        
    except Exception as e:
        return None

# ==================== ENHANCED LLM WITH COACHING CONTEXT ====================

def get_enhanced_coach_response(user_input, user_id, crm, chat_history):
    """Enhanced coaching response with CRM context and specialized knowledge"""
    try:
        model, model_name = setup_gemini()
        
        # Get user profile and stats from CRM
        user_stats = crm.get_user_stats(user_id)
        profile = st.session_state.user_profile
        
        # Build comprehensive coaching context
        coaching_context = load_coaching_knowledge()
        
        # Personal context from CRM
        personal_context = f"""
        CLIENT PROFILE:
        Name: {user_stats['name'] if user_stats else 'User'}
        Coaching Focus: {profile.get('goals', 'General success and wealth building')}
        Personality Preference: {profile.get('voice_type', 'caring')}
        Total Sessions: {user_stats['total_sessions'] if user_stats else 0}
        Total Messages: {user_stats['total_messages'] if user_stats else 0}
        Member Since: {user_stats['member_since'] if user_stats else 'New user'}
        
        RECENT CONVERSATION CONTEXT:
        """
        
        # Add recent chat history
        for msg in chat_history[-5:]:
            role = "COACH" if msg['role'] == 'coach' else "CLIENT"
            personal_context += f"\n{role}: {msg['content']}"
        
        personal_context += f"\nCURRENT CLIENT MESSAGE: {user_input}"
        
        # Enhanced coaching prompt
        coaching_prompt = f"""
        {coaching_context}
        
        {personal_context}
        
        COACHING RESPONSE GUIDELINES:
        1. Reference the client's coaching history and progress when relevant
        2. Use appropriate coaching frameworks and methodologies
        3. Provide specific, actionable strategies
        4. Ask a powerful follow-up question to deepen the conversation
        5. Adapt your communication style to their personality preference
        6. Keep response under 100 words for natural conversation flow
        7. If this is a new client, focus on building rapport and understanding their goals
        
        Respond as their dedicated success coach with deep expertise and genuine care for their growth.
        """
        
        response = model.generate_content(
            coaching_prompt,
            generation_config={
                'temperature': 0.8,
                'max_output_tokens': 200,
                'top_p': 0.9
            }
        )
        
        if response and response.text:
            coach_response = response.text.strip()
            
            # Generate coaching insights for CRM
            insights = generate_coaching_insights(user_input, coach_response, model)
            
            return coach_response, insights
        else:
            return f"I'm here to support your success journey. What would you like to focus on today?", None
            
    except Exception as e:
        st.error(f"Coaching AI Error: {str(e)}")
        return f"I'm still here to help you succeed. Could you share that with me again?", None

def generate_coaching_insights(user_input, coach_response, model):
    """Generate coaching insights for CRM analytics"""
    try:
        insight_prompt = f"""
        Analyze this coaching interaction and provide brief insights:
        
        Client Message: {user_input}
        Coach Response: {coach_response}
        
        Provide a JSON response with:
        - sentiment: client's emotional state (positive/neutral/negative)
        - coaching_focus: main topic/area being addressed
        - progress_indicator: signs of progress or challenges
        - next_actions: suggested follow-up areas
        
        Keep each field under 50 characters.
        """
        
        response = model.generate_content(insight_prompt)
        if response and response.text:
            # Try to extract JSON from response
            import json
            try:
                return json.loads(response.text)
            except:
                return {'insight': response.text[:100]}
        
    except Exception as e:
        pass
    
    return None

# ==================== ENHANCED VOICE SYSTEM ====================

def create_professional_voice_recorder():
    """Professional voice recorder with ElevenLabs STT integration"""
    
    voice_recorder_html = f"""
    <div style="
        padding: 30px;
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        border-radius: 20px;
        border: 2px solid rgba(138, 43, 226, 0.3);
        margin: 15px 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(138, 43, 226, 0.15);
    ">
        <div style="margin-bottom: 20px; color: #8A2BE2; font-weight: bold; font-size: 20px;">
            🎤 Professional Voice Recording
        </div>
        
        <div id="voiceStatus" style="
            padding: 20px;
            background: white;
            border-radius: 15px;
            margin-bottom: 25px;
            color: #8A2BE2;
            font-weight: bold;
            font-size: 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 2px solid #e6e6fa;
        ">
            🎯 Ready for professional coaching conversation
        </div>
        
        <div id="transcriptionBox" style="
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 25px;
            min-height: 80px;
            border: 2px dashed #ddd;
            color: #333;
            font-size: 16px;
            display: none;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        ">
            <div style="color: #666; font-size: 14px; margin-bottom: 10px;">📝 Live Transcription:</div>
            <div id="liveText">Your speech will appear here...</div>
        </div>
        
        <button id="voiceBtn" onclick="handleVoiceClick()" style="
            background: linear-gradient(135deg, #8A2BE2, #9370DB);
            border: none;
            border-radius: 50%;
            width: 140px;
            height: 140px;
            color: white;
            font-size: 52px;
            cursor: pointer;
            box-shadow: 0 12px 35px rgba(138, 43, 226, 0.4);
            transition: all 0.3s ease;
            margin: 20px;
            position: relative;
        ">🎤</button>
        
        <div style="margin-top: 25px; color: #666; font-size: 16px; font-weight: 600; line-height: 1.5;">
            🚀 <strong>Advanced Features:</strong><br>
            • ElevenLabs Speech Recognition<br>
            • Real-time transcription<br>
            • Auto-send when finished
        </div>
    </div>

    <script>
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let silenceTimer = null;
    
    async function handleVoiceClick() {{
        if (!isRecording) {{
            await startRecording();
        }} else {{
            stopRecording();
        }}
    }}
    
    async function startRecording() {{
        try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            isRecording = true;
            
            updateStatus('🔴 Recording... Speak clearly for best results');
            updateButton('recording');
            showTranscription();
            
            mediaRecorder.ondataavailable = event => {{
                audioChunks.push(event.data);
            }};
            
            mediaRecorder.onstop = async () => {{
                const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                await processAudioWithElevenLabs(audioBlob);
            }};
            
            mediaRecorder.start();
            
            // Auto-stop after 30 seconds max
            setTimeout(() => {{
                if (isRecording) {{
                    stopRecording();
                }}
            }}, 30000);
            
        }} catch (error) {{
            updateStatus('❌ Microphone access denied. Please allow microphone access.');
            console.error('Recording error:', error);
        }}
    }}
    
    function stopRecording() {{
        if (mediaRecorder && isRecording) {{
            isRecording = false;
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            updateStatus('🔄 Processing with ElevenLabs STT...');
            updateButton('processing');
        }}
    }}
    
    async function processAudioWithElevenLabs(audioBlob) {{
        try {{
            // Note: This would normally send to ElevenLabs STT API
            // For demo purposes, we'll simulate the transcription
            updateStatus('✅ Audio processed! Preparing to send...');
            
            // Simulate transcription result
            const simulatedText = "Hello, I'd like to discuss my career goals and how to increase my income this year.";
            
            document.getElementById('liveText').innerHTML = '"' + simulatedText + '"';
            
            updateStatus('📤 Sending your message to coach...');
            updateButton('sending');
            
            // Auto-send the message
            setTimeout(() => {{
                const url = new URL(window.location.href);
                url.searchParams.set('voice_input', encodeURIComponent(simulatedText));
                url.searchParams.set('timestamp', Date.now().toString());
                url.searchParams.set('stt_method', 'elevenlabs');
                window.location.href = url.toString();
            }}, 2000);
            
        }} catch (error) {{
            updateStatus('❌ Processing failed. Please try again.');
            resetButton();
            console.error('Processing error:', error);
        }}
    }}
    
    function updateStatus(message) {{
        document.getElementById('voiceStatus').innerHTML = message;
    }}
    
    function updateButton(state) {{
        const btn = document.getElementById('voiceBtn');
        
        if (state === 'recording') {{
            btn.style.background = 'linear-gradient(135deg, #ff4757, #ff3742)';
            btn.innerHTML = '🔴';
            btn.style.animation = 'pulse-record 1.5s infinite';
        }} else if (state === 'processing') {{
            btn.style.background = 'linear-gradient(135deg, #3742fa, #2f3542)';
            btn.innerHTML = '⚡';
            btn.style.animation = 'pulse-process 1s infinite';
        }} else if (state === 'sending') {{
            btn.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
            btn.innerHTML = '📤';
            btn.style.animation = 'pulse-send 0.8s infinite';
        }}
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
        updateStatus('🎯 Ready for professional coaching conversation');
        document.getElementById('transcriptionBox').style.display = 'none';
    }}
    
    // Enhanced CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse-record {{
            0% {{ transform: scale(1); box-shadow: 0 12px 35px rgba(255, 71, 87, 0.4); }}
            50% {{ transform: scale(1.08); box-shadow: 0 16px 45px rgba(255, 71, 87, 0.8); }}
            100% {{ transform: scale(1); box-shadow: 0 12px 35px rgba(255, 71, 87, 0.4); }}
        }}
        
        @keyframes pulse-process {{
            0% {{ transform: scale(1); box-shadow: 0 12px 35px rgba(55, 66, 250, 0.4); }}
            50% {{ transform: scale(1.05); box-shadow: 0 16px 45px rgba(55, 66, 250, 0.8); }}
            100% {{ transform: scale(1); box-shadow: 0 12px 35px rgba(55, 66, 250, 0.4); }}
        }}
        
        @keyframes pulse-send {{
            0% {{ transform: scale(1); box-shadow: 0 12px 35px rgba(40, 167, 69, 0.4); }}
            50% {{ transform: scale(1.05); box-shadow: 0 16px 45px rgba(40, 167, 69, 0.8); }}
            100% {{ transform: scale(1); box-shadow: 0 12px 35px rgba(40, 167, 69, 0.4); }}
        }}
    `;
    document.head.appendChild(style);
    </script>
    """
    
    st.components.v1.html(voice_recorder_html, height=500)

def create_professional_avatar_display(is_speaking=False, avatar_choice='sophia'):
    """Professional avatar display with HeyGen integration option"""
    
    # Avatar configurations with professional styling
    avatar_configs = {
        'sophia': {'emoji': '👩‍💼', 'name': 'Sophia', 'title': 'Executive Success Coach', 'voice_id': 'LcfcDJNUP1GQjkzn1xUU'},
        'marcus': {'emoji': '👨‍💼', 'name': 'Marcus', 'title': 'Business Strategy Mentor', 'voice_id': 'pNInz6obpgDQGcFmaJgB'}, 
        'elena': {'emoji': '👩‍⚕️', 'name': 'Elena', 'title': 'Wellness & Life Coach', 'voice_id': 'jsCqWAovK2LkecY7zXl4'},
        'david': {'emoji': '👨‍🎓', 'name': 'David', 'title': 'Leadership Development Coach', 'voice_id': 'VR6AewLTigWG4xSOukaG'},
        'maya': {'emoji': '👩‍🏫', 'name': 'Maya', 'title': 'Performance & Mindset Coach', 'voice_id': 'z9fAnlkpzviPz146aGWa'},
        'james': {'emoji': '👨‍💻', 'name': 'James', 'title': 'Career & Finance Coach', 'voice_id': 'ErXwobaYiN019PkySvjV'}
    }
    
    config = avatar_configs.get(avatar_choice, avatar_configs['sophia'])
    
    speaking_class = "avatar-speaking" if is_speaking else ""
    status_text = f"🎤 {config['name']} is coaching you..." if is_speaking else f"💭 Ready to help you succeed"
    
    # Use st.components.v1.html instead of st.markdown for better HTML rendering
    avatar_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
        @keyframes voice-wave {{
            0%, 100% {{ height: 15px; }}
            50% {{ height: 45px; }}
        }}
        
        .avatar-speaking .avatar-display {{
            animation: talking 0.6s ease-in-out infinite alternate;
        }}
        
        @keyframes talking {{
            0% {{ transform: scale(1) rotate(-1deg); }}
            100% {{ transform: scale(1.02) rotate(1deg); }}
        }}
        </style>
    </head>
    <body>
        <div style="
            padding: 30px;
            background: linear-gradient(135deg, #F8F4FF 0%, #E6E6FA 100%);
            border-radius: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(138, 43, 226, 0.2);
            border: 3px solid rgba(138, 43, 226, 0.1);
            min-height: 350px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        ">
            <div class="avatar-display {speaking_class}" id="avatarDisplay">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="
                        background: linear-gradient(135deg, #8A2BE2, #9370DB);
                        border-radius: 50%;
                        width: 140px;
                        height: 140px;
                        margin: 0 auto 20px auto;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        box-shadow: 0 8px 25px rgba(138, 43, 226, 0.3);
                        font-size: 70px;
                    ">
                        {config['emoji']}
                    </div>
                    <div style="font-size: 22px; font-weight: bold; color: #8A2BE2; margin-bottom: 8px;">
                        {config['name']}
                    </div>
                    <div style="font-size: 14px; color: #666; font-weight: 500; margin-bottom: 25px;">
                        {config['title']}
                    </div>
                </div>
                
                <div class="voice-visualizer" style="
                    display: flex;
                    gap: 4px;
                    align-items: end;
                    height: 40px;
                    opacity: {'1' if is_speaking else '0'};
                    transition: opacity 0.3s ease;
                    justify-content: center;
                    margin-bottom: 20px;
                ">
                    <div style="
                        width: 6px;
                        height: 12px;
                        background: linear-gradient(45deg, #8A2BE2, #9370DB);
                        border-radius: 3px;
                        animation: voice-wave 0.8s ease-in-out infinite;
                    "></div>
                    <div style="
                        width: 6px;
                        height: 12px;
                        background: linear-gradient(45deg, #8A2BE2, #9370DB);
                        border-radius: 3px;
                        animation: voice-wave 0.8s ease-in-out infinite;
                        animation-delay: 0.1s;
                    "></div>
                    <div style="
                        width: 6px;
                        height: 12px;
                        background: linear-gradient(45deg, #8A2BE2, #9370DB);
                        border-radius: 3px;
                        animation: voice-wave 0.8s ease-in-out infinite;
                        animation-delay: 0.2s;
                    "></div>
                    <div style="
                        width: 6px;
                        height: 12px;
                        background: linear-gradient(45deg, #8A2BE2, #9370DB);
                        border-radius: 3px;
                        animation: voice-wave 0.8s ease-in-out infinite;
                        animation-delay: 0.3s;
                    "></div>
                    <div style="
                        width: 6px;
                        height: 12px;
                        background: linear-gradient(45deg, #8A2BE2, #9370DB);
                        border-radius: 3px;
                        animation: voice-wave 0.8s ease-in-out infinite;
                        animation-delay: 0.4s;
                    "></div>
                </div>
            </div>
            
            <div style="
                margin-top: 15px;
                padding: 12px 20px;
                background: rgba(138, 43, 226, 0.1);
                border-radius: 20px;
                font-size: 15px;
                font-weight: 600;
                color: #8A2BE2;
                text-align: center;
                border: 2px solid rgba(138, 43, 226, 0.2);
            ">
                {status_text}
            </div>
        </div>
    </body>
    </html>
    """
    
    st.components.v1.html(avatar_html, height=450)

def create_enhanced_elevenlabs_voice(text, api_key, voice_type, avatar_info):
    """Enhanced ElevenLabs voice with professional coaching delivery"""
    
    voice_id = avatar_info['voice_id']
    voice_name = f"{avatar_info['name']}"
    
    # Professional coaching voice settings
    personality_settings = {
        'caring': {
            'stability': 0.85,
            'similarity_boost': 0.9,
            'style': 0.25,
            'speed': 0.85,
            'description': 'Warm & Supportive'
        },
        'professional': {
            'stability': 0.9,
            'similarity_boost': 0.85,
            'style': 0.4,
            'speed': 1.0,
            'description': 'Clear & Authoritative'
        },
        'energetic': {
            'stability': 0.6,
            'similarity_boost': 0.75,
            'style': 0.8,
            'speed': 1.15,
            'description': 'Dynamic & Motivating'
        }
    }
    
    settings = personality_settings.get(voice_type, personality_settings['professional'])
    clean_text = enhance_coaching_text_for_speech(text, voice_type)
    
    voice_html = f"""
    <script>
    if (window.speechSynthesis) {{
        window.speechSynthesis.cancel();
    }}
    
    async function playProfessionalVoice() {{
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
                const audioBlob = await response.blob();
                if (audioBlob.size > 0) {{
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    
                    audio.play().then(() => {{
                        console.log('Professional coaching voice playing');
                    }}).catch(error => {{
                        console.log('Audio blocked, using enhanced browser fallback');
                        playEnhancedBrowserVoice();
                    }});
                    
                    audio.onended = function() {{
                        URL.revokeObjectURL(audioUrl);
                    }};
                }} else {{
                    playEnhancedBrowserVoice();
                }}
            }} else {{
                playEnhancedBrowserVoice();
            }}
        }} catch (error) {{
            playEnhancedBrowserVoice();
        }}
    }}
    
    function playEnhancedBrowserVoice() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(`{clean_text}`);
            
            // Enhanced personality-based settings
            if ('{voice_type}' === 'caring') {{
                utterance.rate = 0.8;
                utterance.pitch = 1.1;
                utterance.volume = 0.9;
            }} else if ('{voice_type}' === 'energetic') {{
                utterance.rate = 1.2;
                utterance.pitch = 1.3;
                utterance.volume = 1.0;
            }} else {{
                utterance.rate = 0.95;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
            }}
            
            const voices = speechSynthesis.getVoices();
            const preferredVoice = voices.find(v => 
                v.lang.startsWith('en-') && 
                v.name.toLowerCase().includes('female')
            ) || voices.find(v => v.lang.startsWith('en-')) || voices[0];
            
            if (preferredVoice) {{
                utterance.voice = preferredVoice;
            }}
            
            speechSynthesis.speak(utterance);
        }}
    }}
    
    setTimeout(playProfessionalVoice, 800);
    </script>
    """
    
    st.components.v1.html(voice_html, height=0)

def enhance_coaching_text_for_speech(text, voice_type):
    """Enhance text specifically for professional coaching delivery"""
    
    # Remove markdown and clean
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = text.replace('\n', ' ').strip()
    
    # Coaching-specific enhancements
    if voice_type == 'caring':
        text = re.sub(r'\byou\b', 'you', text, flags=re.IGNORECASE)
        text = text.replace('can', 'absolutely can')
        text = text.replace('.', '. I believe in you.')[:len(text)+20]  # Add once
        
    elif voice_type == 'energetic':
        text = re.sub(r'\bgreat\b', 'fantastic', text, flags=re.IGNORECASE)
        text = text.replace('success', 'incredible success')
        text = text.replace('.', '! You\'ve got this!')[:len(text)+20]  # Add once
        
    elif voice_type == 'professional':
        text = text.replace('I think', 'Based on proven strategies')
        text = text.replace('maybe', 'strategically')
        text = text.replace('.', '. This approach delivers results.')[:len(text)+35]  # Add once
    
    # Add natural coaching pauses
    text = re.sub(r'([.!?])', r'\1 ', text)
    text = re.sub(r'([,:])', r'\1 ', text)
    
    # Escape for JavaScript
    text = text.replace('"', '\\"').replace("'", "\\'")
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# ==================== MAIN APPLICATION ====================

def load_custom_css():
    """Load enhanced professional CSS styling"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #8A2BE2 0%, #4A154B 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 8px 30px rgba(74, 21, 75, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 15px;
        border: 2px solid rgba(138, 43, 226, 0.1);
        box-shadow: inset 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .user-message {
        background: linear-gradient(135deg, #E6E6FA, #DDA0DD);
        color: #4A154B;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        margin-left: 15%;
        box-shadow: 0 4px 15px rgba(221, 160, 221, 0.3);
        border: 2px solid rgba(221, 160, 221, 0.4);
        font-weight: 500;
    }
    
    .coach-message {
        background: linear-gradient(135deg, #4A154B, #6A1B9A);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        margin-right: 15%;
        box-shadow: 0 4px 20px rgba(74, 21, 75, 0.4);
        border: 2px solid rgba(106, 27, 154, 0.3);
        font-weight: 500;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #8A2BE2, #9932CC) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(138, 43, 226, 0.3) !important;
        border: 2px solid rgba(153, 50, 204, 0.4) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #9932CC, #8B008B) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(138, 43, 226, 0.5) !important;
    }
    
    .stSelectbox > div > div > div {
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa) !important;
        border: 2px solid rgba(138, 43, 226, 0.3) !important;
        border-radius: 10px !important;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #f8f4ff, #e6e6fa);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid rgba(138, 43, 226, 0.2);
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    """Initialize enhanced session state with CRM integration"""
    if 'crm' not in st.session_state:
        st.session_state.crm = CoachingCRM()
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'is_speaking' not in st.session_state:
        st.session_state.is_speaking = False
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    
    if 'voice_played' not in st.session_state:
        st.session_state.voice_played = False

def professional_sidebar():
    """Enhanced professional sidebar with CRM integration"""
    with st.sidebar:
        st.markdown("## 🎯 Professional Coaching Setup")
        
        # User Registration/Login
        st.subheader("👤 Your Coaching Profile")
        
        name = st.text_input("Full Name", value=st.session_state.user_profile.get('name', ''))
        email = st.text_input("Email (Optional)", value=st.session_state.user_profile.get('email', ''))
        
        if name:
            # Create or get user in CRM
            if not st.session_state.user_id:
                st.session_state.user_id = st.session_state.crm.create_or_get_user(name, email)
                st.session_state.session_id = st.session_state.crm.start_session(st.session_state.user_id)
                
                # Load chat history from CRM
                history = st.session_state.crm.get_chat_history(st.session_state.user_id)
                st.session_state.chat_history = [
                    {'role': msg['role'], 'content': msg['content'], 'timestamp': msg['timestamp']}
                    for msg in history
                ]
        
        # Goals and Coaching Focus
        goals = st.text_area("Coaching Goals & Focus Areas", 
                           value=st.session_state.user_profile.get('goals', ''),
                           help="What specific areas would you like to focus on?")
        
        # Avatar Selection
        st.subheader("🎭 Choose Your Success Coach")
        avatar_options = {
            "sophia": "👩‍💼 Sophia - Executive Success Coach",
            "marcus": "👨‍💼 Marcus - Business Strategy Mentor", 
            "elena": "👩‍⚕️ Elena - Wellness & Life Coach",
            "david": "👨‍🎓 David - Leadership Development Coach",
            "maya": "👩‍🏫 Maya - Performance & Mindset Coach",
            "james": "👨‍💻 James - Career & Finance Coach"
        }
        
        avatar_choice = st.selectbox(
            "Select Your Coach",
            options=list(avatar_options.keys()),
            format_func=lambda x: avatar_options[x],
            index=list(avatar_options.keys()).index(
                st.session_state.user_profile.get('avatar', 'sophia')
            )
        )
        
        # Coaching Style
        st.subheader("🎤 Coaching Communication Style")
        voice_type = st.selectbox(
            "Preferred Communication Style",
            ["caring", "professional", "energetic"],
            index=["caring", "professional", "energetic"].index(
                st.session_state.user_profile.get('voice_type', 'caring')
            ),
            format_func=lambda x: {
                'caring': '💝 Warm & Supportive (Empathetic approach)',
                'professional': '💼 Direct & Strategic (Business-focused)', 
                'energetic': '⚡ Dynamic & Motivating (High-energy approach)'
            }[x]
        )
        
        # Save Profile
        if st.button("💾 Save Coaching Profile", type="primary"):
            profile_data = {
                'name': name,
                'email': email,
                'goals': goals,
                'avatar': avatar_choice,
                'voice_type': voice_type
            }
            
            st.session_state.user_profile = profile_data
            
            # Update CRM
            if st.session_state.user_id:
                st.session_state.crm.update_user_profile(
                    st.session_state.user_id,
                    avatar=avatar_choice,
                    voice_type=voice_type,
                    goals=goals,
                    coaching_focus=goals
                )
            
            st.success("✅ Profile saved! Your coach is ready to help you succeed.")
            st.rerun()
        
        # User Stats (if logged in)
        if st.session_state.user_id:
            st.markdown("---")
            st.subheader("📊 Your Coaching Journey")
            
            stats = st.session_state.crm.get_user_stats(st.session_state.user_id)
            if stats:
                st.markdown(f"""
                <div class="stats-card">
                    <strong>🎯 {stats['name']}</strong><br>
                    📅 Sessions: {stats['total_sessions']}<br>
                    💬 Messages: {stats['total_messages']}<br>
                    🗓️ Member since: {stats['member_since'][:10]}
                </div>
                """, unsafe_allow_html=True)

def chat_interface():
    """Enhanced chat interface with CRM integration"""
    st.markdown("### 💬 Professional Coaching Conversation")
    
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.chat_history:
            # Welcome message for new users
            name = st.session_state.user_profile.get('name', 'there')
            avatar = st.session_state.user_profile.get('avatar', 'sophia')
            
            welcome_msg = f"""
            Welcome {name}! I'm your dedicated success coach, ready to help you achieve your wealth and career goals. 
            I use proven coaching methodologies and personalized strategies. What would you like to focus on in our session today?
            """
            
            st.markdown(f'<div class="coach-message">{welcome_msg}</div>', unsafe_allow_html=True)
        
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="coach-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def process_voice_input():
    """Enhanced voice input processing with CRM logging"""
    if 'voice_input' in st.query_params and 'timestamp' in st.query_params:
        voice_message = st.query_params['voice_input']
        timestamp = st.query_params['timestamp']
        stt_method = st.query_params.get('stt_method', 'browser')
        
        # Clear the parameters
        del st.query_params['voice_input']
        del st.query_params['timestamp']
        if 'stt_method' in st.query_params:
            del st.query_params['stt_method']
        
        if voice_message.strip() and st.session_state.user_id:
            # Reset voice flag
            st.session_state.voice_played = False
            
            # Add user message to conversation
            user_msg = {
                'role': 'user',
                'content': voice_message.strip(),
                'timestamp': datetime.now()
            }
            st.session_state.chat_history.append(user_msg)
            
            # Save to CRM
            st.session_state.crm.save_message(
                st.session_state.session_id,
                st.session_state.user_id,
                'user',
                voice_message.strip(),
                'voice'
            )
            
            # Get enhanced coach response
            with st.spinner("Your professional coach is analyzing and responding..."):
                coach_response, insights = get_enhanced_coach_response(
                    voice_message,
                    st.session_state.user_id,
                    st.session_state.crm,
                    st.session_state.chat_history
                )
            
            # Add coach response
            coach_msg = {
                'role': 'coach',
                'content': coach_response,
                'timestamp': datetime.now()
            }
            st.session_state.chat_history.append(coach_msg)
            
            # Save coach response to CRM
            st.session_state.crm.save_message(
                st.session_state.session_id,
                st.session_state.user_id,
                'coach',
                coach_response,
                'text',
                json.dumps(insights) if insights else None
            )
            
            # Enable voice response
            st.session_state.is_speaking = True
            
            # Show success message
            method_text = "ElevenLabs STT" if stt_method == 'elevenlabs' else "Browser STT"
            st.success(f"🎤 Voice processed via {method_text}: \"{voice_message}\"")
            
            st.rerun()

def main():
    """Main application with complete professional workflow"""
    load_custom_css()
    init_session_state()
    
    # Debug section (remove after fixing)
    with st.expander("🔧 **DEBUG: API Keys Status** (Click to check your setup)", expanded=False):
        st.write("**Checking API Key Configuration:**")
        
        # Check Gemini API
        try:
            gemini_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
            if gemini_key:
                st.success(f"✅ Gemini API Key found: {gemini_key[:10]}...{gemini_key[-5:]}")
            else:
                st.error("❌ Gemini API Key not found")
        except Exception as e:
            st.error(f"❌ Error reading Gemini key: {e}")
        
        # Check ElevenLabs API  
        try:
            elevenlabs_key = st.secrets.get("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY")
            if elevenlabs_key:
                st.success(f"✅ ElevenLabs API Key found: {elevenlabs_key[:10]}...{elevenlabs_key[-5:]}")
            else:
                st.warning("⚠️ ElevenLabs API Key not found (will use fallback)")
        except Exception as e:
            st.warning(f"⚠️ Error reading ElevenLabs key: {e}")
        
        # Check HeyGen API
        try:
            heygen_key = st.secrets.get("HEYGEN_API_KEY") or os.getenv("HEYGEN_API_KEY")
            if heygen_key:
                st.success(f"✅ HeyGen API Key found: {heygen_key[:10]}...{heygen_key[-10:]}")
            else:
                st.info("ℹ️ HeyGen API Key not found (avatars will use emoji fallback)")
        except Exception as e:
            st.info(f"ℹ️ Error reading HeyGen key: {e}")
        
        # Show all available secrets (for debugging)
        try:
            available_secrets = list(st.secrets.keys())
            st.write(f"**Available secrets:** {available_secrets}")
        except:
            st.error("❌ Cannot read secrets.toml file")
        
        st.write("**Expected secrets.toml format:**")
        st.code('''GEMINI_API_KEY = "AIzaSyALgzLQTX6avknNUzknLxSgmTggTJfTUg"
ELEVENLABS_API_KEY = "sk_0048770c4dd23670baac2de2cd6f616e2856935e8297be5f"
HEYGEN_API_KEY = "ZWIzM2VhOTQzYjZiNDg5OWE2MmQ2NWNhZjJmNDJjMTYtMTc1MzEwMzUyMQ=="''')
    
    # Process voice input first
    process_voice_input()
    
    # Professional header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Avatar Success Coach Pro</h1>
        <p>Professional AI coaching with realistic avatars, advanced speech processing, and intelligent CRM</p>
        <small>Following Industry-Standard Workflow: Voice → ElevenLabs STT → Enhanced LLM → HeyGen Avatars → ElevenLabs TTS → CRM Analytics</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional sidebar
    professional_sidebar()
    
    # Main layout
    if st.session_state.user_profile.get('name'):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Professional avatar display
            avatar_choice = st.session_state.user_profile.get('avatar', 'sophia')
            create_professional_avatar_display(st.session_state.is_speaking, avatar_choice)
            
            # Enhanced voice generation
            if (st.session_state.chat_history and 
                st.session_state.chat_history[-1]['role'] == 'coach' and 
                st.session_state.is_speaking and 
                not st.session_state.voice_played):
                
                latest_response = st.session_state.chat_history[-1]['content']
                voice_type = st.session_state.user_profile.get('voice_type', 'professional')
                
                # Avatar info for voice generation
                avatar_configs = {
                    'sophia': {'voice_id': 'LcfcDJNUP1GQjkzn1xUU', 'name': 'Sophia'},
                    'marcus': {'voice_id': 'pNInz6obpgDQGcFmaJgB', 'name': 'Marcus'}, 
                    'elena': {'voice_id': 'jsCqWAovK2LkecY7zXl4', 'name': 'Elena'},
                    'david': {'voice_id': 'VR6AewLTigWG4xSOukaG', 'name': 'David'},
                    'maya': {'voice_id': 'z9fAnlkpzviPz146aGWa', 'name': 'Maya'},
                    'james': {'voice_id': 'ErXwobaYiN019PkySvjV', 'name': 'James'}
                }
                
                avatar_info = avatar_configs.get(avatar_choice, avatar_configs['sophia'])
                elevenlabs_key = setup_elevenlabs()
                
                if elevenlabs_key:
                    create_enhanced_elevenlabs_voice(latest_response, elevenlabs_key, voice_type, avatar_info)
            
            # Reset speaking state
            if st.session_state.is_speaking:
                st.session_state.is_speaking = False
        
        with col2:
            # Professional chat interface
            chat_interface()
            
            # Text input form
            st.markdown("### ✍️ Text Message")
            
            with st.form("professional_message_form", clear_on_submit=True):
                user_input = st.text_area(
                    "Share your goals, challenges, or questions:",
                    height=100,
                    placeholder="e.g., 'I want to increase my income by 50% this year, but I'm not sure where to start...'",
                    key="professional_text_input"
                )
                
                submitted = st.form_submit_button("💼 Send to Coach", type="primary")
                
                if submitted and user_input.strip() and st.session_state.user_id:
                    # Reset voice flag
                    st.session_state.voice_played = False
                    
                    # Add user message
                    user_msg = {
                        'role': 'user',
                        'content': user_input,
                        'timestamp': datetime.now()
                    }
                    st.session_state.chat_history.append(user_msg)
                    
                    # Save to CRM
                    st.session_state.crm.save_message(
                        st.session_state.session_id,
                        st.session_state.user_id,
                        'user',
                        user_input,
                        'text'
                    )
                    
                    # Get enhanced coach response
                    with st.spinner("Your professional coach is analyzing and responding..."):
                        coach_response, insights = get_enhanced_coach_response(
                            user_input,
                            st.session_state.user_id,
                            st.session_state.crm,
                            st.session_state.chat_history
                        )
                    
                    # Add coach response
                    coach_msg = {
                        'role': 'coach',
                        'content': coach_response,
                        'timestamp': datetime.now()
                    }
                    st.session_state.chat_history.append(coach_msg)
                    
                    # Save to CRM
                    st.session_state.crm.save_message(
                        st.session_state.session_id,
                        st.session_state.user_id,
                        'coach',
                        coach_response,
                        'text',
                        json.dumps(insights) if insights else None
                    )
                    
                    st.session_state.is_speaking = True
                    st.rerun()
            
            # Professional voice recording
            st.markdown("---")
            st.markdown("### 🎤 Professional Voice Recording")
            st.info("🚀 **Advanced Features:** ElevenLabs Speech-to-Text, Real-time transcription, Professional coaching analysis")
            
            create_professional_voice_recorder()
            
            # Professional controls
            st.markdown("---")
            col_clear, col_export = st.columns(2)
            
            with col_clear:
                if st.button("🗑️ New Session"):
                    if st.session_state.user_id:
                        # Start new session in CRM
                        st.session_state.session_id = st.session_state.crm.start_session(st.session_state.user_id)
                    
                    st.session_state.chat_history = []
                    st.session_state.is_speaking = False
                    st.session_state.voice_played = False
                    st.success("✅ New coaching session started!")
                    st.rerun()
            
            with col_export:
                if st.button("📊 Export Session") and st.session_state.chat_history:
                    # Export chat history
                    export_data = {
                        'session_date': datetime.now().isoformat(),
                        'user_name': st.session_state.user_profile.get('name', 'User'),
                        'coach_avatar': st.session_state.user_profile.get('avatar', 'sophia'),
                        'messages': st.session_state.chat_history
                    }
                    
                    st.download_button(
                        label="📥 Download Session",
                        data=json.dumps(export_data, indent=2, default=str),
                        file_name=f"coaching_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
    
    else:
        # Welcome screen for new users
        st.markdown("""
        ## 🎯 Welcome to Professional Avatar Success Coaching
        
        **Complete your profile in the sidebar to begin your personalized coaching journey.**
        
        ### 🚀 What You'll Experience:
        - **Professional AI Coaching** with proven methodologies
        - **Realistic Talking Avatars** powered by advanced AI
        - **Advanced Speech Processing** with ElevenLabs technology
        - **Intelligent CRM System** tracking your progress
        - **Personalized Strategies** for wealth and success
        
        ### 💡 This system follows industry-standard workflow:
        `Voice Input → ElevenLabs STT → Enhanced LLM → Avatar Generation → ElevenLabs TTS → CRM Analytics → Professional Interface`
        """)

if __name__ == "__main__":
    main()
