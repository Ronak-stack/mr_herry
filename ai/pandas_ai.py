# 🔥 AI code generator
def generate_code(prompt, df, client):
    columns = list(df.columns)
    sample_data = df.head(3).to_dict(orient="records")

    system_prompt = f"""
    You are a Python data analyst.

    You are given a pandas dataframe named df.

    Columns: {columns}

    Sample Data: {sample_data}

    Example:
    User: average profit
    Output: df.select_dtypes(include='number').mean()

    Rules:
    - Only write pandas code
    - DO NOT assign variables (no df_clean, no new variables)
    - DO NOT write multiple lines of code
    - ONLY return a single-line python expression
    - Use method chaining if needed

    - If cleaning is required, apply it inline (e.g., df.apply(pd.to_numeric, errors='coerce'))

    - Prefer using df.select_dtypes(include='number') for aggregations

    - For filtering use conditions like df[df['column'] == value]
    - For multiple values use .isin([...])

    - For comparisons use groupby when needed
    - For sorting use sort_values()
    
    - If visualization is requested:
    - Use bar chart for comparisons
    - Use line chart for trends over time
    - Use pie chart for proportions

    - Use correct column names only
    - Do not import anything
    - Do not use file operations
    - Always return clean and readable pandas code
    - Prefer grouping for comparisons
    - Always sort results when comparing
    - Limit output size when needed (top 5 or top 10)

    - Break down complex queries into steps
    - Apply filtering, grouping, sorting as needed
    - Combine multiple operations using method chaining
    - Always return final result only
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()