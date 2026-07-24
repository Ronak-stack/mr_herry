import pandas as pd
from sqlalchemy import text


def execute_sql(engine, sql):

    with engine.connect() as conn:

        result = conn.execute(text(sql))

        rows = result.fetchall()

        return pd.DataFrame(
            rows,
            columns=result.keys()
        )