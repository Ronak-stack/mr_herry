# Few shot prompting
# Few shot prompting: The model is provided with a few examples before asking it to generate a response.

from openai import OpenAI
from dotenv import load_dotenv
import os

#load env file
load_dotenv()
# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You should only and only answer the coding related questions. Do not answer anything else. Your name is Alexa. If user asks something other then coding just say sorry.

Example:
Q: Can you explain the a+b whole suare?
A: Sorry, I can only help with coding related questions.

Q: Hey, Write a code in python for adding two numbers.
A: def add(a,b):
        return(a+d)
"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        # {"role": "user", "content": "Please tell me about bin-bang theory"}
        {"role": "user", "content": "Please writing the python code which work like a curl of php and fetch the home page detail of given website url"}
    ]
)

print(response.choices[0].message.content)