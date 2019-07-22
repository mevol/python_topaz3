"""This file contains the main script for converting phase information
into a regularly sized electron density map using tools from CCP4"""

import logging
import os
from pathlib import Path
from typing import Tuple

import procrunner

from topaz3.mtz_info import mtz_get_cell
from topaz3.space_group import mtz_find_space_group, textfile_find_space_group

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def phs_to_mtz(
    phase_filename: str, cell_info: Tuple, space_group: str, output_filename: str
):
    """Use the CCP4 f2mtz utility to convert a phase file into a .mtz file
     and return the mtz file location.

    :param phase_filename: input phase file to be transformed
    :param cell_info: list of 6 floating point values with cell information
    :param space_group: space group for structure, e.g "P212121"
    :param output_filename: absolute path for the mtz output file
    :returns: location of the mtz file
     """
    try:
        phase_filepath = Path(phase_filename)
        output_filepath = Path(output_filename)
    except Exception:
        raise Exception("Inputs must be paths of input phase file and output mtz file.")

    logger.debug(f"Converting phase to mtz")
    logger.debug(f"Input file at {phase_filepath}")
    logger.debug(f"Output file at {output_filepath}")

    # Check parameters coming in
    assert (
        phase_filepath.suffix == ".phs" or phase_filepath.suffix == ".pha"
    ), "Please provide a phase_filename which points to the phase file you wish to convert."
    assert phase_filepath.exists(), f"Could not find a valid file at {phase_filepath}."
    assert (
        output_filepath.suffix == ".mtz"
    ), "Please provide an output_filename with a .mtz extension."
    assert (
        output_filepath.parent.exists()
    ), f"Could not find output directory at {output_filepath.parent}"
    try:
        assert len(cell_info) == 6
        # Will raise error if values are not floats
        assert [float(value) for value in cell_info]
    except Exception:
        raise Exception(
            "Cell info must be list of 6 floating numbers for the cell lengths and angles."
        )

    # Convert list of cells info into string
    cell_info_string = " ".join([str(cell) for cell in cell_info])

    # Catch strange R/H space group inconsistency (different between different programs)
    if space_group[0] == "R":
        space_group = "H" + space_group[1:]

    # Build up keywords
    keywords = "\n".join(
        [
            f"CELL {cell_info_string}",
            f"SYMM {space_group}",
            "labout H K L F FOM PHI SIGF",
            "CTYPOUT H H H F W P Q",
        ]
    )

    logger.debug(f"Keywords: {keywords}")

    # Convert to bytes
    b_keywords = bytes(keywords, "utf-8")

    # Get location of shell script
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    cfft_shell = os.path.join(__location__, "shell_scripts/f2mtz.sh")

    # Build up command list
    command = [cfft_shell, "hklin", phase_filepath, "hklout", output_filepath]

    logger.debug(f"Command: {command}")

    # Run external program
    result = procrunner.run(command, stdin=b_keywords, print_stdout=False, timeout=5)

    # Check that it worked
    assert (
        result["exitcode"] == 0
    ), f"Error converting {phase_filepath} to {output_filepath}"
    assert (
        result["stderr"] == b""
    ), f"Error collecting information from {phase_filepath} to {output_filepath}"
    assert (
        result["timeout"] is False
    ), f"Error collecting information from {phase_filepath} to {output_filepath}"

    logger.debug("Conversion successful")

    return output_filepath


def mtz_to_map(mtz_filename, output_filename):
    """Convert .mtz file to map using CCP4 cfft utility and return the new output map location.

    :param mtz_filename: input mtz file
    :param output_filename: absolute path for the mtz output file
    :returns: location of the mtz file
    """

    try:
        mtz_filepath = Path(mtz_filename)
        output_filepath = Path(output_filename)
    except Exception:
        raise Exception("Inputs must be paths of input mtz file and output map file.")

    logger.debug(f"Converting mtz to map")
    logger.debug(f"Input file at {mtz_filepath}")
    logger.debug(f"Output file at {output_filepath}")

    # Check parameters coming in
    assert (
        mtz_filepath.suffix == ".mtz"
    ), "Please provide an mtz_filename which points to the .mtz file you wish to convert."
    assert mtz_filepath.exists(), f"Could not find a valid file at {mtz_filepath}"
    assert (
        output_filepath.suffix == ".map"
    ), "Please provide an output_filename with a .map extension."
    assert (
        output_filepath.parent.exists()
    ), f"Could not find output directory at {output_filepath.parent}"

    # Build up standard input for cfft utility
    keywords = "\n".join(
        [
            f"mtzin {mtz_filename}",
            "colin-fc /*/*/[F,PHI]",
            f"mapout {output_filename}",
            "stats",
            "stats-radius 4.0",
        ]
    )

    logger.debug(f"Keywords: {keywords}")

    # Convert to bytes
    b_keywords = bytes(keywords, "utf-8")

    # Get location of shell script
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    cfft_shell = os.path.join(__location__, "shell_scripts/cfft.sh")

    # Run external program
    result = procrunner.run(
        [cfft_shell, "-stdin"], stdin=b_keywords, print_stdout=False, timeout=5
    )

    # Check that it worked
    assert (
        result["exitcode"] == 0
    ), f"Error converting {mtz_filepath} to {output_filepath}"
    assert (
        result["stderr"] == b""
    ), f"Error collecting information from {mtz_filepath} to {output_filepath}"
    assert (
        result["timeout"] is False
    ), f"Error collecting information from {mtz_filepath} to {output_filepath}"

    logger.debug("Conversion successful")

    return output_filepath


def map_to_map(
    map_filename: str,
    xyz_limits: Tuple[int, int, int],
    space_group: str,
    output_filename: str,
):
    """Converts a map file to a map file with specific xyz dimensions and returns the output file location

    :param phase_filename: input phase file to check for bad values
    :param space_group: space group for structure, e.g "P212121"
    :param xyz_limits: size limits for the x, y, z axes of the output map
    :param output_filename: absolute path for the map output file
    :returns: location of output map
    """

    try:
        map_filepath = Path(map_filename)
        output_filepath = Path(output_filename)
    except Exception:
        raise Exception("Inputs must be paths of input map file and output map file.")

    logger.debug(f"Converting map to map")
    logger.debug(f"Input file at {map_filepath}")
    logger.debug(f"Output file at {output_filepath}")

    # Check parameters coming in
    assert (
        map_filepath.suffix == ".map"
    ), "Please provide a map_filename which points to the .map file you wish to convert."
    assert map_filepath.exists(), f"Could not find a valid file at {map_filepath}"
    assert (
        output_filepath.suffix == ".map"
    ), "Please provide an output_filename with a .map extension."
    assert (
        output_filepath.parent.exists()
    ), f"Could not find output directory at {output_filepath.parent}"
    try:
        assert len(xyz_limits) == 3
        # Will raise error if values are not integers
        assert all(type(value) == int for value in xyz_limits)
    except Exception:
        raise Exception(
            "XYZ Limits must be list of 3 integers for the XYZ dimension of the new map."
        )

    # Catch strange R/H space group inconsistency (different between different programs)
    if space_group[0] == "R":
        space_group = "H" + space_group[1:]

    # Build up keywords
    keywords = "\n".join(
        [
            f"XYZLIM 0 {xyz_limits[0]} 0 {xyz_limits[1]} 0 {xyz_limits[2]}",
            "EXTEND XTAL",
            f"SYMM {space_group}",
        ]
    )

    logger.debug(f"Keywords: {keywords}")

    # Convert to bytes
    b_keywords = bytes(keywords, "utf-8")

    # Get location of shell script
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    cfft_shell = os.path.join(__location__, "shell_scripts/mapmask.sh")

    # Build up command list
    command = [cfft_shell, "mapin", map_filepath, "mapout", output_filepath]

    logger.debug(f"Command: {command}")

    # Run external program
    result = procrunner.run(command, stdin=b_keywords, print_stdout=False, timeout=5)

    # Check that it worked
    assert (
        result["exitcode"] == 0
    ), f"Error converting {map_filepath} to {output_filepath}"
    assert (
        result["stderr"] == b""
    ), f"Error collecting information from {map_filepath} to {output_filepath}"
    assert (
        result["timeout"] is False
    ), f"Error collecting information from {map_filepath} to {output_filepath}"

    logger.debug("Conversion successful")

    return output_filepath


def phase_to_map(
    phase_filename: str,
    cell_info: Tuple,
    space_group: str,
    xyz_limits: Tuple[int, int, int],
    output_filename: str,
):
    """
    Convert a phase file to a regularised map file with dimensions x, y, z using the space group and cell info provided.

    :param phase_filename: input phase file to check for bad values
    :param cell_info: list of 6 floating point values with cell information
    :param space_group: space group for structure, e.g "P212121"
    :param xyz_limits: x, y, z, size of the map output
    :param output_filename: absolute path for the map output file
    :returns: True
    """

    try:
        phase_filepath = Path(phase_filename)
        output_filepath = Path(output_filename)
    except Exception:
        raise Exception("Inputs must be paths of input phase file and output map file.")

    assert (
        output_filepath.parent.exists()
    ), f"Could not find directory for output file, expected at {output_filepath.parent}"

    logger.debug(f"Beginning phase to map conversion")
    logger.debug(f"Input: {phase_filepath}")
    logger.debug(f"Output: {output_filepath}")

    # Create temporary file names
    mtz_filepath = output_filepath.parent / (output_filepath.stem + "_temp.mtz")
    map_filepath = output_filepath.parent / (output_filepath.stem + "_temp.map")

    # Convert phase to mtz
    phs_to_mtz(phase_filepath, cell_info, space_group, mtz_filepath)

    # Convert mtz to map
    mtz_to_map(mtz_filepath, map_filepath)

    # Convert map to regularized map
    map_to_map(map_filepath, xyz_limits, space_group, output_filepath)

    # Check that file was created
    assert output_filepath.exists(), "Output file path was not created"

    logger.debug(f"Map successfully generated at {output_filepath}")

    return True


def phase_remove_bad_values(phase_filename: str, output_filename: str) -> str:
    """
    Inspects a phase file looking for lines with ******** values which represent bad data.
    If these lines are found, remove and write a temporary phase file out.
    Returns the filepath of the temporary file created, otherwise returns the original filepath

    :param phase_filename: input phase file to check for bad values
    :param output_filename: file to store filtered output in if necessary
    :returns: path of file with good values in
    """
    try:
        phase_filepath = Path(phase_filename)
        output_filepath = Path(output_filename)
    except Exception:
        raise Exception("Inputs must be absolute paths to files.")

    with open(phase_filepath, "r") as phase_data:
        lines = [line for line in phase_data]
        filtered_phase = [line for line in lines if "******" not in line]

    if (len(lines)) == len(filtered_phase):
        return phase_filename
    else:
        # Write out to temporary file and return that
        with open(output_filepath, "w") as filtered_phase_file:
            filtered_phase_file.writelines(filtered_phase)
        return output_filename


def files_to_map(
    phase_filename: str,
    cell_info_filename: str,
    space_group_filename: str,
    xyz_limits: Tuple[int, int, int],
    output_filename: str,
):
    """
    Extract information from files before running the phase to map conversion.

    Checks phase file provided for bad values and amends if necesary with *phase_remove_bad_values*

    :param phase_filename: phase file to convert to map
    :param cell_info_filename: file with cell info, normally .mtz
    :param space_group_filename: file with space group information, can be .mtz or other (.log, .txt, etc)
    :param xyz_limits: x, y, z, size of the map output
    :param output_filename: absolute path for the map output file. This will be used to generate temporary file names for the intermediate files
    :return: True
    """

    try:
        phase_filepath = Path(phase_filename)
        output_filepath = Path(output_filename)
        cell_info_filepath = Path(cell_info_filename)
        space_group_filepath = Path(space_group_filename)
    except Exception:
        raise Exception("Inputs must be absolute paths to files.")

    # Check incoming files (which won't be checked later)
    assert cell_info_filepath.exists(), f"Could not find file at {cell_info_filepath}"
    assert (
        cell_info_filepath.suffix == ".mtz"
    ), f"Expected .mtz file, got {cell_info_filepath}"
    assert (
        space_group_filepath.exists()
    ), f"Could not find file at {space_group_filepath}"

    logger.debug(f"Getting cell info from {cell_info_filepath}")
    try:
        cell_info = mtz_get_cell(cell_info_filepath)
    except Exception:
        logger.error(f"Could not get cell information from {cell_info_filepath}")
        raise

    logger.debug(f"Getting space group from {space_group_filepath}")
    try:
        if space_group_filepath.suffix == ".mtz":
            space_group = mtz_find_space_group(space_group_filepath)
        else:
            space_group = textfile_find_space_group(space_group_filepath)
    except Exception:
        logger.error(f"Could not get space info from {space_group_filepath}")
        raise

    logger.debug("Running phase to map conversion")
    try:
        # Check the phase file first
        phase_filepath_good = phase_remove_bad_values(
            phase_filepath,
            output_filepath.parent / (output_filepath.stem + "_temp.phs"),
        )
        # Log the result
        if phase_filepath is not phase_filepath_good:
            logger.info(
                f"Filtered bad values from phase filepath and stored results in {phase_filepath_good}"
            )

        # Run the conversion
        phase_to_map(
            phase_filepath_good, cell_info, space_group, xyz_limits, output_filepath
        )
    except Exception:
        logger.error("Could not convert phase file to map")
        raise

    logger.info("Conversion complete")

    return True
