from fastapi.responses import FileResponse
from utils.helper import clean_for_json, delete_file

from ai.sql_generator import generate_sql, get_schema
from ai.pandas_ai import generate_code
from ai.self_heal import execute_with_retry
from utils.security import is_safe_sql, clean_sql
from utils.chart import generate_chart, detect_chart_type
from memory.context_store import save_memory, get_memory
from ai.sql_validator import validate_sql
from ai.sql_fixer import fix_sql
from ai.runtime_fixer import fix_runtime_sql
from utils.db import execute_sql
from ai.decision import decide_flow

def handle_sql(
    state,
    client,
    engine,
    background_tasks
):
    prompt = state.current_prompt
    flow = decide_flow(prompt, client)

    sql = generate_sql(state,client, engine)
    
    cleaned_sql = clean_sql(sql)

    schema = get_schema(engine)

    validation = validate_sql(
            prompt,
            cleaned_sql,
            schema,
            client
        )
    if not validation.startswith("VALID"):
        fixed_sql = fix_sql(
            prompt,
            cleaned_sql,
            validation,
            schema,
            client
        )
        cleaned_sql = clean_sql(fixed_sql)

    if not is_safe_sql(cleaned_sql):
            return {
                "error": "Unsafe SQL detected",
                "generated_sql": sql
            }

    try:
        dfk = execute_sql(engine, cleaned_sql)
    except Exception as db_error:
        fixed_sql = fix_runtime_sql(
            prompt,
            cleaned_sql,
            str(db_error),
            schema,
            client
        )

        cleaned_sql = clean_sql(fixed_sql)
        dfk = execute_sql(engine, cleaned_sql)

    if dfk.empty:
        return {
            "error": "No data found for this query",
            "generated_sql": cleaned_sql
        }
    # save_memory(prompt,cleaned_sql)
    save_memory(intent="SQL", prompt=prompt, output={"sql": cleaned_sql})

    if flow == "SQL_ONLY":
        return {
            "type": "sql_only",
            "generated_sql": sql,
            "result": clean_for_json(dfk.to_dict(orient="records"))
        }

    elif flow == "SQL_PANDAS":
        code = generate_code(prompt, dfk, client)

        result = execute_with_retry(code, dfk, client)

        keywords = ["chart", "graph", "plot", "visualize"]

        # 📊 Chart support
        if any(k in prompt.lower() for k in keywords):
            if hasattr(result, "plot"):
                chart_type = detect_chart_type(prompt)
                file_path = generate_chart(result, chart_type)
                background_tasks.add_task(delete_file, file_path)

                return FileResponse(file_path, media_type="image/png")
        cleaned_result = clean_for_json(result)
        return {
            "type": "sql_pandas",
            "generated_sql": sql,
            "generated_code": code,
            "result": str(cleaned_result)
        }

    else:
        return {"error": "Unknown decision type"}