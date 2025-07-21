"""
Configuration settings for the Avatar Success Coach application
"""

import os
from typing import Dict, Any

class Config:
    """Application configuration class"""
    
    # App settings
    APP_NAME = "Avatar Success Coach"
    APP_ICON = "🎯"
    VERSION = "1.0.0"
    
    # AI Model settings
    GEMINI_MODELS = [
        "gemini-2.0-flash",      # Latest stable model (recommended)  
        "gemini-1.5-flash",      # Fallback option
        "gemini-1.5-pro"         # Final fallback
    ]
    MAX_TOKENS = 200
    TEMPERATURE = 0.7
    
    # Speech settings
    SPEECH_LANG = "en-US"
    TTS_RATE = 0.8
    TTS_PITCH = 1.0
    TTS_VOLUME = 1.0
    
    # Chat settings
    MAX_CHAT_HISTORY = 10
    MAX_CONTEXT_MESSAGES = 5
    
    # Avatar settings
    AVATAR_EMOJI = "🎯"
    ANIMATION_DURATION = 2000  # milliseconds
    
    # Coaching focus areas
    FOCUS_AREAS = [
        "Financial Planning",
        "Career Growth",
        "Entrepreneurship",
        "Investment Strategy",
        "Time Management",
        "Leadership Skills",
        "Networking",
        "Personal Development",
        "Mindset Development",
        "Goal Setting",
        "Risk Management",
        "Wealth Building"
    ]
    
    # Experience levels
    EXPERIENCE_LEVELS = [
        "Beginner",
        "Intermediate", 
        "Advanced"
    ]
    
    @staticmethod
    def get_api_key(key_name: str) -> str:
        """Get API key from environment variables or Streamlit secrets"""
        try:
            import streamlit as st
            return st.secrets.get(key_name) or os.getenv(key_name)
        except:
            return os.getenv(key_name)
    
    @staticmethod
    def get_coaching_prompt() -> str:
        """Get the base coaching prompt"""
        return """
        You are an expert Success and Wealth Coach with years of experience helping people achieve their financial and personal goals. Your coaching style is:

        EXPERTISE AREAS:
        - Wealth Building & Financial Planning
        - Entrepreneurship & Business Development  
        - Goal Setting & Achievement Strategies
        - Mindset & Personal Development
        - Time Management & Productivity
        - Investment Strategies & Risk Management
        - Leadership Development
        - Network Building & Relationship Management

        CORE PRINCIPLES:
        1. Success requires consistent daily actions and disciplined habits
        2. True wealth encompasses financial freedom, time freedom, and life purpose
        3. Mindset is the foundation of all achievement
        4. Everyone can improve their situation with the right strategy and commitment
        5. Progress should be measured and celebrated regularly

        COACHING APPROACH:
        - Ask thoughtful questions to understand the client's current situation
        - Provide specific, actionable advice tailored to their level
        - Use real-world examples and analogies to illustrate concepts
        - Balance encouragement with realistic expectations
        - Focus on both immediate steps and long-term vision
        - Always end responses with a question or call-to-action to maintain engagement

        TONE & STYLE:
        - Professional but warm and approachable
        - Confident and knowledgeable without being condescending
        - Encouraging and motivational
        - Direct and practical
        - Conversational and engaging

        Keep responses under 150 words for better engagement. Always aim to provide value while keeping the conversation flowing.
        """

# Coaching knowledge base from the uploaded document
COACHING_KNOWLEDGE = """
CORE SUCCESS PRINCIPLES:

Success and wealth do not come overnight. They are results of daily disciplined actions, consistent learning, and a relentless drive for progress. To become truly rich—not just in money, but in time, purpose, and freedom—requires you to elevate your habits, mindset, and strategy.

KEY AREAS OF FOCUS:

1. MINDSET OF THE WEALTHY
- Develop abundance thinking
- Embrace continuous learning
- Maintain long-term perspective
- Build resilience and persistence

2. GOAL SETTING & CLARITY
- Set specific, measurable objectives
- Break down big goals into actionable steps
- Regular review and adjustment
- Accountability systems

3. FINANCIAL EDUCATION
- Understand money fundamentals
- Learn about different investment vehicles
- Develop financial literacy
- Master budgeting and cash flow

4. TIME MANAGEMENT MASTERY
- Prioritize high-impact activities
- Eliminate time wasters
- Use productivity systems
- Focus on what matters most

5. NETWORKING & MENTORSHIP
- Build valuable relationships
- Seek guidance from successful people
- Provide value to others
- Join professional communities

6. SMART SAVING & INVESTING
- Pay yourself first
- Diversify investments
- Understand risk vs reward
- Long-term wealth building

7. MULTIPLE INCOME STREAMS
- Reduce dependency on single source
- Build passive income
- Leverage skills and knowledge
- Scale existing income sources

8. ENTREPRENEURSHIP BASICS
- Identify market opportunities
- Start small and test ideas
- Focus on solving problems
- Build systems and processes

9. DAILY HABITS OF SUCCESS
- Morning routines
- Continuous reading and learning
- Regular exercise and health maintenance
- Consistent review and planning

10. OVERCOMING OBSTACLES
- Learn from failures
- Handle criticism constructively
- Maintain confidence during setbacks
- Adapt strategies when needed
"""
