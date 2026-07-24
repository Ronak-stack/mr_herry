state = {
    "intent": None,
    "flow": None,
    "last_prompt": None,
    "last_sql": None,
    "last_result": None,
    "history": []
}


def get_state():
    return state