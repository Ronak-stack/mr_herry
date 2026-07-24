def detect_intent(prompt, client):

    system_prompt = """
    You are an Intent Classifier.

    Possible intents:

    SQL
    CHAT
    TODO
    REMINDER
    CALCULATOR

    Return ONLY one word.

    Example:

    Show all users
    SQL

    Add buy milk to my todo
    TODO

    Remind me tomorrow 5 PM
    REMINDER

    What is 25 * 8
    CALCULATOR

    Who is Iron Man
    CHAT
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip().upper()