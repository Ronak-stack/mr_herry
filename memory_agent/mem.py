import os
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

config = {
    "version":"v1.1",
    "embedder":{
        "provider":"openai",
        "config":{"api_key":os.getenv("OPENAI_API_KEY"), "model":"text-embedding-3-small"}
    },
    "llm":{
        "provider":"openai",
        "config":{"api_key":os.getenv("OPENAI_API_KEY"), "model":"gpt-4.1"}
    },
    "graph_store":{
        "provider":"neo4j",
        "config":{
            "url":os.getenv("neo4j_connection_uri"),
            "username":os.getenv("neo4j_aura_username"),
            "password":os.getenv("neo4j_aura_password")
        }
    },
    "vector_store":{
        "provider":"qdrant",
        "config":{
            "host":"localhost",
            "port":6333,
        }
    }
}

memory_client = Memory(MemoryConfig(**config))
print(f"memory_client.config:{memory_client.config}\n")
print(memory_client.__dict__.keys())

while True:

    # load input instrcution
    user_query = input(">")

    # search for relivant memory from database
    search_memory = memory_client.search(query=user_query, filters={"user_id": "ronak_dev"})

    # extract memories from search_memory object
    results = search_memory.get("results", []) if isinstance(search_memory, dict) else search_memory
    memories = [
        f"ID:{mem.get("id")}\nMemory:{mem.get("memory")}" for mem in results
    ]

    print("Found memories:", memories)

    # Let's make a SYSTEM_PROMT using last fetached memories from database
    SYSTEM_PROMPT = f"""
        Here is the context about the user:
        {json.dumps(memories)}
    """  

    # response by chat gpt
    response = client.chat.completions.create(
        model= "gpt-4.1-mini",
        messages=[
            {"role":"system", "content":SYSTEM_PROMPT},
            {"role":"user", "content":user_query}
        ]
    )

    ai_response = response.choices[0].message.content

    print("AI:", ai_response),

    reslut = memory_client.add(
        user_id="ronak_dev",
        messages=[
            {"role":"user", "content":user_query},
            {"role":"assistant", "content":ai_response}
        ]
    )
    print(f"reslut:{json.dumps(reslut)}")

    print("Convertsection saved!")