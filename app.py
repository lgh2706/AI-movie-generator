import os
import openai
import streamlit as st
import requests
import elevenlabs
import base64
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pydub import AudioSegment

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
openai.api_key = OPENAI_API_KEY

# Define the base directory for generated files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, "generated_files")

# Ensure the directory exists
if not os.path.exists(GENERATED_DIR):
    os.makedirs(GENERATED_DIR)

# Function to generate movie script and save it
def generate_movie_script(user_prompt):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Hollywood screenwriter. Write a detailed, engaging movie script including scenes, characters, and dialogue."},
            {"role": "user", "content": user_prompt}
        ]
    )
    script_content = response.choices[0].message.content
    script_path = os.path.join(GENERATED_DIR, "movie_script.txt")
    with open(script_path, "w", encoding="utf-8") as script_file:
        script_file.write(script_content)
    return script_path

# Function to generate AI image and save it
def generate_movie_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    image_path = os.path.join(GENERATED_DIR, "movie_scene.png")
    
    image_response = requests.get(image_url, stream=True)
    if image_response.status_code == 200:
        with open(image_path, "wb") as f:
            f.write(image_response.content)
        return image_path
    return None

# Function to generate AI voice narration and save it
def generate_voice_narration(text):
    audio = elevenlabs.generate(
        text=text,
        voice="Roger",
        model="eleven_multilingual_v2",
        api_key=ELEVENLABS_API_KEY
    )
    audio_path = os.path.join(GENERATED_DIR, "ai_voice_narration.mp3")
    with open(audio_path, "wb") as f:
        f.write(audio)
    return audio_path

# Function to generate AI video and save it
def generate_ai_video():
    image_path = os.path.join(GENERATED_DIR, "movie_scene.png")
    if not os.path.exists(image_path):
        return None

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    data_uri = f"data:image/png;base64,{encoded_image}"
    
    runway_url = "https://api.runwayml.com/v1/image-to-video"
    headers = {"Authorization": f"Bearer {RUNWAY_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": "A cinematic AI-generated sci-fi movie scene", "promptImage": [{"uri": data_uri, "position": "first"}], "ratio": "1280:768", "motion": "cinematic", "duration": 10, "fps": 24}
    
    response = requests.post(runway_url, headers=headers, json=data)
    if response.status_code == 200:
        video_url = response.json().get("video_url")
        if not video_url:
            return None
        
        video_path = os.path.join(GENERATED_DIR, "ai_movie_trailer.mp4")
        video_response = requests.get(video_url, stream=True)
        if video_response.status_code == 200:
            with open(video_path, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=1024):
                    f.write(chunk)
            return video_path
    return None

# Streamlit UI
st.title("🎬 Neural Flicks")
st.subheader("Generate AI-powered movie scripts & trailers!")

user_prompt = st.text_input("Enter your movie idea:", "A cyberpunk heist thriller")
if st.button("Generate Movie Script & Image"):
    if user_prompt == "A cyberpunk heist thriller":
        st.warning("Using pre-generated files for demo...")
        time.sleep(10)  # Wait for 10 seconds
        script_path = os.path.join(GENERATED_DIR, "movie_script.txt")
        image_path = os.path.join(GENERATED_DIR, "movie_scene.png")
    else:
        if user_prompt:
            script_path = generate_movie_script(user_prompt)
            image_path = generate_movie_image(f"An epic scene from the movie: {user_prompt}")
        else:
            st.warning("Please enter a movie idea!")
    if user_prompt == "A cyberpunk heist thriller":
        st.warning("Using pre-generated files for demo...")
        time.sleep(10)  # Wait for 10 seconds
        script_path = os.path.join(GENERATED_DIR, "movie_script.txt")
        image_path = os.path.join(GENERATED_DIR, "movie_scene.png")
    else:
        script_path = generate_movie_script(user_prompt)
        image_path = generate_movie_image(f"An epic scene from the movie: {user_prompt}")
    if user_prompt == "A cyberpunk heist thriller":
        st.warning("Using pre-generated files for demo...")
        time.sleep(10)  # Wait for 10 seconds
        script_path = os.path.join(GENERATED_DIR, "movie_script.txt")
        image_path = os.path.join(GENERATED_DIR, "movie_scene.png")
    else:
            script_path = generate_movie_script(user_prompt)
            image_path = generate_movie_image(f"An epic scene from the movie: {user_prompt}")
    
    if script_path:
        with open(script_path, "r", encoding="utf-8") as file:
            script_text = file.read()
        st.text_area("Generated Movie Script", script_text, height=400)
    
    if image_path:
        st.image(image_path, caption="AI-Generated Movie Scene", use_container_width=True)

if st.button("Generate AI Voice Narration"):
    if user_prompt == "A cyberpunk heist thriller":
        st.warning("Using pre-generated voice narration for demo...")
        time.sleep(10)  # Wait for 10 seconds
        audio_path = os.path.join(GENERATED_DIR, "ai_voice_narration.mp3")
    else:
        script_path = os.path.join(GENERATED_DIR, "movie_script.txt")
        if os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as file:
                script_text = file.read()
            audio_path = generate_voice_narration(script_text)
            st.audio(audio_path, format="audio/mp3")
        else:
            st.warning("No script found! Generate a script first.")
    if user_prompt == "A cyberpunk heist thriller":
        st.warning("Using pre-generated voice narration for demo...")
        time.sleep(10)  # Wait for 10 seconds
        audio_path = os.path.join(GENERATED_DIR, "ai_voice_narration.mp3")
    else:
        script_path = os.path.join(GENERATED_DIR, "movie_script.txt")
        if os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as file:
                script_text = file.read()
            audio_path = generate_voice_narration(script_text)
            st.audio(audio_path, format="audio/mp3")
    if user_prompt == "A cyberpunk heist thriller":
        st.warning("Using pre-generated voice narration for demo...")
        time.sleep(10)  # Wait for 10 seconds
        audio_path = os.path.join(GENERATED_DIR, "ai_voice_narration.mp3")
    else:
        script_path = os.path.join(GENERATED_DIR, "movie_script.txt")
        if os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as file:
                script_text = file.read()
            audio_path = generate_voice_narration(script_text)
    if user_prompt == "A cyberpunk heist thriller":
        st.warning("Using pre-generated voice narration for demo...")
        time.sleep(10)  # Wait for 10 seconds
        audio_path = os.path.join(GENERATED_DIR, "ai_voice_narration.mp3")
    else:
    script_path = os.path.join(GENERATED_DIR, "movie_script.txt")
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as file:
            script_text = file.read()
                audio_path = generate_voice_narration(script_text)
        st.audio(audio_path, format="audio/mp3")

if st.button("Generate AI Movie Trailer"):
    if user_prompt == "A cyberpunk heist thriller":
        st.warning("Using pre-generated AI movie trailer for demo...")
        time.sleep(10)  # Wait for 10 seconds
        video_path = os.path.join(GENERATED_DIR, "ai_movie_trailer.mp4")
    else:
        image_path = os.path.join(GENERATED_DIR, "movie_scene.png")
        if os.path.exists(image_path):
            video_path = generate_ai_video()
            if video_path:
                with open(video_path, "rb") as video_file:
                    video_bytes = video_file.read()
                    st.video(video_bytes)
                    st.download_button("📥 Download AI Movie Trailer", video_bytes, file_name="ai_movie_trailer.mp4", mime="video/mp4")
            else:
                st.warning("Failed to generate AI video. Please try again.")
        else:
            st.warning("No movie image found! Generate an image first.")
    video_path = generate_ai_video()
    if video_path:
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
            st.video(video_bytes)
            st.download_button("📥 Download AI Movie Trailer", video_bytes, file_name="ai_movie_trailer.mp4", mime="video/mp4")

st.markdown("🚀 *Powered by OpenAI GPT-4, DALL·E 3, ElevenLabs, and Runway AI*")
