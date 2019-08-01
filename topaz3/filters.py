"""Module to perform some simple filtering on image files"""

import argparse
import logging
import os
from pathlib import Path
from typing import Callable

from matplotlib.image import imread, imsave
from scipy.ndimage import gaussian_filter, median_filter

# Dictionary to map string values to filter functions, add more as necessary
available_filters = {"gaussian": gaussian_filter, "median": median_filter}


def filter_file(
    input_file: str, output_file: str, filter: Callable, parameters: dict = {}
):
    """
    Read the input file, apply filter with expanded parameters as keywords and save in the output file location

    :param input_file: file to be filtered
    :param output_file: save output here
    :param filter: apply this filter
    :param parameters: give these parameters to filter
    :return: output file location
    """

    assert Path(input_file).exists(), f"Could not find file at {input_file}"
    assert isinstance(
        parameters, dict
    ), f"Expected dict for parameters, got {parameters} of type {type(parameters)}"

    try:
        # Imread only takes string types, not PosixPath from pathlib
        input_image = imread(str(input_file))
    except Exception:
        logging.exception(f"Could not read image from {input_file}")
        raise

    try:
        output_image = filter(input_image, **parameters)
    except TypeError:
        logging.error(f"Using paramaters: {parameters}")
        logging.exception(
            f"Make sure you are providing key, pair values according to the specification of the filter: {filter}"
        )
        raise
    except Exception:
        logging.exception(f"Could not filter {input_file} with {filter}")
        raise

    try:
        imsave(output_file, output_image)
    except PermissionError:
        logging.exception(f"Do not have permission to save file at {output_file}")
        raise
    except Exception:
        logging.exception(f"Could not save image at {output_file}")

    return output_file


def filter_directory(
    input_directory: str, output_directory: str, filter: Callable, parameters: dict = {}
):
    """
    Filter every file in the input directory and save to output directory

    :param input_directory: filter all files from this directory
    :param output_directory: output files here
    :param filter: filter to apply
    :param parameters: parameters for filter
    :return: True
    """
    logging.info(f"Transforming files from {input_directory} to {output_directory}")

    assert Path(
        input_directory
    ).exists(), f"Could not find input directory at {input_directory}"
    assert isinstance(
        parameters, dict
    ), f"Expected dict for parameters, got {parameters} of type {type(parameters)}"
    if not Path(output_directory).exists():
        try:
            os.mkdir(output_directory)
        except Exception:
            logging.exception(
                f"Could not create output directory at {output_directory}"
            )

    input_files = [file for file in Path(input_directory).iterdir()]
    for i in range(len(input_files)):
        print(f"Filtering image {i+1} of {len(input_files)}", end="\r")
        filter_file(
            input_files[i],
            Path(output_directory) / Path(input_files[i]).name,
            filter,
            parameters,
        )


def string_or_number(input: str):
    """Returns an integer if sting is integer or float if string is float otherwise just hand back the string"""
    try:
        return int(input)
    except ValueError:
        try:
            return float(input)
        except ValueError:
            return input


def filter_command_line():
    """Run the filter from the command line"""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Filter all images from input_dir to output_dir using the filter selected."
        "Pass extra arguments to the filtter using key value pairs from the command line"
        " separated by the equals sign, e.g key=value"
    )

    parser.add_argument("input_dir", help="path of directory to filter images from")
    parser.add_argument("output_dir", help="path of directory to output files to")
    parser.add_argument(
        "filter",
        help=f"choose filter to apply from: {', '.join([k for k in available_filters.keys()])}",
    )

    args, unknown_args = parser.parse_known_args()
    logging.debug(args)
    logging.debug(unknown_args)

    # Check filter is available
    assert (
        args.filter in available_filters
    ), f"Got filter {args.filter}, please choose from {available_filters}"

    # Create parameters_dict
    # Create list of key value pairs separated by equals signs
    arg_pairs = [arg.split("=") for arg in unknown_args]
    logging.debug(arg_pairs)

    # Check all values are pairs now
    assert (
        all([len(args) == 2 for args in arg_pairs]) is True
    ), f"Expected key value pairs separated by '=' sign, got {arg_pairs}"

    # Turn pairs into dict, converting numbers where possible
    parameters_dict = {key: string_or_number(value) for key, value in arg_pairs}
    logging.debug(parameters_dict)

    # Run the function
    filter_directory(
        args.input_dir, args.output_dir, available_filters[args.filter], parameters_dict
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    filter_command_line()
