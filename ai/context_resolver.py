def resolve_context(
    current_prompt,
    memory,
    client
):
    formatted_memory = format_memory(memory)

    system_prompt:str = f"""
                You are an expert conversation resolver.

                Task:
                    - Read the conversation history
                    - Read the current prompt
                    - Decide the current prompt refers to any previous conversation.
                    - Then return a JSON object with:

                        - is_followup (boolean)

                        - memory_index (number or null)

                    - Return the zero-based memory index.
                    - If the current prompt depends on previous information, mark it as follow-up.

                    - If it is a completely new request, mark it as not follow-up.

                    Output format:
                    {{
                        'is_followup': true,
                        'memory_index': 0
                    }}
                    or
                    {{
                        'is_followup': false,
                        'memory_index': null
                    }}

                    Rules:
                        - First determine which previous conversations are relevant to the current prompt.
                        - If multiple previous conversations are relevant, select the most recent relevant conversation.
                        - Prefer the highest memory index only among conversations that are relevant.
                        - If no previous conversation is relevant, return is_followup as false and memory_index as null.
                        - Return only JSON.
                        - No explanation.
                        - No explanation
                        - If multiple conversations can relate to the current prompt, always select the most recent relevant conversation.
                        - Prefer the highest memory index among relevant conversations.
                """
    user_prompt = f"""
                Conversation History:

                    {formatted_memory}

                Current User Prompt:

                    {current_prompt}
            """
    

    response = client.chat.completions.create(model="gpt-4.1-mini",messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    # load json library for manage and control json data
    import json
    return json.loads(response.choices[0].message.content.strip())

def format_memory(memory):
    import json
    text = ""
    for index, item in enumerate(memory):
        text += f"\n Conversation: #{index}\n\n" #

        text += f"\n Intent: {item.get('intent','')}\n\n"

        text += f"\n Prompt: {item.get('prompt')}\n\n"

        text += f"\n Output: {json.dumps(item.get('output', {}), indent=2)}\n\n"

        # load metadata
        text += f"\n metadata: {json.dumps(item.get('metadata', {}), indent=2)}"

    return text