"""This file contains the main script for converting phase information
into a regularly sized electron density map using tools from CCP4"""

import procrunner
import os
import logging
import logconfig

from pathlib import Path
from mtz_info import mtz_get_cell
from space_group import textfile_find_space_group, mtz_find_space_group

log = logging.getLogger(name="debug_log")
userlog = logging.getLogger(name="usermessages")


def phs_to_mtz(phase_filename, cell_info, space_group, output_filename):
    """Use the CCP4 f2mtz utility to convert a phase file into a .mtz file
     and return the new file location."""
    try:
        phase_filepath = Path(phase_filename)
        output_filepath = Path(output_filename)
    except Exception:
        raise Exception("Inputs must be paths of input phase file and output mtz file.")

    userlog.debug(f"Converting phase to mtz")
    log.debug(f"Input file at {phase_filepath}")
    log.debug(f"Output file at {output_filepath}")

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

    log.debug(f"Keywords: {keywords}")

    # Convert to bytes
    b_keywords = bytes(keywords, "utf-8")

    # Get location of shell script
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    cfft_shell = os.path.join(__location__, "shell_scripts/f2mtz.sh")

    # Build up command list
    command = [cfft_shell, "hklin", phase_filepath, "hklout", output_filepath]

    log.debug(f"Command: {command}")

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
        result["timeout"] == False
    ), f"Error collecting information from {phase_filepath} to {output_filepath}"

    userlog.debug("Conversion successful")

    return output_filepath


def mtz_to_map(mtz_filename, output_filename):
    """Convert .mtz file to map using cfft utility and return the new output file location."""

    try:
        mtz_filepath = Path(mtz_filename)
        output_filepath = Path(output_filename)
    except Exception:
        raise Exception("Inputs must be paths of input mtz file and output map file.")

    userlog.debug(f"Converting mtz to map")
    log.debug(f"Input file at {mtz_filepath}")
    log.debug(f"Output file at {output_filepath}")

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

    log.debug(f"Keywords: {keywords}")

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
        result["timeout"] == False
    ), f"Error collecting information from {mtz_filepath} to {output_filepath}"

    userlog.debug("Conversion successful")

    return output_filepath


def map_to_map(map_filename, xyz_limits, space_group, output_filename):
    """Converts a map file to a map file with specific xyz dimensions and returns the output file location"""

    try:
        map_filepath = Path(map_filename)
        output_filepath = Path(output_filename)
    except Exception:
        raise Exception("Inputs must be paths of input map file and output map file.")

    userlog.debug(f"Converting map to map")
    log.debug(f"Input file at {map_filepath}")
    log.debug(f"Output file at {output_filepath}")

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

    log.debug(f"Keywords: {keywords}")

    # Convert to bytes
    b_keywords = bytes(keywords, "utf-8")

    # Get location of shell script
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    cfft_shell = os.path.join(__location__, "shell_scripts/mapmask.sh")

    # Build up command list
    command = [cfft_shell, "mapin", map_filepath, "mapout", output_filepath]

    log.debug(f"Command: {command}")

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
        result["timeout"] == False
    ), f"Error collecting information from {map_filepath} to {output_filepath}"

    userlog.debug("Conversion successful")

    return output_filepath


def phase_to_map(phase_filename, cell_info, space_group, xyz_limits, output_filename):
    """Convert a phase file to a regularised map file with dimensions x, y, z"""

    try:
        phase_filepath = Path(phase_filename)
        output_filepath = Path(output_filename)
    except Exception:
        raise Exception("Inputs must be paths of input phase file and output map file.")

    assert (
        output_filepath.parent.exists()
    ), f"Could not find directory for output file, expected at {output_filepath.parent}"

    userlog.debug(f"Beginning phase to map conversion")
    log.debug(f"Input: {phase_filepath}")
    log.debug(f"Output: {output_filepath}")

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

    userlog.debug(f"Map successfully generated at {output_filepath}")

    return True


def files_to_map(
    phase_filename,
    cell_info_filename,
    space_group_filename,
    xyz_limits,
    output_filename,
):
    """Extract information from files before running the phase to map conversion"""

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

    log.info(f"Getting cell info from {cell_info_filepath}")
    try:
        cell_info = mtz_get_cell(cell_info_filepath)
    except Exception:
        log.error(f"Could not get cell information from {cell_info_filepath}")
        raise

    log.info(f"Getting space group from {space_group_filepath}")
    try:
        if space_group_filepath.suffix == ".mtz":
            space_group = mtz_find_space_group(space_group_filepath)
        else:
            space_group = textfile_find_space_group(space_group_filepath)
    except Exception:
        log.error(f"Could not get space info from {space_group_filepath}")
        raise

    log.info("Running phase to map conversion")
    try:
        phase_to_map(
            phase_filepath, cell_info, space_group, xyz_limits, output_filepath
        )
    except Exception:
        log.error("Could not convert phase file to map")
        raise

    userlog.info("Conversion complete")

    return True


if __name__ == "__main__":
    # Set up initial logging things
    userlog = logging.getLogger(name="usermessages")
    log = logging.getLogger(name="debug_log")
    logconfig.setup_logging()

    userlog.info("Beginning test run of Files to Map conversion")

    files_to_map(
        "/dls/science/users/riw56156/topaz_test_data/python_test/4PUC_i.phs",
        "/dls/science/users/riw56156/topaz_test_data/AUTOMATIC_DEFAULT_free.mtz",
        "/dls/science/users/riw56156/topaz_test_data/simple_xia2_to_shelxcde.log",
        [200, 200, 200],
        "/dls/science/users/riw56156/topaz_test_data/python_test/file_to_map/output.map",
    )

    """
    #Setting up file path names
    phase_filepath = Path('/dls/science/users/riw56156/topaz_test_data/python_test/4PUC_str_i.phs')
    mtz_filepath = phase_filepath.parent / (phase_filepath.stem + '_temp.mtz')
    map_filepath = phase_filepath.parent / (phase_filepath.stem + '_temp.map')
    output_filepath = phase_filepath.with_suffix('.map')

    phase_to_map('/dls/science/users/riw56156/topaz_test_data/python_test/4PUC_i.phs',
                 '/dls/science/users/riw56156/topaz_test_data/python_test/phase_to_map/output.map',
                 [66.45, 112.123, 149.896, 90, 90, 90],
                 "P212121",
                 [200, 200, 200])
    """
