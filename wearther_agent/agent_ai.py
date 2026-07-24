import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
import json
from pydantic import BaseModel, Field
from typing import Optional

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example PLAN, OUTPUT")
    content: Optional[str] = Field(None, description="The optional string content")
    tool: Optional[str] = Field(None, description="The ID of the tool to call")
    input: Optional[str] = Field(None, description="")


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

available_tool = {
    "get_weather":get_weather
}


SYSTEM_PROMPT = """
    You're an expert AI assistant in resolving user queries using chain of thought.
    You work on Start, plan and output steps.
    You need to first plan what needs to be done. The plan can be multiple steps. Once you think enough plan has been done, finally you can given an Output.
    You can also call a tool if required from the list of available tools.
    for every tool call wait for the observe step which is the putput from the called tool

    Rules:
    - Strictly follow the given JSON output format
    - Only run one step at a time.
    - The sequence of step is start (where user given an input), plan (That can be multiple times) and finally output (which is going to the displayed to the user).

    Output JSON Format:
    {"step":"START" | "PLAN" | "OUTPUT | "TOOL" , "content":"string", "tool":"string", "input":"string"}

    Available Tools:
    - get_weather(city:str): Takes city name as input string and returns the weather report info about the city

    Example:
    START: What is the current weather of jaipur now?
    PLAN: {"step":"PLAN": "content":"Seems like user is intereseted in fetch weather report of jaipur"}
    PLAN: {"step":"PLAN": "content":"looking at the tool for get the weather details"}
    PLAN: {"step":"TOOL": "tool":"get_weather": "input":"Jaipur"}
    PLAN: {"step":"OBSERVE": "tool":"get_weather":"output":"The temp of jaipur is cloudy 50"}
    OUTPUT: {"step":"OUTPUT", "content":"35 C"}
    PLAN: {"step":"PLAN": "content":"I got the weather info about jaipur"}
    PLAN: {"step":"STOP": "content":"The current weather in deah"}
"""

print("\n\n\n\n\n\n")

message_history = [{"role":"system", "content":SYSTEM_PROMPT}]
user_query = input("")
message_history.append({"role":"user", "content":user_query})
while True:
    # response = client.chat.completions.create(
    #     model="gpt-4.1-mini",
    #     response_format={"type":"json_object" },
    #     messages=message_history
    # )
    response = client.chat.completions.parse(
        model="gpt-4.1-mini",
        response_format=MyOutputFormat,
        messages=message_history
    )
    # raw_result = (response.choices[0].message.content)
    raw_result = response.choices[0].message.content
    message_history.append({"role":"assistant", "content":raw_result})
    # parsed_result = json.loads(raw_result)
    parsed_result = response.choices[0].message.parsed
    if parsed_result.step == "START":
        print("Starting LLM loop:", parsed_result.content)
        continue

    if parsed_result.step == "TOOL":
        tool_to_call = parsed_result.tool
        tool_input = parsed_result.input
        print(f"tool_to_call: {tool_to_call} ({tool_input})")
        # print("Planning LLM loop:", parsed_result.content)
        # continue

        tool_response = available_tool[tool_to_call](tool_input)
        print(f"{tool_to_call} ({tool_input}) = {tool_response}")
        message_history.append({
            "role":"developer",
            "content":json.dumps({
                "step":"OBSERVE",
                "tool":tool_to_call,
                "input":tool_input,
                "output":tool_response
            })
        })
        continue

    if parsed_result.step == "PLAN":
        print("Planning LLM loop:", parsed_result.content)
        continue

    if parsed_result.step == "OUTPUT":
        print("Output:", parsed_result.content)
        break