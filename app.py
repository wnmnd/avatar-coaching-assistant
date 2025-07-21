import streamlit as st
from utils.gemini_llm import coaching_response
from utils.avatar_generator import generate_avatar_video

st.set_page_config(page_title="AI Coaching Avatar", page_icon="🤖")

st.title("🤖 AI Coaching Assistant")
st.write("Talk to your personal AI coach with a humanlike avatar!")

user_input = st.text_area("Ask me anything:")

if st.button("Get Coaching Advice"):
    if user_input:
        with st.spinner("Thinking..."):
            reply = coaching_response(user_input)
            st.subheader("Coach's Response:")
            st.write(reply)

            video_url = generate_avatar_video(reply)
            if video_url:
                st.subheader("Coach Avatar:")
                st.video(video_url)
            else:
                st.warning("Could not generate avatar video. Try again later.")
    else:
        st.warning("Please enter a question.")
