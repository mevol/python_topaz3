"""Find the space group information from a file, should work for multiple file inputs"""

import re
import os
from pathlib import Path
import logging
import procrunner

def find_space_group(text):
    """Open the filename at this path and try to extract a space group. Return space group string."""

    #Get the results which match lines of space group
    potential_lines = re.findall("(?<=[sS]pace [gG]roup)(.*)", text)
    logging.debug(potential_lines)

    #Get results which match the format of a space group - join for easier search and output
    potential_groups = re.findall("[A-Z][ 0-9]+", "\n".join(potential_lines))
    logging.debug(potential_groups)

    space_groups = [group.replace(" ", "") for group in potential_groups]
    logging.debug(space_groups)

    if len(space_groups) == 0:
        logging.warning("Could not find space group")
        raise Exception("Could not find any space groups in text")

    #If there are multiple results, use the first one
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
    except Exception as e:
        logging.warning(f"Could not open file at {file}")
        raise

    logging.debug("Searching for space group")
    try:
        space_group = find_space_group(text)
    except Exception as e:
        logging.warning(f"Could not find space group in {file}")
        raise

    return space_group


def mtz_find_space_group(mtzfile):
    """Dump the content of an mtz file and inspect it for space groups"""

    # Check input file is of correct type
    mtz_filepath = Path(mtzfile)
    assert mtz_filepath.exists(), f"Could not find file at {mtzfile}"
    assert mtz_filepath.suffix==".mtz", f"Expected mtz file, found {mtz_filepath}"

    # Get location of shell script
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    phenix_shell = os.path.join(__location__, 'shell_scripts/phenix_dump.sh')

    # Build up command list
    command = [phenix_shell, mtz_filepath]

    logging.info(f"Command: {command}")

    # Run external program
    result = procrunner.run(command, print_stdout=False)

    # Check that it worked
    #Only using one assert because module load command raises an error even if it works properly
    assert result["exitcode"] == 0, f"Error dumping {mtz_filepath}"

    # Decode output from bytes to UTF-8 string
    text = str(result["stdout"], "utf-8")

    logging.debug("Searching for space group")
    try:
        space_group = find_space_group(text)
    except Exception as e:
        logging.warning(f"Could not find space group in {mtz_filepath}")
        raise

    return space_group


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    print(textfile_find_space_group("/dls/science/users/riw56156/topaz_test_data/phenix_output.txt"))
    print(textfile_find_space_group("/dls/science/users/riw56156/topaz_test_data/simple_xia2_to_shelxcde.log"))
    print(mtz_find_space_group("/dls/science/users/riw56156/topaz_test_data/AUTOMATIC_DEFAULT_free.mtz"))