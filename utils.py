"""
Utility functions for the Avatar Success Coach application
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import streamlit as st

def clean_text(text: str) -> str:
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
    
    return text.strip()

def format_chat_message(role: str, content: str, timestamp: datetime = None) -> Dict[str, Any]:
    """Format a chat message"""
    if timestamp is None:
        timestamp = datetime.now()
    
    return {
        'role': role,
        'content': content,
        'timestamp': timestamp
    }

def get_personalized_greeting(user_profile: Dict[str, Any]) -> str:
    """Generate a personalized greeting based on user profile"""
    name = user_profile.get('name', 'there')
    experience = user_profile.get('experience', 'beginner')
    focus_areas = user_profile.get('focus_areas', [])
    
    greeting = f"Hello {name}! "
    
    if experience == 'Beginner':
        greeting += "I'm excited to help you start your journey to success and wealth. "
    elif experience == 'Intermediate':
        greeting += "Great to see you're already on your success path! Let's take it to the next level. "
    else:
        greeting += "Welcome back! I'm here to help you refine and optimize your success strategies. "
    
    if focus_areas:
        areas_text = ", ".join(focus_areas[:3])  # Limit to 3 areas
        greeting += f"I see you're interested in {areas_text}. "
    
    greeting += "What would you like to work on today?"
    
    return greeting

def generate_coaching_prompt(user_input: str, user_profile: Dict[str, Any], chat_history: List[Dict]) -> str:
    """Generate a contextual prompt for the AI coach"""
    
    base_prompt = """You are a professional Success and Wealth Coach. Provide helpful, actionable advice."""
    
    # Add user context
    if user_profile:
        context = "\nUser Profile:\n"
        if user_profile.get('name'):
            context += f"- Name: {user_profile['name']}\n"
        if user_profile.get('experience'):
            context += f"- Experience Level: {user_profile['experience']}\n"
        if user_profile.get('goals'):
            context += f"- Goals: {user_profile['goals']}\n"
        if user_profile.get('focus_areas'):
            context += f"- Focus Areas: {', '.join(user_profile['focus_areas'])}\n"
        
        base_prompt += context
    
    # Add recent chat history for context
    if chat_history:
        base_prompt += "\nRecent conversation:\n"
        for msg in chat_history[-3:]:  # Last 3 messages
            base_prompt += f"{msg['role']}: {msg['content']}\n"
    
    base_prompt += f"\nUser's current question/message: {user_input}\n"
    base_prompt += """
    Provide a helpful response that:
    1. Addresses their specific question or concern
    2. Gives actionable advice appropriate for their experience level
    3. Includes a follow-up question to continue the conversation
    4. Stays under 150 words
    5. Maintains a warm, professional coaching tone
    """
    
    return base_prompt

def save_conversation_log(user_profile: Dict[str, Any], chat_history: List[Dict]) -> None:
    """Save conversation for CRM purposes (simplified version)"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_profile': user_profile,
            'conversation_length': len(chat_history),
            'topics_discussed': extract_topics_from_chat(chat_history),
            'user_questions': [msg['content'] for msg in chat_history if msg['role'] == 'user']
        }
        
        # In a real implementation, save to database
        # For now, we'll just store in session state
        if 'conversation_logs' not in st.session_state:
            st.session_state.conversation_logs = []
        
        st.session_state.conversation_logs.append(log_entry)
        
    except Exception as e:
        print(f"Error saving conversation log: {e}")

def extract_topics_from_chat(chat_history: List[Dict]) -> List[str]:
    """Extract main topics discussed in the conversation"""
    topics = []
    keywords = {
        'financial': ['money', 'investment', 'savings', 'budget', 'financial', 'wealth'],
        'career': ['job', 'career', 'promotion', 'work', 'professional'],
        'business': ['business', 'entrepreneur', 'startup', 'company'],
        'goals': ['goal', 'objective', 'target', 'plan', 'strategy'],
        'mindset': ['mindset', 'thinking', 'belief', 'attitude', 'confidence'],
        'time': ['time', 'productivity', 'schedule', 'management', 'efficiency']
    }
    
    all_text = ' '.join([msg['content'].lower() for msg in chat_history])
    
    for topic, words in keywords.items():
        if any(word in all_text for word in words):
            topics.append(topic)
    
    return topics

def validate_api_key(api_key: str) -> bool:
    """Validate if API key format looks correct"""
    if not api_key or api_key == "your_gemini_api_key_here":
        return False
    
    # Basic validation - Gemini API keys usually start with specific patterns
    if len(api_key) < 20:
        return False
    
    return True

def format_success_tip() -> str:
    """Return a random success tip for display"""
    tips = [
        "💡 Success Tip: Start each day by reviewing your top 3 priorities.",
        "💡 Wealth Wisdom: Pay yourself first - save before you spend.",
        "💡 Mindset Shift: View challenges as opportunities to grow stronger.",
        "💡 Time Hack: Use the 80/20 rule - focus on high-impact activities.",
        "💡 Network Secret: Always look for ways to help others succeed.",
        "💡 Investment Truth: Time in the market beats timing the market.",
        "💡 Leadership Lesson: Lead by example and others will follow.",
        "💡 Success Strategy: Track your progress to stay motivated."
    ]
    
    import random
    return random.choice(tips)

def calculate_session_stats(chat_history: List[Dict]) -> Dict[str, Any]:
    """Calculate statistics for the current session"""
    if not chat_history:
        return {'messages': 0, 'user_messages': 0, 'coach_responses': 0}
    
    user_messages = [msg for msg in chat_history if msg['role'] == 'user']
    coach_messages = [msg for msg in chat_history if msg['role'] == 'coach']
    
    return {
        'total_messages': len(chat_history),
        'user_messages': len(user_messages),
        'coach_responses': len(coach_messages),
        'avg_response_length': sum(len(msg['content']) for msg in coach_messages) / len(coach_messages) if coach_messages else 0,
        'session_duration': calculate_session_duration(chat_history)
    }

def calculate_session_duration(chat_history: List[Dict]) -> str:
    """Calculate how long the session has been active"""
    if not chat_history:
        return "0 minutes"
    
    first_msg = chat_history[0]['timestamp']
    last_msg = chat_history[-1]['timestamp']
    
    if isinstance(first_msg, str):
        first_msg = datetime.fromisoformat(first_msg)
    if isinstance(last_msg, str):
        last_msg = datetime.fromisoformat(last_msg)
    
    duration = last_msg - first_msg
    minutes = int(duration.total_seconds() / 60)
    
    if minutes < 1:
        return "Less than 1 minute"
    elif minutes == 1:
        return "1 minute"
    else:
        return f"{minutes} minutes"

def get_javascript_speech_component(text: str, voice_settings: Dict[str, Any] = None) -> str:
    """Generate JavaScript component for text-to-speech with enhanced voice options"""
    if not voice_settings:
        voice_settings = {
            'voice_speed': 0.8,
            'voice_pitch': 1.0, 
            'voice_type': 'caring',
            'auto_speak': True
        }
    
    clean_speech_text = clean_text(text)
    
    return f"""
    <script>
    function speakText() {{
        if ('speechSynthesis' in window) {{
            // Stop any currently playing speech
            speechSynthesis.cancel();
            
            var utterance = new SpeechSynthesisUtterance(`{clean_speech_text}`);
            utterance.rate = {voice_settings['voice_speed']};
            utterance.pitch = {voice_settings['voice_pitch']};
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
                var voiceType = '{voice_settings['voice_type']}';
                var selectedVoice = null;
                
                // Enhanced voice selection based on personality
                if (voiceType === 'caring') {{
                    selectedVoice = voices.find(voice => 
                        voice.lang.startsWith('en-') && 
                        (voice.name.includes('Female') || voice.name.includes('Karen') || 
                         voice.name.includes('Susan') || voice.name.includes('Victoria') ||
                         voice.name.includes('Samantha'))
                    );
                }} else if (voiceType === 'professional') {{
                    selectedVoice = voices.find(voice => 
                        voice.lang.startsWith('en-') && 
                        (voice.name.includes('Daniel') || voice.name.includes('Alex') ||
                         voice.name.includes('David') || voice.name.includes('Mark'))
                    );
                }} else if (voiceType === 'energetic') {{
                    selectedVoice = voices.find(voice => 
                        voice.lang.startsWith('en-') && 
                        (voice.name.includes('Zira') || voice.name.includes('Catherine') ||
                         voice.name.includes('Moira') || voice.name.includes('Fiona'))
                    );
                }} else if (voiceType === 'wise') {{
                    selectedVoice = voices.find(voice => 
                        voice.lang.startsWith('en-') && 
                        (voice.name.includes('George') || voice.name.includes('Bruce') ||
                         voice.name.includes('Arthur') || voice.name.includes('James'))
                    );
                }}
                
                // Fallback to best available English voice
                if (!selectedVoice) {{
                    selectedVoice = voices.find(voice => 
                        voice.lang.startsWith('en-') && 
                        (voice.quality === 'high' || voice.localService === true)
                    ) || voices.find(voice => voice.lang.startsWith('en-'));
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
            alert('Text-to-speech is not supported in this browser. Please try Chrome or Edge for best results.');
        }}
    }}
    
    // Auto-play if enabled
    var autoPlay = {str(voice_settings.get('auto_speak', True)).lower()};
    if (autoPlay) {{
        setTimeout(speakText, 800);
    }}
    </script>
    
    <div style="text-align: center; margin: 10px 0;">
        <button id="speakButton" onclick="speakText()" style="
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
        " onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 6px 20px rgba(40, 167, 69, 0.4)'" 
           onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 15px rgba(40, 167, 69, 0.3)'">
            🔊 Play Response
        </button>
    </div>
    """
