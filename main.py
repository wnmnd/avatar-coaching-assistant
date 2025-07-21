import streamlit as st
import google.generativeai as genai
import json
import time
import base64
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
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .avatar-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    
    .avatar {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 5px solid #667eea;
        animation: pulse 2s infinite;
        background: linear-gradient(45deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        color: white;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .speaking {
        animation: bounce 0.5s infinite alternate;
    }
    
    @keyframes bounce {
        0% { transform: scale(1); }
        100% { transform: scale(1.1); }
    }
    
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
    }
    
    .coach-message {
        background: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
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
    if not api_key:
        st.error("Please set your Gemini API key in secrets.toml or environment variable")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

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
    model = setup_gemini()
    
    # Build context from chat history
    context = load_coaching_knowledge()
    context += "\n\nCONVERSATION HISTORY:\n"
    for msg in chat_history[-5:]:  # Last 5 messages for context
        context += f"{msg['role']}: {msg['content']}\n"
    
    prompt = f"""
    {context}
    
    User's latest message: {user_input}
    
    As a professional success coach, provide a helpful, engaging response that:
    1. Acknowledges what the user said
    2. Provides valuable insight or advice
    3. Asks a follow-up question to keep the conversation going
    
    Keep your response under 150 words and maintain a warm, professional tone.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return "I apologize, but I'm having trouble responding right now. Could you please try again?"

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

# Text-to-speech component
def text_to_speech_component(text):
    if text:
        # Simple text-to-speech using HTML5 Speech Synthesis API
        tts_js = f"""
        <script>
        function speakText() {{
            if ('speechSynthesis' in window) {{
                var utterance = new SpeechSynthesisUtterance(`{text}`);
                utterance.rate = 0.8;
                utterance.pitch = 1;
                utterance.volume = 1;
                
                // Try to use a female voice for the coach
                var voices = speechSynthesis.getVoices();
                var femaleVoice = voices.find(voice => 
                    voice.name.includes('Female') || 
                    voice.name.includes('Samantha') ||
                    voice.name.includes('Karen') ||
                    voice.gender === 'female'
                );
                if (femaleVoice) {{
                    utterance.voice = femaleVoice;
                }}
                
                speechSynthesis.speak(utterance);
                
                utterance.onstart = function() {{
                    console.log('Speaking started');
                }};
                
                utterance.onend = function() {{
                    console.log('Speaking ended');
                }};
            }} else {{
                alert('Text-to-speech not supported in this browser');
            }}
        }}
        
        // Auto-speak when loaded
        window.onload = function() {{
            setTimeout(speakText, 500);
        }}
        </script>
        
        <button onclick="speakText()">🔊 Play Response</button>
        """
        
        st.components.v1.html(tts_js, height=50)

# Avatar component
def avatar_component(is_speaking=False):
    avatar_class = "avatar speaking" if is_speaking else "avatar"
    
    avatar_html = f"""
    <div class="avatar-container">
        <div class="{avatar_class}">
            🎯
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

# User profile sidebar
def user_profile_sidebar():
    with st.sidebar:
        st.header("👤 Your Profile")
        
        name = st.text_input("Name", value=st.session_state.user_profile.get('name', ''))
        goals = st.text_area("Primary Goals", value=st.session_state.user_profile.get('goals', ''))
        experience = st.selectbox(
            "Experience Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(
                st.session_state.user_profile.get('experience', 'Beginner')
            )
        )
        
        focus_areas = st.multiselect(
            "Focus Areas",
            [
                "Financial Planning",
                "Career Growth",
                "Entrepreneurship",
                "Investment Strategy",
                "Time Management",
                "Leadership Skills",
                "Networking",
                "Personal Development"
            ],
            default=st.session_state.user_profile.get('focus_areas', [])
        )
        
        if st.button("Save Profile"):
            st.session_state.user_profile = {
                'name': name,
                'goals': goals,
                'experience': experience,
                'focus_areas': focus_areas
            }
            st.success("Profile saved!")

# Main app
def main():
    load_css()
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Avatar Success Coach</h1>
        <p>Your AI-powered wealth and success mentor</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User profile sidebar
    user_profile_sidebar()
    
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
        
        # Text input
        st.markdown("### ✍️ Type Your Message")
        user_input = st.text_area(
            "What would you like to discuss about your path to success?",
            height=100,
            placeholder="Ask about goal setting, financial planning, mindset, or any success-related topic..."
        )
        
        col_send, col_clear = st.columns([1, 1])
        
        with col_send:
            if st.button("Send Message", type="primary"):
                if user_input.strip():
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
        
        with col_clear:
            if st.button("Clear Chat"):
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
