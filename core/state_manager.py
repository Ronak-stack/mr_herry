from .schemas.state_manager import State, Previous
def build_state(
    current_prompt,
    intent,
    context,
    memory
):
    previous = None
    is_followup = context['is_followup']
    
    if is_followup:
        previous_memory = memory[context["memory_index"]]

        previous = Previous(
            intent=previous_memory["intent"],
            prompt=previous_memory["prompt"],
            output=previous_memory["output"],
            metadata=previous_memory.get("metadata", {})
        )

        state_manager_response_object = State(
            intent=intent,
            is_followup=is_followup,
            current_prompt=current_prompt,
            previous=previous
        )

        return state_manager_response_object
    else:
        return State(intent=intent, is_followup=is_followup, current_prompt=current_prompt)