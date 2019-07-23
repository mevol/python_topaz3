"""
Script to split a directory into training and testing samples.

Can take a directory filled with subdirectories (which should all be equal)
or a directory of similar files (same extension).

Copies the test samples to the test directory provided and then deletes them
from the original location.
"""

import logging
import random
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

    # Get random indexes
    random_indexes = [int(random.random()) * len(file_list) for i in range(split_num)]

    return random_indexes


if __name__ == "__main__":
    print(test_split([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10))
    print(test_split([], 10))
