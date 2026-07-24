from utils.security import safe_execute
    
def fix_code(code, error, client):
    system_prompt = f"""
    You are a Python debugging expert.

    Fix the given pandas code based on error.

    Code:
    {code}

    Error:
    {error}

    Rules:
    - Return only fixed pandas code
    - Single-line expression only
    - Do not explain anything
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def execute_with_retry(code, df, client):
    try:
        return safe_execute(code, df)

    except Exception as e:
        print("ERROR:", str(e))

        fixed_code = fix_code(code, str(e), client)
        print("FIXED CODE:", fixed_code)

        try:
            return safe_execute(fixed_code, df)
        except Exception as e2:
            return {"error": str(e2), "final_code": fixed_code}