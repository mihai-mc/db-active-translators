import os
import argparse
import logging
from pathlib import Path

from google.auth import default
import gspread

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

logger = logging.getLogger(__name__)


class GoogleSheets:
    SPREADSHEET_ID = "1Dnh4blW2lAa9PRYKVJL1i79JZCDc6V0Uzw2ZRR9P10Y"
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    @classmethod
    def google_authentication(cls):
        if not os.getenv("GITHUB_ACTIONS"):
            # Running locally
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path("service-account-credentials.json").absolute())

        creds, _ = default(scopes=cls.SCOPES)
        return creds

    @classmethod
    def get_spreadsheet(cls, worksheet_name="Form Responses 1"):
        creds = cls.google_authentication()
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(cls.SPREADSHEET_ID).worksheet(worksheet_name)

        return spreadsheet


def parse_args():
    logger.info("Parsing arguments . . .")

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--db-path", type=Path, default=Path("output/translators.json"))
    parser.add_argument("-s", "--save-path", type=Path, default=Path("output/translators_filtered.json"))
    args = parser.parse_args()

    return args


def main():
    sheet = GoogleSheets.get_spreadsheet()

    rows = sheet.get_all_records()
    # print(rows[:10])


if __name__ == "__main__":
    main()
