import matplotlib.pyplot as plt

def generate_chart(data, chart_type="bar"):
    if hasattr(data, "empty") and data.empty:
        raise Exception("No data to plot")
    import uuid
    filename = f"chart_{uuid.uuid4().hex}.png"

    if chart_type == "line":
        data.plot(kind='line', figsize=(10,5))
    elif chart_type == "pie":
        data.plot(kind='pie', autopct='%1.1f%%')
    else:
        data.plot(kind='bar', figsize=(10,5))

    plt.xticks(rotation=45)
    plt.title("Analysis Result")
    plt.tight_layout()

    plt.savefig(filename)
    plt.close()
    return filename

def detect_chart_type(prompt):
    prompt = prompt.lower()

    if "trend" in prompt or "over time" in prompt:
        return "line"
    elif "percentage" in prompt or "distribution" in prompt:
        return "pie"
    else:
        return "bar"