import os
import json
from .generateSpeech import generate_speech
from openai import OpenAI

# Instantiate OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Set OpenAI model to use (GPT-4)
OPENAI_MODEL = "gpt-4o"

async def generate_response_and_audio(transcribed_text, websocket):
    if not transcribed_text:
        await websocket.send_text(json.dumps({'type': 'text', 'content': "I'm sorry, I didn't catch that. Could you please repeat?"}))
        return

    system_prompt = """
      Task: Create a comprehensive and informative LLM assistant for Glasgow City Driving School's website.

      Context:
      
      Business: Glasgow City Driving School
      Location: Glasgow, United Kingdom
      Services: Beginner Driving Courses, Advanced Driving Lessons, Driving Theory Classes, Mock Driving Tests, Automatic and Manual Transmission Options, Refresher Courses
      Common Queries: Location details, operating hours, services offered, types of vehicles used, choosing the right driving course.
      Assistant's Role:
      
      Address common queries directly and efficiently.
      Provide concise and informative answers.
      Escalate complex or unusual queries to human customer service.
      Be polite, helpful, and informative in all interactions.
      Avoid making assumptions or providing false or misleading information.
      Assistant's Response Format:
      
      Direct Answer: If the query is straightforward, provide a clear and helpful response.
      Contact Information: If the query is beyond the assistant's scope, direct the user to the appropriate contact channel (e.g., phone number, email address).
      Example Query and Response:
      
      Query: "What are your operating hours?"
      Response: "Our driving school is open from [Start Time] to [End Time] on [Days of the Week]."
      Note: The assistant should be able to understand and respond to a variety of phrasings and variations of the common queries.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": transcribed_text}
    ]

    try:
        # Use the new OpenAI API to generate a response
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7
        )

        # Access the response from the assistant
        assistant_response = response.choices[0].message.content
        print(f"Assistant's response: {assistant_response}")

        # Send the assistant's response text to the client
        await websocket.send_text(json.dumps({'type': 'text', 'content': assistant_response}))
      
        # Convert the assistant's response to speech
        await generate_speech(assistant_response, websocket)

    except Exception as e:
        print(f"Error generating response: {e}")
        await websocket.send_text(json.dumps({'type': 'text', 'content': "I'm sorry, I couldn't process your request at this time."}))