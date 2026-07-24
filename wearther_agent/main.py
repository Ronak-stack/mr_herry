import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
#load env file
load_dotenv()
# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_weather(city:str):
    url = f"https://wttr.in/{city.lower()}?format=%c+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    else:
        return f"Something went wrong"

def main():
    user_query = input("Ask your question>")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user", "content":user_query}]
    )

    print(f"Bot:{response.choices[0].message.content}")

main()
