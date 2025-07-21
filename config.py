import os
import google.generativeai as genai

# Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# D-ID
D_ID_API_KEY = os.environ.get("D_ID_API_KEY")

# ElevenLabs (optional)
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
