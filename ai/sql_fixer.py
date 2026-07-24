def fix_sql(prompt, sql, validation_error, schema, client):

    system_prompt = f"""
    You are a senior SQL engineer.

    User request:
    {prompt}

    Schema:
    {schema}

    Invalid SQL:
    {sql}

    Validation Error:
    {validation_error}

    Fix the SQL query.

    Return ONLY corrected SQL.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt}
        ]
    )

    return response.choices[0].message.content.strip()