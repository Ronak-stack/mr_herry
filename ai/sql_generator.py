import pandas as pd   # 👈 ye top pe hona chahiye
from ai.query_planner import create_plan
SCHEMA_CACHE = None

def validate_sql(prompt, sql, schema, client):

    system_prompt = f"""
        You are a SQL validator.

        Schema:
        {schema}

        User Request:
        {prompt}

        SQL:
        {sql}

        Your task:

        1. Check whether tables exist.
        2. Check whether columns exist.
        3. Check joins.
        4. Check whether query answers the user request.

        IMPORTANT:

        Return EXACTLY ONE OF THESE:

        VALID

        OR

        INVALID: <reason>

        Do NOT return SQL.
        Do NOT explain.
        Do NOT rewrite query.
        """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def generate_sql(state, client, engine):
    schema = get_schema(engine)
    from ai.table_selector import select_tables, build_filtered_schema

    previous=state.previous if state.is_followup else None
    selected = select_tables(state.current_prompt, schema, client, previous)

    filtered_schema = build_filtered_schema(schema, selected.split(","))
    plan = create_plan(state.current_prompt, filtered_schema, client)

    print("CURRENT PROMPT:", state.current_prompt)
    print("IS FOLLOWUP:", state.is_followup)
    print("PREVIOUS:", state.previous)

    if state.is_followup:
        previous_context = f"""
            Previous Prompt:
            {state.previous.prompt}

            Previous Output:
            {state.previous.output}
            """
    else:
        previous_context = "No previous conversation."

                
    system_prompt = f"""
    You are a SQL expert.

    Database schema:
    {filtered_schema}

    Conversation Memory:
    {previous_context}

    Execution Plan:
    {plan}

    Rules:
    - Use correct tables and columns
    - Use JOIN when needed
    - Only SELECT queries allowed
    - Do not guess columns
    - Use table aliases when needed
    - Always handle NULL values using COALESCE

    Return only SQL query.
    """

    print("SELECTED TABLES:", selected)

    print("QUERY PLAN:")
    print(plan)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": state.current_prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def get_tables(engine):
    query = "SHOW TABLES"
    tables = pd.read_sql(query, engine)
    return tables.iloc[:, 0].tolist()


def get_columns(engine, table):
    query = f"DESCRIBE {table}"
    cols = pd.read_sql(query, engine)
    return cols["Field"].tolist()

def get_schema(engine):
    global SCHEMA_CACHE

    if SCHEMA_CACHE is not None:
        print("⚡ Using cached schema")
        return SCHEMA_CACHE

    print("⏳ Loading schema from DB...")

    tables = get_tables(engine)

    schema = ""

    for table in tables:
        cols = get_columns(engine, table)

        schema += f"\nTable: {table}\n"

        for col in cols:
            schema += f"- {col}\n"

    # Relationships add karo
    relationships = get_relationships(engine)

    schema += "\nRelationships:\n"

    for _, row in relationships.iterrows():
        schema += (
            f"{row['TABLE_NAME']}.{row['COLUMN_NAME']} "
            f"-> "
            f"{row['REFERENCED_TABLE_NAME']}."
            f"{row['REFERENCED_COLUMN_NAME']}\n"
        )

    SCHEMA_CACHE = schema

    return schema

def filter_schema(schema, prompt):
    prompt = prompt.lower()

    selected_tables = []

    # 🧠 simple keyword mapping
    if "user" in prompt:
        selected_tables.append("users")

    if "order" in prompt:
        selected_tables.append("orders")
        selected_tables.append("order_items")

    if "product" in prompt:
        selected_tables.append("products")

    # 👉 अगर kuch match nahi hua → full schema fallback
    if not selected_tables:
        return schema

    filtered = ""

    blocks = schema.split("\nTable:")

    for block in blocks:
        for table in selected_tables:
            if table in block:
                filtered += "\nTable:" + block

    return filtered if filtered else schema

def get_relationships(engine):
    query = """
    SELECT
        TABLE_NAME,
        COLUMN_NAME,
        REFERENCED_TABLE_NAME,
        REFERENCED_COLUMN_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE REFERENCED_TABLE_NAME IS NOT NULL
    AND TABLE_SCHEMA = DATABASE()
    """

    return pd.read_sql(query, engine)