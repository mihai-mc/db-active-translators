import os
from pathlib import Path

from google.auth import default
import gspread

GOOGLE_SPREADSHEET_ID = '1Dnh4blW2lAa9PRYKVJL1i79JZCDc6V0Uzw2ZRR9P10Y'
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def google_authentication():
    if not os.getenv("GITHUB_ACTIONS"):
        # Running locally
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path('service-account-credentials.json').absolute())
    creds, _ = default(scopes=GOOGLE_SCOPES)
    return creds


def main():
    creds = google_authentication()
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(GOOGLE_SPREADSHEET_ID).worksheet('Form Responses 1')
    rows = sheet.get_all_records()
    print(rows)

if __name__ == "__main__":
    main()