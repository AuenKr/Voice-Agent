import io
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment

from dotenv import load_dotenv
load_dotenv()

from uitls.speechToText import transcribe_whisper_api
from uitls.generateResponse import generate_response_and_audio

app = FastAPI()

# CORS configuration (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        print("Started receiving audio file")
        while True:
            # Receive the audio file from the client
            data = await websocket.receive_bytes()
            audio_data = io.BytesIO(data)

            print("Processing received audio chunk...")
            # Convert audio data to WAV format with 16-bit, 16kHz, mono
            audio_segment = AudioSegment.from_file(audio_data, format="webm")
            audio_segment = audio_segment.set_frame_rate(16000).set_sample_width(2).set_channels(1)
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)

            # Transcribe audio data using OpenAI SST API
            transcription = await asyncio.to_thread(transcribe_whisper_api, wav_io)
            print(f"Transcribed text: {transcription}")

            print("Send transcribe chunk to frontend")
            # Send the transcription to the client
            await websocket.send_text(json.dumps({'type': 'text', 'content': transcription}))

            print("Started generation response for user")
            # Stream GPT-4 response and TTS audio back to the client (generated audio as bytes)
            await generate_response_and_audio(transcription, websocket)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
    finally:
        await websocket.close()
