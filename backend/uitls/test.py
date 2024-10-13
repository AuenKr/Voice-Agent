import os
import json
import io
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

load_dotenv()
OPENAPI_MODEL="whisper-1"
      
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="nova",
  input="Today is a wonderful day to build something people love!"
)

response.stream_to_file(speech_file_path)