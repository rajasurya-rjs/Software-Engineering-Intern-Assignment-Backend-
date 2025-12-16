# etl/extract/sheets_extractor.py

import pandas as pd
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_sheets_service(credentials_path: str):
    creds = Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def fetch_sheet_data(spreadsheet_id: str, sheet_name: str, credentials_path: str):
    service = get_sheets_service(credentials_path)
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=sheet_name
    ).execute()

    values = result.get("values", [])

    if not values:
        logging.warning(f"No data found in sheet: {sheet_name}")
        return []

    headers = values[0]
    rows = values[1:]

    records = [dict(zip(headers, row)) for row in rows]

    logging.info(
        f"Extracted {len(records)} rows from sheet '{sheet_name}'"
    )

    return records


def extract_all(spreadsheet_id: str, credentials_path: str):
    return {
        "students": fetch_sheet_data(
            spreadsheet_id, "students_raw", credentials_path
        ),
        "courses": fetch_sheet_data(
            spreadsheet_id, "courses_raw", credentials_path
        ),
        "enrollments": fetch_sheet_data(
            spreadsheet_id, "enrollments_raw", credentials_path
        ),
    }
