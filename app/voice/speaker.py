from openai import OpenAI
import os
import base64

client = OpenAI()

def generate_audio(text: str, output_path: str = "report_audio.mp3"):
    """
    Generates audio for the full report and saves it to a file.
    Used for the final readout.
    """
    # Truncate if too long to save cost/time (optional)
    short_text = text[:4096] 
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=short_text
    )
    
    # Save to file
    response.stream_to_file(output_path)
    return output_path

def generate_audio_stream(text: str, index: int):
    """
    Generates audio for a single sentence chunk (for streaming).
    Returns base64 string for immediate playback.
    """
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    
    # Return base64 for browser playback
    audio_content = response.content
    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
    return audio_base64