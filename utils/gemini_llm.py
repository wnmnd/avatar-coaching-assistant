import google.generativeai as genai

def coaching_response(user_text: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "You are a friendly and empathetic coaching assistant. "
        "Give practical advice, sound motivational, and guide the user through Q&A. "
        f"User: {user_text}"
    )
    response = model.generate_content(prompt)
    return response.text
