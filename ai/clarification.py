def needs_clarification(prompt, client):
    system_prompt = """
    Decide if clarification is absolutely required.

    Only say YES if:
    - The query is incomplete
    - OR missing critical information

    If query is understandable → say NO

    Examples:

    "show all users" → NO
    "users with orders" → NO
    "top customers" → NO

    "top customers by what?" → YES
    "compare profit" → YES

    Answer only YES or NO.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def ask_clarification(prompt, client):
    system_prompt = f"""
    The user query is unclear:

    "{prompt}"

    Ask a short and specific clarification question to better understand the request.
    Do not explain anything else.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt}
        ]
    )

    return response.choices[0].message.content.strip()