import os
import argparse
import logging
import re

from collections import defaultdict
from pathlib import Path

import gspread
from google.auth import default

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
        logger.info("Authenticating to Google Sheets . . .")

        if not os.getenv("GITHUB_ACTIONS"):
            # Running locally
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path("service-account-credentials.json").absolute())

        creds, _ = default(scopes=cls.SCOPES)
        return creds

    @classmethod
    def get_spreadsheet(cls, worksheet_name="Form Responses 1"):
        logger.info("Downloading spreadsheet . . .")

        creds = cls.google_authentication()
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(cls.SPREADSHEET_ID).worksheet(worksheet_name)

        return spreadsheet

    @classmethod
    def process_spreadsheet_data(cls) -> dict:
        # NOTE: We're skipping most checks here as the data is guaranteed to be a table
        spreadsheet = cls.get_spreadsheet()
        spreadsheet_entries = spreadsheet.get_all_records()
        logger.info(f"Found {len(spreadsheet_entries)} records in the spreadsheet . . .")

        # NOTE: Mutate the data in the spreadsheet
        #       * Use the `numar_autorizatie` field as a primary key
        #       * Only record the most-recent entries
        #       * Log any duplicate entries
        translators_by_auth_no = {}
        for entry in spreadsheet_entries:
            # Gather fields
            auth_no = entry["Număr de autorizație"]
            phone_no = entry["Număr de telefon"]
            email = entry["Email Address"]
            other_contact_details = entry["Alte detalii"]
            DI = entry["Sunteți disponibil(ă) pentru interpretariat ? [DI]"]
            DII = entry["Sunteți disponibil(ă) pentru interpretariat la Instanțe ? [DII]"]
            LA = entry["Sunteți înscris pe lista vreunei Ambasade/vreunui Consulat [LA] ?"]

            # Mutate fields (as required)
            auth_no = remove_whitespace(auth_no)
            phone_no = clean_phone_number(phone_no)
            email = remove_whitespace(email).lower()
            DI = "DI" if DI == "Da" else ""
            DII = "DII" if DII == "Da" else ""
            LA = "LA" if LA == "Da" else ""
            other_contact_details = str(other_contact_details).strip()

            # Report duplicates as errors
            if auth_no in translators_by_auth_no.keys():
                logger.error(f"Duplicate translator found with Auth. No.: {auth_no}. Updating with latest info . . .")

            translators_by_auth_no[auth_no] = {
                "Nr. Aut.": auth_no,
                "Contact": "\n".join(filter(None, [phone_no, email, other_contact_details])),
                "DI/DII/LA": "\n".join(filter(None, [DI, DII, LA])),
            }

        return translators_by_auth_no


def parse_args():
    logger.info("Parsing arguments . . .")

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--db-path", type=Path, default=Path("output/translators.json"))
    parser.add_argument("-s", "--save-path", type=Path, default=Path("output/translators_filtered.json"))
    args = parser.parse_args()

    return args


def remove_whitespace(text) -> str:
    return re.sub(r"\s+", "", str(text))


def clean_phone_number(phone_number) -> str:
    phone_number = remove_whitespace(phone_number)

    if phone_number.startswith("40"):  # The "+" from "+40" got escaped
        phone_number = f"+{phone_number}"

    return phone_number


def main():

    google_sheets_data = GoogleSheets.process_spreadsheet_data()


if __name__ == "__main__":
    main()
