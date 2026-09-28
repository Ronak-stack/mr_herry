import re


def is_explicit_todo_request(prompt: str) -> bool:
    text = prompt.lower().strip()

    todo_patterns = [
        # Personal todo/task references
        r"\bmera todo\b",
        r"\bmere todos\b",
        r"\bmera task\b",
        r"\bmere tasks\b",

        # Todo management
        r"\btodo dikhao\b",
        r"\btodos dikhao\b",
        r"\btodo show\b",
        r"\btodos show\b",
        r"\btodo list\b",
        r"\btodos list\b",
        r"\btodo search\b",
        r"\btodos search\b",

        # Create/update/delete/complete
        r"\btodo bana\b",
        r"\btodo bana do\b",
        r"\btodo add\b",
        r"\btodo update\b",
        r"\btodo edit\b",
        r"\btodo hata\b",
        r"\btodo delete\b",
        r"\btodo remove\b",
        r"\btodo complete\b",
        r"\btodo done\b",

        # Common natural-language search phrases
        r"\blatest .*todos?\b",
        r"\bnext .*todos?\b",
        r"\brecent .*todos?\b",
        r"\bpending .*todos?\b",
        r"\bcompleted .*todos?\b",
        r"\ball .*todos?\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in todo_patterns
    )

def detect_intent(prompt, client, previous=None):
    # Explicit TODO-management request
    if is_explicit_todo_request(prompt):
        return "TODO"

    if previous:
        previous_context = f"""
            Previous conversation:
            Intent: {previous.get('intent')}
            Prompt: {previous.get('prompt')}
            Output: {previous.get('output')}
        """
    else:
        previous_context = "No previous conversation."

    system_prompt = f"""
        You are an Intent Classifier for NEXORA.

        Possible intents:

        SQL
        CHAT
        TODO
        REMINDER
        CALCULATOR

        Previous Conversation:
        {previous_context}

        Your task:
        Determine the intent of the CURRENT user prompt.

        IMPORTANT:
        - Understand the user's meaning regardless of language.
        - The user may speak English, Hindi, Hinglish, or a mixture of languages.
        - Do NOT classify based only on keywords.
        - Classify based on the actual requested action.

        TODO:
        Choose TODO when the user wants to:
        - add a task to their todo list
        - create a todo
        - save something as a task
        - remember something as a task
        - add something to their tasks/todos
        - update an existing todo
        - complete a todo
        - delete a todo
        - show/list/search/retrieve existing todos
        - show my latest todo
        - show my latest N todos
        - show my next todo
        - show recent todos
        - show pending todos
        - show completed todos
        - show all my todos

        Important:
        Requests about managing the user's TODOs must be classified as TODO,
        even when they contain words such as:
        "latest", "recent", "next", "3", "5", "data", or "according to date/time".

        Examples:

        Mera latest todo dikhao
        TODO

        Mere latest 3 todos dikhao
        TODO

        Mera next todo dikhao
        TODO

        Mere pending todos dikhao
        TODO

        Mere latest 5 todos date ke according dikhao
        TODO
        Add buy milk to my todo
        TODO

        Mere todo me buy milk add kar do
        TODO

        Mere todos me add kro ki mujhe 28 august ko morning me
        2000 rupee ATM se nikalne hain
        TODO

        Mujhe yaad rakhna hai ki kal electricity bill bharna hai
        TODO

        Kal subah 8 baje mujhe gym jana hai, todo me daal do
        TODO

        REMINDER:
        Choose REMINDER when the user explicitly wants NEXORA
        to remind/notify them at a specific time.

        Examples:

        Remind me tomorrow at 5 PM
        REMINDER

        Mujhe kal 5 baje yaad dila dena ki meeting hai
        REMINDER

        SQL:
        Choose SQL when the user wants information or operations
        related to database data.
        - If the user is asking about database tables, rows, columns,
        counts, aggregations, or SQL data, classify as SQL.
        - A request such as "todos table me kitne records hain?"
        is SQL, not TODO.

        Examples:

        Show all users
        SQL

        Only active users
        SQL

        Show all products
        SQL

        How many users are there?
        SQL

        CALCULATOR:
        Choose CALCULATOR for mathematical calculations.

        Examples:

        What is 25 * 8
        CALCULATOR

        Calculate 500 + 2000
        CALCULATOR

        CHAT:
        Choose CHAT for general conversation or questions that do
        not belong to the above categories.

        Examples:

        Who is Iron Man?
        CHAT

        How are you?
        CHAT

        IMPORTANT:
        The CURRENT user prompt has priority over previous conversation.

        Return ONLY one word:
        SQL
        CHAT
        TODO
        REMINDER
        CALCULATOR
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