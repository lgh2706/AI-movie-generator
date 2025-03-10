import os
import openai
import streamlit as st

# Load API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = API_KEY

# Function to generate movie script using OpenAI's new API format
def generate_movie_script(user_prompt):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional Hollywood screenwriter. Write a creative, engaging movie script with scenes, characters, and dialogue."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("🎬 AI Movie Generator")
st.subheader("Generate AI-powered movie scripts in seconds!")

# User input for movie idea
user_prompt = st.text_input("Enter your movie idea:", "A sci-fi adventure on Mars")

if st.button("Generate Movie Script"):
    if user_prompt:
        script = generate_movie_script(user_prompt)
        st.text_area("Generated Movie Script", script, height=400)
    else:
        st.warning("Please enter a movie idea before generating.")

st.markdown("🚀 *Powered by OpenAI GPT-4*")
