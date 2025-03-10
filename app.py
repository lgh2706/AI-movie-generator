import os
import openai
import streamlit as st

# Load API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = API_KEY

# Function to generate movie script
def generate_movie_script(user_prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Hollywood screenwriter creating movie scripts."},
            {"role": "user", "content": f"Generate a detailed movie script for: {user_prompt}"}
        ],
        max_tokens=1000
    )
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("🎬 AI Movie Generator")
st.subheader("Generate AI-powered movie scripts in seconds!")

# User input for movie idea
user_prompt = st.text_input("Enter your movie idea:", "A cyberpunk heist thriller")

if st.button("Generate Movie Script"):
    if user_prompt:
        script = generate_movie_script(user_prompt)
        st.text_area("Generated Movie Script", script, height=400)
    else:
        st.warning("Please enter a movie idea before generating.")

st.markdown("🚀 *Powered by OpenAI GPT-4*")
