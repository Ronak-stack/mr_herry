def safe_execute(code, df):
    code_lower = code.lower()

    import re
    blocked_patterns = [
        r"\bimport\b",
        r"__",
        r"\bexec\b",
        r"\beval\b",
        r"\bopen\b",
        r"\bos\b",
        r"\bsys\b"
    ]

    if any(re.search(pattern, code_lower) for pattern in blocked_patterns):
        raise Exception("Unsafe code detected")

    try:
        return eval(code, {"__builtins__": {}}, {"df": df})
    except Exception as e:
        return {"error": str(e)}
    
def is_safe_sql(sql):
    sql = sql.strip().lower()
    
    blocked = ["insert", "update", "delete", "drop", "alter"]
    
    if any(word in sql for word in blocked):
        return False
    
    return sql.startswith("select")

def clean_sql(sql):
    return sql.strip().lower().replace("```sql", "").replace("```", "").strip()