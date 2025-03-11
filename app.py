import os
import openai
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import requests
import elevenlabs
import cv2
import time
import numpy as np
from pydub import AudioSegment

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Initialize session state to store script, image, music, and video
if "movie_script" not in st.session_state:
    st.session_state.movie_script = ""
if "movie_image_url" not in st.session_state:
    st.session_state.movie_image_url = ""
if "movie_image_path" not in st.session_state:
    st.session_state.movie_image_path = ""  # ✅ Initialize movie_image_path
if "audio_file" not in st.session_state:
    st.session_state.audio_file = ""
if "music_file" not in st.session_state:
    st.session_state.music_file = ""
if "video_file" not in st.session_state:
    st.session_state.video_file = ""


# Function to generate movie script using OpenAI GPT-4
def generate_movie_script(user_prompt):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Hollywood screenwriter. Write a detailed, engaging movie script including scenes, characters, and dialogue."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

# Function to generate AI image (scene or character) using DALL·E
def generate_movie_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

# Function to generate AI voice narration using ElevenLabs
def generate_voice_narration(text):
    audio = elevenlabs.generate(
        text=text,
        voice="Roger",  # Replace with a valid voice from ElevenLabs
        model="eleven_multilingual_v2",
        api_key=ELEVENLABS_API_KEY
    )

    # Save the generated voice file
    audio_file = "ai_voice_narration.mp3"
    with open(audio_file, "wb") as f:
        f.write(audio)

    return audio_file



import requests
import os
import time

# Define the base directory for generated files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, "generated_files")

# ✅ Ensure the directory exists
if not os.path.exists(GENERATED_DIR):
    os.makedirs(GENERATED_DIR)

# ✅ Runway API Key (Loaded from Render environment variables)
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")

# ✅ Function to generate AI video using Runway Gen-2
def generate_ai_video(output_file="ai_movie_trailer.mp4"):
    print("🎬 Starting AI video generation with Runway Gen-2...")

    # ✅ Ensure the locally saved image file exists
    image_path = os.path.join(GENERATED_DIR, "movie_scene.png")
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found at {image_path}")
        return None

    print(f"🔍 Using local image file: {image_path}")

    # ✅ Convert local image to a base64 Data URI (required by Runway)
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    data_uri = f"data:image/png;base64,{encoded_image}"

    # ✅ Correct API endpoint for image-to-video generation
    runway_url = "https://api.runwayml.com/v1/video/generate"

    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Runway-Version": "2024-11-06",
        "Content-Type": "application/json"
    }

    data = {
        "prompt": "A cinematic AI-generated sci-fi movie scene",
        "promptImage": [
            {
                "uri": data_uri,  # ✅ Use base64-encoded image
                "position": "first"
            }
        ],
        "ratio": "1280:768",
        "motion": "cinematic",
        "duration": 10,
        "fps": 24
    }

    print("🚀 Sending request to Runway API...")
    response = requests.post(runway_url, headers=headers, json=data)

    if response.status_code == 200:
        video_url = response.json().get("video_url")
        if not video_url:
            print("❌ Error: No video URL returned from Runway.")
            return None

        print(f"✅ AI-generated video available at: {video_url}")

        # ✅ Download the AI-generated video
        output_path = os.path.join(GENERATED_DIR, output_file)
        video_response = requests.get(video_url, stream=True)
        if video_response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"✅ AI-generated video saved: {output_path}")
            return output_path
        else:
            print("❌ Error: Failed to download the AI-generated video.")
            return None
    else:
        print(f"❌ Runway API request failed. Response Code: {response.status_code}")
        print(f"🔴 API Response: {response.text}")
        return None











# Streamlit UI
st.title("🎬 Neural Flicks")
st.subheader("Generate AI-powered movie scripts & movie trailer!")

# User input for movie idea
user_prompt = st.text_input("Enter your movie idea:", "A cyberpunk heist thriller")

if st.button("Generate Movie Script & Image"):
    if user_prompt:
        # ✅ Generate and store the movie script
        st.session_state.movie_script = generate_movie_script(user_prompt)

        # ✅ Save the script as a .txt file
        script_filename = os.path.join(GENERATED_DIR, "movie_script.txt")
        with open(script_filename, "w", encoding="utf-8") as script_file:
            script_file.write(st.session_state.movie_script)
        print(f"✅ Movie script saved: {script_filename}")

        # ✅ Generate and store the AI-generated scene image
        image_prompt = f"An epic scene from the movie: {user_prompt}"
        image_url = generate_movie_image(image_prompt)

        # ✅ Download and save the image locally
        image_filename = os.path.join(GENERATED_DIR, "movie_scene.png")
        image_response = requests.get(image_url, stream=True)
        if image_response.status_code == 200:
            with open(image_filename, "wb") as image_file:
                image_file.write(image_response.content)
            print(f"✅ AI-generated image saved: {image_filename}")
            st.session_state.movie_image_path = image_filename  # Store local path instead of URL
        else:
            print("❌ Error: Failed to download AI-generated image.")
            st.session_state.movie_image_path = ""

# ✅ Display the stored script
if st.session_state.movie_script:
    st.text_area("Generated Movie Script", st.session_state.movie_script, height=400)

# ✅ Display the locally saved image
if st.session_state.movie_image_path and os.path.exists(st.session_state.movie_image_path):
    st.image(st.session_state.movie_image_path, caption="AI-Generated Movie Scene", use_container_width=True)




# Play AI voice narration
if st.session_state.audio_file:
    st.audio(st.session_state.audio_file, format="audio/mp3")




# Generate and play AI movie trailer
if st.button("Generate AI Movie Trailer"):
    print("🎬 'Generate AI Movie Trailer' button clicked!")

    if st.session_state.movie_image_url:
        print("✅ Movie image exists! Sending to Runway Gen-2 for video generation...")

        # ✅ Generate the video using Runway API
        video_path = generate_ai_video(st.session_state.movie_image_url)

        # ✅ Debug: Check if the video file exists
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            print(f"✅ AI-generated video found: {video_path} (Size: {file_size} bytes)")

            # ✅ Play the video in Streamlit
            with open(video_path, "rb") as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)

            # ✅ Provide a download button for the video
            st.download_button("📥 Download AI Movie Trailer", video_bytes, file_name="ai_movie_trailer.mp4", mime="video/mp4")

        else:
            print("❌ AI video generation failed!")
            st.warning("Failed to generate AI video. Please try again.")

    else:
        print("❌ No movie script found! Can't generate video.")
        st.warning("Generate a movie script first!")







st.markdown("🚀 *Powered by OpenAI GPT-4, DALL·E 3, ElevenLabs, and Runway AI*")
