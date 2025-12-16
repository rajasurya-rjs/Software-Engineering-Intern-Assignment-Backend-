from etl.utils.db import get_connection
from etl.utils.logger import get_logger

logger = get_logger()

def load_all(students, courses, enrollments):
    conn = get_connection()
    cur = conn.cursor()

    logger.info("Loading data into NeonDB")

    for s in students:
        cur.execute(
            """
            INSERT INTO students (full_name, email, department_id, enrollment_year)
            VALUES (%s, %s, 1, %s)
            ON CONFLICT (email) DO NOTHING
            """,
            (s["student_name"], s["email"], int(s["batch_year"]))
        )

    for c in courses:
        cur.execute(
            """
            INSERT INTO courses (course_code, course_name, credits, department_id)
            VALUES (%s, %s, %s, 1)
            ON CONFLICT (course_code) DO NOTHING
            """,
            (c["course_code"], c["course_name"], int(c["credits"]))
        )
    for e in enrollments:
        try:
            cur.execute(
                """
                INSERT INTO enrollments (student_id, course_id, enrollment_date, grade)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (student_id, course_id) DO NOTHING
                """,
                (
                    int(e["student_id"]),
                    int(e["course_id"]),
                    e.get("enrollment_date") or "2025-01-01",
                    e.get("grade")
                )
            )
        except Exception as ex:
            logger.warning(f"Skipping enrollment record {e}: {ex}")


    conn.commit()
    cur.close()
    conn.close()

    logger.info("Database load completed")
