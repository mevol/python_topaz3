"""Command line tool to enable entire image preparation step from yaml config file"""

import argparse
import logging
import os
from pathlib import Path
import sys
import yaml

import sqlite3

from topaz3.prepare_training_data import prepare_training_data
from topaz3.maps_to_images import directory_to_images

example_config = """phase_dir: /phase/directory/path
cell_info_dir: /cell/info/directory
cell_info_path: cell/info/path.mtx
space_group_dir: /space/group/directory
space_group_path: space/group/path.log
xyz_limits:
  - 200
  - 200
  - 200
db_path: /db/is/here.db
maps_dir: /output/maps/directory
slices_per_axis: 20
images_dir: /output/images/directory
"""


def params_from_yaml(args):
    """Extract the parameters for preparation from a yaml file and return a dict"""
    # Check the path exists
    try:
        config_file_path = Path(args.config_file)
        assert config_file_path.exists()
    except Exception:
        logging.error(f"Could not find config file at {args.config_file}")
        raise

    # Load the data from the config file
    try:
        with open(config_file_path, "r") as f:
            params = yaml.safe_load(f)
    except Exception:
        logging.error(
            f"Could not extract parameters from yaml file at {config_file_path}"
        )
        raise

    if "db_path" not in params.keys():
        params["db_path"] = None

    if "delete_temp" not in params.keys():
        params["delete_temp"] = True

    if "verbose" not in params.keys():
        params["verbose"] = True

    return params


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Transform a large directory of cells with phase information "
        "into labelled image slices ready for AI training.\n "
        "See https://github.com/TimGuiteDiamond/topaz3 for further details"
    )

    parser.add_argument(
        "config_file", help="yaml file which contains parameters for data preparation"
    )
    parser.add_argument(
        "--make-output",
        action="store_true",
        help="automatically generate maps and images directories and database for output",
    )
    parser.add_argument(
        "--example", action="store_true", help="creates example in the config_file"
    )

    args = parser.parse_args()

    print(args)

    if args.example:
        logging.info(f"Creating example in {args.config_file}")
        with open(args.config_file, "w") as cf:
            cf.write(example_config)
        sys.exit(0)

    logging.info(f"Extracting parameters from {args.config_file}")
    parameters = params_from_yaml(args)

    if args.make_output:
        logging.info("Generating output directories")
        try:
            os.mkdir(parameters["maps_dir"])
        except TypeError:
            logging.error(
                f"Expected file path for maps_dir, got {parameters['maps_dir']}"
            )
            raise
        except FileExistsError:
            logging.error(f"Using existing maps_dir at {parameters['maps_dir']}")
        except PermissionError:
            logging.error(
                f"Do not have permission to create maps_dir at {parameters['maps_dir']}"
            )
            raise

        try:
            os.mkdir(parameters["images_dir"])
        except TypeError:
            logging.error(
                f"Expected file path for images_dir, got {parameters['images_dir']}"
            )
            raise
        except FileExistsError:
            logging.error(f"Using existing images_dir at {parameters['images_dir']}")
        except PermissionError:
            logging.error(
                f"Do not have permission to create images_dir at {parameters['images_dir']}"
            )
            raise

        if parameters["db_path"] is not None:
            logging.info("Creating database")
            try:
                conn = sqlite3.connect(parameters["db_path"])
            except sqlite3.Error:
                logging.error(f"Issue creating database at {parameters['db_path']}")
                raise
            finally:
                conn.close()

    logging.info(f"Converting phase files to map files")
    prepare_training_data(
        parameters["phase_dir"],
        parameters["cell_info_dir"],
        parameters["cell_info_path"],
        parameters["space_group_dir"],
        parameters["space_group_path"],
        parameters["xyz_limits"],
        parameters["maps_dir"],
        parameters["db_path"],
    )

    logging.info(f"Slicinig maps into images")
    directory_to_images(
        parameters["maps_dir"],
        parameters["slices_per_axis"],
        parameters["images_dir"],
        parameters["verbose"],
    )


if __name__ == "__main__":

    main()
