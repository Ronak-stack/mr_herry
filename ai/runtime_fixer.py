def fix_runtime_sql(prompt, sql, db_error, schema, client):

    system_prompt = f"""
        You are a SQL repair expert.

        Schema:
        {schema}

        User Request:
        {prompt}

        SQL:
        {sql}

        Database Error:
        {db_error}

        Fix the SQL query.

        Rules:
        - Return ONLY SQL
        - Keep original intent
        - Use existing tables/columns
        - Only SELECT allowed
        """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt}
        ]
    )

    return response.choices[0].message.content.strip()