import os
import json
import io
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def generate_speech(text, websocket):
    try:
        print("Started generating speech part")
        # Use OpenAI's new TTS API to generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",  # You can change the voice model as needed
            input=text,
        )
        print("Generated the speech part")
        # Create a BytesIO object to store the binary audio response
        audio_io = io.BytesIO()

        # Write the binary audio content directly to BytesIO
        audio_io.write(response.content)

        # Reset the buffer's position to the beginning
        audio_io.seek(0)

        # Send the generated audio as bytes to the websocket client
        await websocket.send_bytes(audio_io.getvalue())
    except Exception as e:
        print(f"Error generating speech: {e}")
        await websocket.send_text(json.dumps({'type': 'text', 'content': "Error generating speech."}))