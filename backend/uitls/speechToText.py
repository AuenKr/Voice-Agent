import os
import io
from openai import OpenAI

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types

from dotenv import load_dotenv
load_dotenv()

# Set Google Cloud project ID
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

def transcribe_google_cloud(stream_file: str) -> str:
    """Transcribes audio from an audio file stream using Google Cloud Speech-to-Text API."""
    client = SpeechClient()

    # Read the audio file as bytes
    with open(stream_file, "rb") as f:
        audio_content = f.read()

    # Split the audio into smaller chunks (max 25,600 bytes per chunk)
    max_chunk_size = 25600  # Google Cloud limit
    stream = [
        audio_content[start: start + max_chunk_size]
        for start in range(0, len(audio_content), max_chunk_size)
    ]

    audio_requests = (
        cloud_speech_types.StreamingRecognizeRequest(audio=audio) for audio in stream
    )

    recognition_config = cloud_speech_types.RecognitionConfig(
        auto_decoding_config=cloud_speech_types.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="long",
    )
    
    streaming_config = cloud_speech_types.StreamingRecognitionConfig(
        config=recognition_config
    )

    config_request = cloud_speech_types.StreamingRecognizeRequest(
        recognizer=f"projects/{GOOGLE_CLOUD_PROJECT}/locations/global/recognizers/_",
        streaming_config=streaming_config,
    )

    def requests(config: cloud_speech_types.RecognitionConfig, audio: list):
        yield config
        yield from audio

    # Transcribes the audio into text
    responses_iterator = client.streaming_recognize(
        requests=requests(config_request, audio_requests)
    )

    responses = []
    transcript = ""
    for response in responses_iterator:
        responses.append(response)
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "

    return transcript.strip()


OPENAPI_MODEL="whisper-1"

def transcribe_whisper_api(audio_io: io.BytesIO) -> str:
    """Transcribes audio using OpenAI's Speech-to-Text API."""
    try:
        print("Started transcription")
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Reset the buffer position
        audio_io.seek(0)
        
        # Save the BytesIO object as a .wav file temporarily
        with open("temp_audio.wav", "wb") as temp_wav_file:
            temp_wav_file.write(audio_io.read())
        
        # Reopen the file to send it to OpenAI
        with open("temp_audio.wav", "rb") as wav_file:
            # OpenAI API request to transcribe the audio
            response = client.audio.transcriptions.create(
                model=OPENAPI_MODEL,  # OpenAI Whisper model
                file=wav_file,
                response_format="text",
                language="en"
            )

        print("Ended transcription")
        # Extract and return the transcription from the response
        transcript = response.strip()
        return transcript
    
    except Exception as e:
        print(f"Error during OpenAI transcription: {e}")
        return "Error during transcription."