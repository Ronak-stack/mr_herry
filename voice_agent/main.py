import asyncio

# load speech recognition
import speech_recognition as sr
from openai import OpenAI, AsyncOpenAI
from openai.helpers import LocalAudioPlayer

from dotenv import load_dotenv
import os
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
async_client = AsyncOpenAI()

async def ai_speaker(speech:str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="ash",
        input=speech,
        instructions="Always speak in cheerfull manner with full of delight and happy",
        response_format="pcm"
    ) as response:
        await LocalAudioPlayer().play(response)


def main():
    # store a recorgnizer object in a varibale
    r = sr.Recognizer()

    # access user's microphone as source of input
    with sr.Microphone() as source: # Mic access

        SYSTEM_PROMPT = f"""
                    You're an expert voice agent. You are given the trasnscript of what user has side using voice.
                    You need to output as if you are an voice agent and whatever you speak will be converted back to audio using AI and played back to user. 
                    """
        message = [{"role":"system", "content":SYSTEM_PROMPT}]
        while True:

            # apply noise cancelition using recorginzer
            r.adjust_for_ambient_noise(source)

            # set the time when recognie user's statment
            r.pause_threshold = 2 # 2 is denoate 2 second

            # load/get user's audio or statement
            print("Speak something....")
            audio = r.listen(source)

            # Start processing audio...(STT)..
            print("Start processing audio...(STT)..")
            stt = r.recognize_google(audio)

            print("You said:",stt)

            message.append({"role":"user", "content":stt})

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=message
            )

            # print(f"AI Bot:{response.choices[0].message.content}")
            asyncio.run(ai_speaker(response.choices[0].message.content))

main()