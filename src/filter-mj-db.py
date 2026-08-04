import argparse
import json
import logging

from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

logger = logging.getLogger(__name__)


def parse_args():
    logger.info("Parsing arguments . . .")

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--db-path", type=Path, default=Path("output/translators.json"))
    parser.add_argument("-s", "--save-path", type=Path, default=Path("output/translators_filtered.json"))
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    # Load JSON
    logger.info(f"Loading translator database from {args.db_path} . . .")
    with open(args.db_path, "r") as f:
        translators_json = json.load(f)

    # Check that all entries have identical fields
    logger.info("Checking database entries . . .")
    assert all([translators_json[0].keys() == t.keys() for t in translators_json]), "Entries differ in the database !"

    # Convert from list[dicts] to dict[lists]
    logger.info("Convert database entries to dict . . .")
    translators_dict = defaultdict(list)
    for translator in translators_json:
        for k, v in translator.items():
            translators_dict[k].append(v)

    # Assessing the number of entries in each field
    len_per_entry = [len(v) for v in translators_dict.values()]
    same_length = all([len_per_entry[0] == e for e in len_per_entry])
    assert same_length, "The database fields DO NOT have the same number of entries!"
    number_of_entries = len_per_entry[0]
    logger.info(f"Found {number_of_entries} entries in the database!")

    # Discard the HTTP "result" field
    logger.info("Inspecting HTTP results codes . . .")
    results_ok = all([x == "OK" for x in translators_dict["result"]])
    assert results_ok, "Some entries did not have an 'OK' (HTPP 200 code). You should investigate this!"

    translators_dict.pop("result")

    # Assess which fields actually contain useful data
    logger.info("Assessing which fields to discard . . .")
    fields_to_keep = []
    for k, v in translators_dict.items():
        filtered_values = filter(lambda x: x is not None and x != "" and x != [], v)
        if len(list(filtered_values)) != 0:  # List not empty
            fields_to_keep.append(k)
    fields_to_keep.sort()

    logger.info(f"Keeping the following fields: {fields_to_keep}")
    logger.info(f"Discarding the following fields: {translators_dict.keys() - set(fields_to_keep)}")

    # NOTE: The `numar_autorizatie` field is guaranteed to be unique, so we use it as a primary key
    logger.info("Construct filtered database using the `numar_autorizatie` as a primary key")
    translators_by_auth_no = {}
    for translator in translators_json:
        auth_no = translator["numar_autorizatie"]
        translator_details_subset = {k: v for k, v in translator.items() if k in fields_to_keep}

        # Only copy over the useful fields
        translators_by_auth_no[auth_no] = translator_details_subset

    # Dump back to .json
    logger.info(f"Save filtered database to {args.save_path}")
    with open(args.save_path, "w") as f:
        json.dump(translators_by_auth_no, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
