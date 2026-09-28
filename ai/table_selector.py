def select_tables(prompt, schema, client, previous=None):

    if previous:
        previous_context = f"""
        Previous Prompt:
        {previous.prompt}

        Previous Output:
        {previous.output}
        """
    else:
        previous_context = "No previous conversation."

    system_prompt = f"""
    You are a database expert.

    Database schema:
    {schema}

    Previous Conversation:
    {previous_context}

    Your task:
    Return ONLY the table names needed for the user query.

    Rules:
    - Return comma separated table names
    - No explanation
    - Only use existing tables

    If this is a follow-up:
    - Identify the primary table/entity from the previous conversation.
    - Treat that table as the default scope.
    - Preserve that scope for the current prompt.
    - Do not add unrelated tables merely because they contain
    columns matching words like active, inactive, count, price, etc.
    - Add another table only when the current request explicitly
    requires information from that table.

    Example:
    users, orders, order_items
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def build_filtered_schema(full_schema, selected_tables):
    filtered = ""

    blocks = full_schema.split("\nTable:")

    selected_tables = {
        table.strip()
        for table in selected_tables
        if table.strip()
    }

    for block in blocks:
        if not block.strip():
            continue

        table_name = block.strip().splitlines()[0].strip()

        if table_name in selected_tables:
            filtered += "\nTable:" + block

    return filtered