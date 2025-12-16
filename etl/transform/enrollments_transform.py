import pandas as pd
from etl.utils.logger import get_logger

logger = get_logger()

VALID_GRADES = {"A", "A-", "B+", "B", "C", "D", "F"}

def transform_enrollments(records):
    df = pd.DataFrame(records)

    initial = len(df)

    df = df.dropna(subset=["student_id", "course_id"])
    df["grade"] = df["grade"].where(df["grade"].isin(VALID_GRADES))

    logger.info(f"Enrollments: {len(df)} valid | {initial - len(df)} dropped")

    return df.to_dict(orient="records")
