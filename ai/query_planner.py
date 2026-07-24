def create_plan(prompt, schema, client):

    system_prompt = f"""
    You are an AI query planner.

    Database schema:
    {schema}

    Your task:
    Break the user request into logical database steps.

    Rules:
    - Think step-by-step
    - Mention tables needed
    - Mention joins needed
    - Mention aggregation/sorting if needed
    - Do NOT generate SQL
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()