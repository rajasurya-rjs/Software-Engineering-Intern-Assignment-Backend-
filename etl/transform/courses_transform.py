import pandas as pd
from etl.utils.logger import get_logger

logger = get_logger()

def transform_courses(records):
    df = pd.DataFrame(records)

    initial = len(df)

    df = df.dropna(subset=["course_code", "course_name"])
    df["credits"] = pd.to_numeric(df["credits"], errors="coerce")
    df = df[df["credits"] > 0]

    df = df.drop_duplicates(subset=["course_code"])

    logger.info(f"Courses: {len(df)} valid | {initial - len(df)} dropped")

    return df.to_dict(orient="records")
