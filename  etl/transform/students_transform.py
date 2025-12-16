import pandas as pd
from etl.utils.logger import get_logger

logger = get_logger()

def transform_students(records):
    df = pd.DataFrame(records)

    initial = len(df)

    df = df.dropna(subset=["email"])
    df["department"] = df["department"].str.strip().str.lower()
    df["batch_year"] = pd.to_numeric(df["batch_year"], errors="coerce")

    df = df.dropna(subset=["batch_year"])

    logger.info(f"Students: {len(df)} valid | {initial - len(df)} dropped")

    return df.to_dict(orient="records")
