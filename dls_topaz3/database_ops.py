"""Module for database operations which are necessary for the smooth operation of this package"""

import sqlite3
import logging
import pandas

from pathlib import Path


def prepare_training_database(database, results):
    """Prepare the database for training

    Results input should be a list of tuples in order
    (structure, original_cc, inverse_cc, original_score, inverse_score)

    To go into database.table columns:
    Name - varchar(4), original_cc - float, inverse_cc - float, original_score - float, inverse_score - float

    If database.table does not exist, it will be created in this format
    """

    # Check database exists and data is formatted correctly
    assert Path(database).exists(), f"Could not find database at {database}"
    assert type(results) == list, "Please provide a formatted list for results"
    assert len(results) > 0, "No results provided"
    assert all(
        len(result) == 5 for result in results
    ), "Must provide correct format for results - see documentation"

    logging.info("Preparing training database")

    # Initiate connection to the database
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
    except Exception:
        logging.error(f"Could not connect to database at {database}")
        raise

    try:
        # Create the table if it does not exist
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS ai_training (Name varchar(4) PRIMARY KEY, original_cc FLOAT, inverse_cc FLOAT, original_score BOOL, inverse_score BOOL)"
        )
    except Exception:
        logging.error("Could not find or create ai_training table")
        raise

    try:
        # Add new values
        cursor.executemany("REPLACE INTO ai_training VALUES (?, ?, ?, ?, ?)", results)
    except Exception:
        logging.error("Error placing values into table, please check results provided")
        raise

    # Save changes and close
    conn.commit()
    conn.close()

    logging.info("Successful write to database")

    return True


def prepare_labels_database(database):
    """Take the existing database and convert it to a clear name and labels database which can be easily read for ai training"""
    # Check database exists
    assert Path(database).exists(), f"Could not find database at {database}"

    # Initiate connection to the database
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
    except Exception:
        logging.error(f"Could not connect to database at {database}")
        raise

    # Read table into pandas dataframe
    data = pandas.read_sql(f"SELECT * FROM ai_training", conn)

    # Create the new dataframe
    sorted_data_original = [{"Name": data["Name"][index], "Label": data["original_score"][index]} for index in range(len(data["Name"]))]
    sorted_data_inverse = [{"Name": f"{data['Name'][index]}_i", "Label": data["inverse_score"][index]} for index in range(len(data["Name"]))]
    new_dataframe = pandas.DataFrame(sorted_data_original + sorted_data_inverse)
    sorted_dataframe = new_dataframe.set_index("Name").sort_index()

    # Empty an existing new table
    try:
        cursor.execute(f"DROP TABLE IF EXISTS ai_labels")
    except Exception:
        logging.error("Could not find or create new table")
        raise

    # Put the sorted dataframe in the new table
    try:
        sorted_dataframe.to_sql("ai_labels", conn)
    except:
        logging.error(f"Could not write sorted dataframe to ai_labels")
        raise

    logging.info(f"Successful write of sorted table")

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    prepare_training_database(
        "/dls/science/users/riw56156/topaz_test_data/metrix_db_20190403.sqlite",
        [("ABC4", 5.0, 11, False, True), ("A3C4", 79, 2.1, True, False)],
    )

    prepare_labels_database(
        "/dls/science/users/riw56156/topaz_test_data/metrix_db_20190403.sqlite",
    )
