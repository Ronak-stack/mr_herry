from .handlers.sql_handler import handle_sql
from .handlers.todo_handler import handle_todo
from modules.todo.todo_action import detect_todo_action
def route_handler(
    state,
    client,
    engine,
    background_tasks
):
    if state.intent == "SQL":
        return handle_sql(state=state, client=client, engine=engine, background_tasks=background_tasks)
    elif state.intent == "TODO":
        return handle_todo(
            state=state,
            client=client,
            engine=engine,
            background_tasks=background_tasks
        )


    return {
        "error": "Unsupported intent"
    }

