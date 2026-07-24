def validate_sql(prompt, sql, schema, client):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": """
You are a strict SQL validator.

Output format:

VALID

or

INVALID: reason

Never return SQL.
Never explain.
Never rewrite.
"""
            },
            {
                "role": "user",
                "content": f"""
Schema:
{schema}

User Request:
{prompt}

SQL:
{sql}
"""
            }
        ]
    )

    return response.choices[0].message.content.strip()