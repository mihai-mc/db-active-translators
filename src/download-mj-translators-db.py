import json
import time
import requests
import logging

from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

logger = logging.getLogger(__name__)


class MinistryOfJustice:
    DB_URL = "https://www.just.ro/mj-dmsws/int-mj"
    HEADERS = {"Content-Type": "application/json", "Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    REQUIRED_FILTERS = {
        "nume": "",
        "idCurteApel": "-1",
        "idLimba": "-1",
        "idJudet": "-1",
        "numar_autorizatie": "",
        "telefon": "",
    }
    PAGE_SIZE = 100  # NOTE: Site's native value was `50` (avoid drawing too much attention)
    REQUEST_TIMEOUT = 30
    SLEEP_TIMEOUT = 1.0

    @classmethod
    def download_database(cls, save_path: Path = Path("output/translators.json")) -> None:

        with requests.Session() as session:
            # Create session
            session.headers.update(cls.HEADERS)

            # NOTE: This is BAD but I have neither the time, nor the patience to deal with the government's broken servers
            #       ---
            #       `just.ro` serves an incomplete TLS certificate chain: missing the 'RapidSSL TLS RSA CA G1' intermediate
            #       Disabling certificate verification for this endpoint
            session.verify = False

            # Get the total number of translators
            logger.info("Getting the total number of translators")
            translator_count_response = session.post(
                f"{cls.DB_URL}/traducatori-count", json=cls.REQUIRED_FILTERS, timeout=cls.REQUEST_TIMEOUT
            )
            translator_count_response.raise_for_status()
            translator_count_json = translator_count_response.json()

            # Check that the request's response is valid
            if translator_count_json.get("result") != "OK":
                raise RuntimeError(f"Failed to obtain translator_count_json:\n\n{translator_count_json}")

            number_of_translators = int(translator_count_json["info"])
            logger.info(f"Total number of translators: {number_of_translators}")

            # Download database
            translators = []
            for start in range(1, number_of_translators + 1, cls.PAGE_SIZE):
                # Setting bounds
                end = min(start + cls.PAGE_SIZE, number_of_translators + 1)
                logger.info(f"Downloading translators: {start} ... {end - 1}")

                # Creating request
                database_response = session.post(
                    f"{cls.DB_URL}/traducatori-search",
                    params={"indexStart": start, "indexEnd": end},
                    json=cls.REQUIRED_FILTERS,
                    timeout=cls.REQUEST_TIMEOUT,
                )
                database_response.raise_for_status()

                # Check that the request's response is valid
                translators_json = database_response.json()
                if translators_json.get("result") != "OK":
                    raise RuntimeError(f"Request failed: {translators_json}")

                # Save translators
                translators.extend(translators_json.get("tertList", []))
                logger.info(f"Downloaded {len(translators)} / {number_of_translators}")

                # Sleep before the next request
                time.sleep(cls.SLEEP_TIMEOUT)

        logger.info(f"Download successful! Downloaded: {len(translators)} translators")

        # Dump to file
        save_path.mkdir(exist_ok=True)
        with save_path.open("w", encoding="utf-8") as f:
            json.dump(translators, f, ensure_ascii=False, indent=4)
        logger.info(f"JSON Database saved at: {save_path.absolute()}")

        return


def main():
    MinistryOfJustice.download_database()


if __name__ == "__main__":
    main()
