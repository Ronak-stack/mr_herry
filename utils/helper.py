def clean_for_json(data):
    import pandas as pd
    import numpy as np
    if isinstance(data, pd.DataFrame):
        data = data.replace([np.nan, np.inf, -np.inf], None)
        return data.to_dict(orient="records")

    elif isinstance(data, pd.Series):
        data = data.replace([np.nan, np.inf, -np.inf], None)
        return data.to_dict()

    elif isinstance(data, dict):
        return {
            k: (None if isinstance(v, float) and (pd.isna(v) or v in [np.inf, -np.inf]) else v)
            for k, v in data.items()
        }

    elif isinstance(data, list):
        return [
            clean_for_json(item) for item in data
        ]

    return data

def delete_file(path):
    import os
    if os.path.exists(path):
        os.remove(path)