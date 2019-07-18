"""Find the space group information from a file, should work for multiple file inputs"""

import logging
import os
import re
import sys
from pathlib import Path

import procrunner


def find_space_group(text):
    """Open the filename at this path and try to extract a space group. Return space group string."""

    # Get the results which match lines of space group
    potential_lines = re.findall("(?<=[sS]pace [gG]roup)(.*)", text)
    logging.debug(potential_lines)

    # Get results which match the format of a space group - join for easier search and output
    potential_groups = re.findall("[A-Z][ 0-9]+", "\n".join(potential_lines))
    logging.debug(potential_groups)

    space_groups = [group.replace(" ", "") for group in potential_groups]
    logging.debug(space_groups)

    if len(space_groups) == 0:
        logging.warning("Could not find space group")
        raise Exception("Could not find any space groups in text")

    # If there are multiple results, use the first one
    logging.debug(space_groups[0])
    return space_groups[0]


def textfile_find_space_group(file):
    """Open a normal text file and send the text to find_space_group. Return space group if found."""
    # Check file exists
    filepath = Path(file)
    assert filepath.exists(), f"Could not find file at {filepath}"

    logging.debug(f"Reading from {file}")
    try:
        with open(file, "r") as f:
            text = f.read()
    except Exception:
        logging.error(f"Could not read from file at {file}")
        raise

    logging.debug("Searching for space group")
    try:
        space_group = find_space_group(text)
    except Exception:
        logging.error(f"Could not find space group in {file}")
        raise

    return space_group


def mtz_find_space_group(mtzfile):
    """Dump the content of an mtz file and inspect it for space groups"""

    # Check input file is of correct type
    mtz_filepath = Path(mtzfile)
    assert mtz_filepath.exists(), f"Could not find file at {mtzfile}"
    assert mtz_filepath.suffix == ".mtz", f"Expected mtz file, found {mtz_filepath}"

    # Get location of shell script
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    phenix_shell = os.path.join(__location__, "shell_scripts/phenix_dump.sh")

    # Build up command list
    command = [phenix_shell, mtz_filepath]

    logging.info(f"Command: {command}")

    # Run external program
    result = procrunner.run(command, print_stdout=False, timeout=5)

    # Check that it worked
    # Module load command raises an error even if it works properly
    assert result["exitcode"] == 0, f"Error dumping {mtz_filepath}"
    assert result["timeout"] == 0, f"Error dumping {mtz_filepath}"

    # Decode output from bytes to UTF-8 string
    text = str(result["stdout"], "utf-8")

    logging.debug("Searching for space group")
    try:
        space_group = find_space_group(text)
    except Exception:
        logging.error(f"Could not find space group in {mtz_filepath}")
        raise

    return space_group


if __name__ == "__main__":

    filename = sys.argv[1]

    logging.info(f"Get space group information from {filename}")

    filepath = Path(filename)

    # Try to get an absolute file path
    current_dir = Path(os.getcwd())

    if Path(current_dir / filepath).exists():
        abs_path = Path(current_dir / filepath)
    else:
        # Check for absolute path
        assert filepath.exists(), f"Could not find a file for {filepath}"
        abs_path = filepath

    # Use text or mtz file?
    if abs_path.suffix == ".mtz":
        logging.info("Detected mtz file...")
        print(mtz_find_space_group(abs_path))
    else:
        logging.info("Using text file analysis...")
        print(textfile_find_space_group(abs_path))
