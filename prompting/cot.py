# Chain of thought

from openai import OpenAI
from dotenv import load_dotenv
import os
import json

#load env file
load_dotenv()
# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
    You're an expert AI assistant in resolving user queries using chain of thought.
    You work on Start, plan and output steps.
    You need to first plan what needs to be done. The plan can be multiple steps. Once you think enough plan has been done, finally you can given an Output.

    Rules:
    - Strictly follow the given JSON output format
    - Only run one step at a time.
    - The sequence of step is start (where user given an input), plan (That can be multiple times) and finally output (which is going to the displayed to the user).

    Output JSON Format:
    {"step":"START" | "PLAN" | "OUTPUT, "content":"string"}

    Example:
    START: Hey, Can you solve 2 + 3 * 5 / 10
    PLAN: {"step":"PLAN". "content":"Seems like user is intereseted in math problem"}
    PLAN: {"step":"PLAN". "content":"looking at the problem, we should solve this uding bodmos method"}
    PLAN: {"step":"PLAN", "content:"Yes, the BODMAS, is correct thing to be done here"}
    PLAN: {"step":"PLAN", "content":"First we must mulltiply 3*5 which is 15"}
    PLAN: {"step":"PLAN", "content":"Now the new equation is 2+15 / 10  }"}
    PLAN: {"step":"PLAN", "content":"We must perform divide that is 15/10 = 1.5%"}
    PLAN: {"step":"PLAN", "content":"Now the new quatitce is 2+1.5 "}
    PLAN: {"step":"PLAN". "content":"Now Finally lets perfor the added"}
    OUTPUT: {"step":"OUTPUT", "content":"3.5"}
"""

print("\n\n\n\n\n\n")

message_history = [{"role":"system", "content":SYSTEM_PROMPT}]
user_query = input("")
message_history.append({"role":"user", "content":user_query})
while True:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type":"json_object" },
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            # {"role": "user", "content": "Please tell me about bin-bang theory"}
            {"role": "user", "content": "Please writing the python code which can find sum of n number "},
            # Manually keep adding messages to history
            {"role":"assistant", "content": json.dumps({"step":"PLAN", "content":"The user wants a Python code to find the sum of n numbers."})},
            {"role":"assistant", "content": json.dumps({"step": "PLAN", "content": "First, clarify whether the user means sum of first n natural numbers or sum of arbitrary n numbers input by the user."})},
            {"role":"assistant", "content": json.dumps({"step": "PLAN", "content": "Assuming the user wants to sum the first n natural numbers as it is the most common interpretation."})}
        ]
    )
    raw_result = (response.choices[0].message.content)
    message_history.append({"role":"assistant", "content":raw_result})
    parsed_result = json.loads(raw_result)
    if parsed_result.get("step") == "START":
        print("Starting LLM loop:", parsed_result.get("content"))
        continue
    
    if parsed_result.get("step") == "PLAN":
        print("Planning LLM loop:", parsed_result.get("content"))
        continue

    if parsed_result.get("step") == "OUTPUT":
        print("Output:", parsed_result.get("content"))
        break