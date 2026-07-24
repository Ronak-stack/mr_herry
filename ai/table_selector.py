def select_tables(prompt, schema, client):

    system_prompt = f"""
    You are a database expert.

    Database schema:
    {schema}

    Your task:
    Return ONLY the table names needed for the user query.

    Rules:
    - Return comma separated table names
    - No explanation
    - Only use existing tables

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

    for block in blocks:
        for table in selected_tables:
            if table.strip() in block:
                filtered += "\nTable:" + block

    return filtered