def detect_todo_action(prompt, client):

    system_prompt = """
    You are a TODO action classifier.

    Determine what action the user wants to perform on their TODOs.

    Possible actions:

    CREATE
    SEARCH
    UPDATE
    DELETE
    COMPLETE

    Rules:

    - CREATE:
      User wants to add/create a new TODO.

    - SEARCH:
      User wants to find, view, show, list, or retrieve existing TODOs.

    - UPDATE:
      User wants to modify an existing TODO.

    - DELETE:
      User wants to remove/delete an existing TODO.
    
    - COMPLETE
      User wants to mark an existing TODO as completed, done, finished, or complete.

    Return ONLY one word.
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