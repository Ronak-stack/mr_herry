import inspect

conversation_memory = []


def save_memory(
    intent,
    prompt,
    output,
    metadata=None
):
    caller = inspect.stack()[1]

    if metadata is None:
        metadata = {}

    memory_item = {
        "intent": intent,
        "prompt": prompt,
        "output": output,
        "metadata": metadata
    }

    conversation_memory.append(memory_item)

    # Keep only the last 5 memories
    if len(conversation_memory) > 5:
        conversation_memory.pop(0)

    print(
        f">>> SAVE_MEMORY CALLED FROM: "
        f"{caller.function} "
        f"({caller.filename}:{caller.lineno})"
    )

    print(">>> MEMORY PROMPT:", prompt)
    print(">>> CURRENT MEMORY:", conversation_memory)


def get_memory():
    print(">>> READING MEMORY <<<")
    print(conversation_memory)

    return conversation_memory