from ai.decision import decide_flow
from ai.intent_router import detect_intent


from ai.context_resolver import resolve_context
from memory.context_store import get_memory

# Load state manager for build state
from core.state_manager import build_state

# load route handlers
from ai.handler_router import route_handler

def process_request(
    prompt,
    client,
    engine,
    background_tasks,
    user_id=None
):

    # Step 1: Load memory
    memory = get_memory()

    # Step 2: Get actual context from current prompt
    context = resolve_context(current_prompt=prompt, memory=memory, client=client)

    # Step 3: Detect intent
    previous = (
        memory[context["memory_index"]]
        if context["is_followup"]
        else None
    )
    intent = detect_intent(prompt, client, previous=previous)
    print(f"intent:{intent}")
    # Step 4: Build state by given context object
    state = build_state(current_prompt=prompt, intent=intent, context=context, memory=memory)

    # Step 5: Route Handler
    return route_handler(
        state=state,
        client=client,
        engine=engine,
        background_tasks=background_tasks
    )