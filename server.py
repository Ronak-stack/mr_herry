from fastapi import FastAPI
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.background import BackgroundTasks
from sqlalchemy import create_engine

from ai.decision import decide_flow
from ai.intent_router import detect_intent

# load handlers
from ai.handlers.sql_handler import handle_sql

from ai.context_resolver import resolve_context
from memory.context_store import get_memory

engine = create_engine("mysql+pymysql://root:@localhost:3306/bot_db")

#load env file
load_dotenv()
# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# 🤖 AI endpoint
@app.get("/ask")
def ask_ai(prompt: str, background_tasks: BackgroundTasks):
    intent = detect_intent(prompt, client)
    flow = decide_flow(prompt,client)

    try:
        memory = get_memory()
        result = resolve_context(
        current_prompt="show email also",
        memory=memory,
        client=client
    )
        context = resolve_context(prompt,memory,client)
        print(f"context:{context}")

        if intent == "SQL":
            return handle_sql(
                prompt,
                client,
                engine,
                background_tasks,
                flow
            )

    except Exception as e:
        return {
            "error": str(e)
        }

# @app.get('/xlsx')
# async def renderExcel():
#     # df = pd.read_excel('./DataSampleData.xlsx')
#     df = pd.read_sql("SELECT * FROM profits", engine)
#     describe = df.describe()
#     head = df.head()
#     return {
#     "columns": list(df.columns),
#     "preview": head.to_dict(orient="records"),
#     "summary": describe.to_dict()
#     }

@app.get('/project_1')
async def katterl_story_project():
    kettel_boiled = True
    if kettel_boiled:
        return ('Kettel done! time make some chai!')
    else:
        return ('No kettel boilded yet!')

@app.get('/debug/memory')
def test_context():

    memory = get_memory()
    result = resolve_context(
        current_prompt="show email also",
        memory=memory,
        client=client
    )

    return result