import os
import openai
import streamlit as st

# Load API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = API_KEY

# Function to generate movie script
def generate_movie_script(user_prompt):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Hollywood screenwriter. Write a detailed, engaging movie script including scenes, characters, and dialogue."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

# Function to generate AI image (scene or character)
def generate_movie_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

# Streamlit UI
st.title("🎬 AI Movie Generator")
st.subheader("Generate AI-powered movie scripts with visuals!")

# User input for movie idea
user_prompt = st.text_input("Enter your movie idea:", "A sci-fi adventure on Mars")

if st.button("Generate Movie Script & Image"):
    if user_prompt:
        # Generate the movie script
        script = generate_movie_script(user_prompt)
        st.text_area("Generated Movie Script", script, height=400)
        
        # Generate the first AI-generated scene image
        image_prompt = f"An epic scene from the movie: {user_prompt}"
        image_url = generate_movie_image(image_prompt)
        
        # Display image
        st.image(image_url, caption="AI-Generated Movie Scene", use_column_width=True)
    else:
        st.warning("Please enter a movie idea before generating.")

st.markdown("🚀 *Powered by OpenAI GPT-4 & DALL·E 3*")
