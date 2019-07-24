"""
Script to split a directory into training and testing samples.

Can take a directory filled with subdirectories (which should all be equal)
or a directory of similar files (same extension).

Copies the test samples to the test directory provided and then deletes them
from the original location.
"""

import argparse
import logging
import os
import random
import shutil
from pathlib import Path
from typing import Tuple


def test_split(file_list: Tuple, split_percent: float) -> Tuple:
    """
    Takes in a tuple or list of file or directory locations,
    returns a list of randomly selected files according to the split_percent

    :param file_list: list to get a subset of
    :param split_percent: percentage of files to split off and return, must be between 1 and 99
    :returns: randomly selected subset of list
    """
    try:
        assert 0 <= split_percent <= 100
        assert isinstance(split_percent, float) or isinstance(split_percent, int)
    except AssertionError:
        logging.error(f"Expected float between 0 and 100, got {split_percent}")

    # How many files to split
    split_num = int(len(file_list) * (split_percent / 100))
    assert (
        split_num > 0
    ), "Split percentage and/or number of files not big enough to create a test split."

    # Seed random for predictable output
    random.seed(9)

    # Guarantees selection without replacement (no duplicates in output set given no duplicates in input set)
    random_files = random.sample(file_list, split_num)

    return random_files


def test_split_directory(
    input_directory: str, split_percent: float, output_directory: str
) -> Tuple:
    """
    Move files or directories from input dir to output dir to separate training and test
    information.

    Looks for all files in the input directory, checks they are all of the same type.
    This means either all directories, or all files with the same file extension.
    Randomly selects split_percent % of them to be moved to the output directory.
    Random number generator is seeded so this is a deterministic translation.

    Copies selected files to output directory then deletes.
    This ensures that all copying is completed before any deletion takes place.
    If there is an error during copying then function can be ran again with same
    parameters (once error is fixed).

    If the input directory contains subdirectories, they will be moved recursively.

    Returns a tuple of the new file locations.

    :param input_directory: directory to randomly select from
    :param split_percent: percentage (0-100) of files to move
    :param output_directory: new location for selected files
    :return: tuple of new file locations
    """

    logging.info(
        f"Performing test split of {split_percent}% of files from {input_directory} to {output_directory}"
    )

    try:
        input_dir_path = Path(input_directory)
        assert input_dir_path.exists()
    except (TypeError, AssertionError):
        logging.error(f"Expected existing input directory, got {input_directory}")
        raise

    assert (
        input_directory is not output_directory
    ), f"Expected different input and output directory, got {input_directory} and {output_directory}"

    # Get list of files in directory
    input_files = [file for file in input_dir_path.iterdir()]
    assert len(input_files) > 0, f"Found no files in {input_dir_path}"
    logging.info(f"Found {len(input_files)} files/dirs to be randomly selected from")

    # Check files are all consistent with one another
    # Gets the set of whether files are directories or not, as they should all be the same
    # this is a straightforward comparison to the expected sets
    all_directories = set([file.is_dir() for file in input_files])
    assert all_directories == {True} or all_directories == {
        False
    }, f"Expected all directories or all files in {input_directory}, got mixture"
    # Gets the set of all file extensions, there should only be one
    # Directories return "" which will also suffice
    file_extensions = set([file.suffix for file in input_files])
    assert (
        len(file_extensions) == 1
    ), f"Expected single file type in {input_directory}, got {file_extensions}"

    # Perform the split
    selected_files = test_split(input_files, split_percent)
    logging.info(f"Randomly selected {len(selected_files)} files/dirs to be moved")

    # Use different functions depending on whether using files or directories
    # More options could be added in the future if there is need for special handling
    # selected_files should have at least 1 value so safe to check
    if Path(selected_files[0]).is_dir():
        copied_file_locations = copy_directories(selected_files, output_directory)
        # Remove the original directories
        logging.info(f"Removing directories from {input_directory}")
        for directory in selected_files:
            shutil.rmtree(directory)
    else:
        copied_file_locations = copy_files(selected_files, output_directory)
        # Remove the original files
        logging.info(f"Removing files from {input_directory}")
        for file in selected_files:
            os.remove(file)

    return copied_file_locations


def copy_files(file_list: Tuple, destination: str) -> Tuple:
    """Takes a list of files and copies them to the destination"""
    logging.info(f"Copying files to {destination}")
    try:
        # shutil.copy returns the file destination
        new_file_locations = [shutil.copy(file, destination) for file in file_list]
    except OSError:
        logging.error(f"Error copying to {destination}")
        raise
    except shutil.SameFileError:
        logging.error(
            f"Source file and destination file are the same when copying to {destination}"
        )
        raise

    return new_file_locations


def copy_directories(dir_list: Tuple, destination: str) -> Tuple:
    """
    Takes a list of directories and copies their trees to the destination with their name as the top
    level directory.

    Example: copy_directories(["/my/stuff"], "your") copies to "/your/stuff".

    **Note:** The destination file should be empty as shutil.copytree will not work if there is already
    a file or directory at the destination path.

    Returns a list of the new top level file locations
    """
    logging.info(f"Copying directory trees to {destination}")
    try:
        # shutil.copytree returns the file destination
        new_file_locations = [
            shutil.copytree(directory, (Path(destination) / Path(directory).name))
            for directory in dir_list
        ]
    except FileExistsError as e:
        logging.error(
            f"File or directory already exists at {e.filename}, so cannot overwrite"
        )
        raise
    except OSError:
        logging.error(f"Error copying to {destination}")
        raise

    return new_file_locations


def command_line():
    """Command line wrapper for test_split_directory"""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Tool to randomly select a number of files/ or directories from an input directory and move them to the output directory. "
        "Random number generator is seeded so this is a repeatable process given the same file inputs. "
        "Input directory must contain either all directories or all files of the same type. "
        "This helps to prevent unwanted files from affecting the test split produced."
    )

    parser.add_argument("input_dir", type=str, help="directory to move files/dirs from")
    parser.add_argument(
        "output_dir", type=str, help="selected files/dirs will be moved here"
    )
    parser.add_argument(
        "--split_percent",
        type=float,
        default=5.0,
        help="percentage of files/dirs to randomly select and move",
    )

    args = parser.parse_args()

    # Execute function
    new_file_locations = test_split_directory(
        args.input_dir, args.split_percent, args.output_dir
    )
    print(
        f"Successfully moved {len(new_file_locations)} files/dirs from {args.input_dir} to {args.output_dir}"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    command_line()
