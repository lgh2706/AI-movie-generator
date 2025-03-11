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
def generate_ai_video(image_url, output_file="ai_movie_trailer.mp4"):
    print("🎬 Starting AI video generation with Runway Gen-2...")

    # ✅ Ensure the image URL is HTTPS and valid
    if not image_url.startswith("https://"):
        print(f"❌ Error: Invalid image URL → {image_url}")
        return None

    # ✅ Check if the image is accessible
    print(f"🔍 Verifying image URL: {image_url}")
    image_check = requests.head(image_url)
    if image_check.status_code != 200:
        print(f"❌ Error: Image URL returned {image_check.status_code}, not 200 OK")
        return None

    # ✅ Correct API endpoint for image-to-video generation
    runway_url = "https://api.runwayml.com/v1/video/generate"

    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Runway-Version": "2024-11-06",  # ✅ Ensure correct API version
        "Content-Type": "application/json"
    }

    data = {
        "prompt": "A cinematic AI-generated sci-fi movie scene",  # AI-generated video description
        "promptImage": [
            {
                "uri": image_url,  # ✅ Ensure valid image URL is provided
                "position": "first"
            }
        ],
        "ratio": "1280:768",  # ✅ Ensure correct resolution format
        "motion": "cinematic",  # ✅ Motion type
        "duration": 10,  # ✅ 10 seconds
        "fps": 24  # ✅ Frames per second
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
st.title("🎬 AI Movie Generator")
st.subheader("Generate AI-powered movie scripts with visuals, narration & music!")

# User input for movie idea
user_prompt = st.text_input("Enter your movie idea:", "A cyberpunk heist thriller")

if st.button("Generate Movie Script & Image"):
    if user_prompt:
        # Generate and store the movie script
        st.session_state.movie_script = generate_movie_script(user_prompt)
        
        # Generate and store the AI-generated scene image
        image_prompt = f"An epic scene from the movie: {user_prompt}"
        st.session_state.movie_image_url = generate_movie_image(image_prompt)

        # Generate AI voice narration
        st.session_state.audio_file = generate_voice_narration(st.session_state.movie_script)

# Display the stored script
if st.session_state.movie_script:
    st.text_area("Generated Movie Script", st.session_state.movie_script, height=400)

# Display the stored image
if st.session_state.movie_image_url:
    st.image(st.session_state.movie_image_url, caption="AI-Generated Movie Scene", use_container_width=True)




# Play AI voice narration
if st.session_state.audio_file:
    st.audio(st.session_state.audio_file, format="audio/mp3")




# Generate and play AI movie trailer
if st.button("Generate AI Movie Trailer"):
    print("🎬 'Generate AI Movie Trailer' button clicked!")

    if st.session_state.movie_script:
        print("✅ Movie script exists! Sending to Runway Gen-2 for video generation...")

        # ✅ Generate the video using Runway API
        video_path = generate_ai_video(st.session_state.movie_script)

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







st.markdown("🚀 *Powered by OpenAI GPT-4, DALL·E 3, ElevenLabs, and Riffusion*")
