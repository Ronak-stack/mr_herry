from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()

# 1. Correct model initialization
llm = init_chat_model(
    model='gpt-4o-mini',
    model_provider="openai"
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    response = llm.invoke(state.get("messages"))
    return {"messages": response}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

def compile_graph_with_checkpoin(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

# 2. Fixed connection string with authSource parameter
DB_URL = "mongodb://admin:admin@127.0.0.1:27018/?authSource=admin"

with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
    # 3. Correct compilation with the database saver
    graph_with_checkpointer = compile_graph_with_checkpoin(checkpointer=checkpointer)
    
    config = {
        "configurable": {
            "thread_id": "ronak"
        }
    }

    # 4. Invoke the checkpoint-enabled graph
    # updated_state = graph_with_checkpointer.invoke(
    #     State({"messages": ["Hi, what is my name?"]}), 
    #     config
    # )

    # print("\n\nupdated_state:", updated_state)

    for chunk in graph_with_checkpointer.stream(
        State({"messages": ["Hi, what is my name?"]}), 
        config,
        stream_mode="values"
    ):
        chunk['messages'][-1].pretty_print()
