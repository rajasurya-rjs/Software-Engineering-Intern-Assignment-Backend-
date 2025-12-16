from etl.extract.sheets_extractor import extract_all
from etl.transform.transformers import transform_all
from etl.load.db_loader import load_all

SPREADSHEET_ID = "1rHkiQO9V8DOLmBasG4R7Y20_88Jly6Ydwn93kG3Lk0k"
CREDS_PATH = "service_account.json"

data = extract_all(SPREADSHEET_ID, CREDS_PATH)

print("Students:", len(data["students"]))
print("Courses:", len(data["courses"]))
print("Enrollments:", len(data["enrollments"]))
