from .handlers.sql_handler import handle_sql
def route_handler(
    state,
    client,
    engine,
    background_tasks
):
    if state.intent == "SQL":

        return handle_sql(state=state, client=client, engine=engine, background_tasks=background_tasks, flow='SQL_ONLYSQL')

    return {
        "error": "Unsupported intent"
    }

