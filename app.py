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
import ffmpeg
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



import ffmpeg
import cv2
import requests
import os
import time

# Function to generate AI video from images and narration
def generate_ai_video(image_url, audio_file, output_file="ai_movie_trailer.mp4"):
    print("🎬 Starting AI video generation...")

    # Ensure output_file is a valid string
    if not isinstance(output_file, str) or output_file.lower() in ["true", "false"]:
        output_file = "final_ai_movie_trailer.mp4"  # Set a valid default filename

    # Download AI-generated image
    image_response = requests.get(image_url, stream=True)
    if image_response.status_code == 200:
        with open("ai_scene.jpg", "wb") as f:
            f.write(image_response.content)
        print("✅ AI-generated image saved successfully!")
    else:
        print("❌ Error: Failed to download image.")
        return None

    # Load image and resize for video
    img = cv2.imread("ai_scene.jpg")
    if img is None:
        print("❌ Error: Failed to load AI-generated image.")
        return None

    height, width, _ = img.shape
    video_fps = 30
    duration = 10  # Force duration to be 10 seconds
    frame_count = video_fps * duration

    # Debug: Check frame count
    print(f"🟢 Generating {frame_count} frames for {duration} seconds at {video_fps} FPS")

    # Create a video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter("temp_video.mp4", fourcc, video_fps, (width, height))

    # Add frames with AI-generated image
    for _ in range(frame_count):
        video_writer.write(img)

    # Release the video writer properly
    video_writer.release()
    time.sleep(2)  # Ensure the file is written before proceeding

    # Debug: Check if video was generated
    if not os.path.exists("temp_video.mp4") or os.path.getsize("temp_video.mp4") == 0:
        print("❌ Error: temp_video.mp4 was not generated correctly!")
        return None

    # Ensure audio file exists before merging
    if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
        print("❌ Error: Audio file not found or is empty!")
        return None  # Stop execution if no valid audio file

    # Debug: Check if temp_video.mp4 exists before merging
    if not os.path.exists("temp_video.mp4"):
        print("❌ Error: Video file not found before merging!")
        return None  # Stop execution if no video file

    # Merge video and voice narration using FFmpeg
    try:
        print(f"🔄 Merging video and audio with FFmpeg... Output file: {output_file}")

        input_video = ffmpeg.input("temp_video.mp4")  # Video input
        input_audio = ffmpeg.input(audio_file)  # Audio input

        process = (
            ffmpeg
            .output(
                input_video,
                input_audio,
                output_file,
                vcodec="libx264",
                acodec="aac",
                format="mp4",
                shortest=True,  # Ensures video and audio end together
                audio_bitrate="192k"
            )
            .run(overwrite_output=True)
        )

        # Debugging: Check if the output file exists
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"✅ Video successfully generated: {output_file}")
            return output_file
        else:
            print("❌ Error: Video file was not generated!")
            return None

    except ffmpeg.Error as e:
        print("❌ FFmpeg error occurred")
        if e.stderr:
            print("FFmpeg error details:", e.stderr.decode("utf-8"))
        else:
            print("No FFmpeg stderr output available")
        return None  # Stop execution if FFmpeg fails



















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
    if st.session_state.movie_image_url and st.session_state.audio_file and "music_file" in st.session_state:
        st.session_state.video_file = generate_ai_video(st.session_state.movie_image_url, st.session_state.audio_file)
        st.video(st.session_state.video_file)
    else:
        st.warning("Generate script, image, narration, and music first!")

st.markdown("🚀 *Powered by OpenAI GPT-4, DALL·E 3, ElevenLabs, and Riffusion*")
