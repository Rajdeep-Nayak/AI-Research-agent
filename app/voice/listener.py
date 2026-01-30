from openai import OpenAI
import os

def transcribe_audio(audio_bytes):
    """
    Converts audio bytes to text using OpenAI Whisper.
    """
    client = OpenAI()
    
    # 1. Save bytes to a temporary file
    temp_filename = "temp_input.wav"
    with open(temp_filename, "wb") as f:
        f.write(audio_bytes)
        
    print("🎤 Transcribing audio...")
    
    # 2. Send to Whisper
    with open(temp_filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    
    # 3. Cleanup
    os.remove(temp_filename)
    
    return transcript.text