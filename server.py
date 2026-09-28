from fastapi import FastAPI
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.background import BackgroundTasks
from sqlalchemy import create_engine

from schemas.ask_schema import AskRequest

from ai.context_resolver import resolve_context
from memory.context_store import get_memory
from ai.pipeline import process_request

engine = create_engine("mysql+pymysql://root:@localhost:3306/bot_db")

#load env file
load_dotenv()
# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# 🤖 AI endpoint
@app.post("/ask")
def ask_ai(
    request: AskRequest,
    background_tasks: BackgroundTasks
):
    return process_request(
        prompt=request.prompt,
        client=client,
        engine=engine,
        background_tasks=background_tasks
    )

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
    print ("Hello world")
    memory = get_memory()
    result = resolve_context(
        current_prompt="show email also",
        memory=memory,
        client=client
    )

    return result

@app.get('/image')
def check_image():
    from image.main import image_checker
    image_checker()