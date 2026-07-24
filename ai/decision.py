def decide_flow(prompt,client):
    system_prompt = """
    You are an AI decision maker.

    Decide whether the task needs:
    - SQL_ONLY
    - SQL_PANDAS

    Rules:
    - Simple aggregation/filter → SQL_ONLY
    - Comparison, trend, ratio → SQL_PANDAS

    Return only one word:
    SQL_ONLY or SQL_PANDAS
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()