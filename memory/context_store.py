conversation_memory = []

def save_memory(
    intent,
    prompt,
    output,
    metadata=None
):
    if metadata is None:
        metadata = {}
    print(">>> SAVING MEMORY <<<")
    conversation_memory.append({
    "intent": intent,
    "prompt": prompt,
    "output": output,
    "metadata": metadata
    })
    print(conversation_memory)

    # keep last 5 only
    if len(conversation_memory) > 5:
        conversation_memory.pop(0)


def get_memory():
    print(">>> READING MEMORY <<<")
    print(conversation_memory)
    return conversation_memory