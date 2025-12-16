from etl.extract.sheets_extractor import extract_all
from etl.transform.students_transform import transform_students
from etl.transform.courses_transform import transform_courses
from etl.transform.enrollments_transform import transform_enrollments
from etl.load.db_loader import load_all
from etl.utils.logger import get_logger

SPREADSHEET_ID = "1rHkiQO9V8DOLmBasG4R7Y20_88Jly6Ydwn93kG3Lk0k"
CREDS_PATH = "service_account.json"

logger = get_logger()

def main():
    logger.info("Starting ETL Pipeline")

    raw_data = extract_all(SPREADSHEET_ID, CREDS_PATH)

    students = transform_students(raw_data["students"])
    courses = transform_courses(raw_data["courses"])
    enrollments = transform_enrollments(raw_data["enrollments"])

    load_all(students, courses, enrollments)

    logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()
