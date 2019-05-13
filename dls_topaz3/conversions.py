"""This file contains the main script for converting phase information into a regularly sized electron density
 map using tools from CCP4"""

import procrunner
import os
import logging

from pathlib import Path

def phs_to_mtz(phase_filename, output_filename, cell_info, symmetry_group):
    """Use the CCP4 f2mtz utility to convert a phase file into a .mtz file and return the new file location."""
    try:
        phase_filepath = Path(phase_filename)
        output_filepath = Path(output_filename)
    except:
        raise Exception("Inputs must be paths of input phase file and output mtz file.")

    logging.info(f"Converting phase to mtz")
    logging.info(f"Input file at {phase_filepath}")
    logging.info(f"Output file at {output_filepath}")

    # Check parameters coming in
    assert phase_filepath.suffix == ".phs" or phase_filepath.suffix == ".pha", \
        "Please provide a phase_filename which points to the phase file you wish to convert."
    assert phase_filepath.exists(), f"Could not find a valid file at {phase_filepath}."
    assert output_filepath.suffix == ".mtz", "Please provide an output_filename with a .mtz extension."
    assert output_filepath.parent.exists(), f"Could not find output directory at {output_filepath.parent}"
    try:
        assert len(cell_info) == 6
        # Will raise error if values are not floats
        test_float = [float(value) for value in cell_info]
    except:
        raise Exception("Cell info must be list of 6 floating numbers for the cell lengths and angles.")
    assert type(symmetry_group) == int, "Please provide an integer symmetry group for the transformation."

    # Convert list of cells info into string
    cell_info_string = " ".join([str(cell) for cell in cell_info])

    # Build up keywords
    keywords = "\n".join([
        f"CELL {cell_info_string}",
        f"SYMM {symmetry_group}",
        "labout H K L F FOM PHI SIGF",
        "CTYPOUT H H H F W P Q"
    ])

    logging.info(f"Keywords: {keywords}")

    # Convert to bytes
    b_keywords = bytes(keywords, "utf-8")

    # Get location of shell script
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    cfft_shell = os.path.join(__location__, 'shell_scripts/f2mtz.sh')

    # Build up command list
    command = [cfft_shell, "hklin", phase_filepath, "hklout", output_filepath]

    logging.info(f"Command: {command}")

    result = procrunner.run(command, stdin=b_keywords)

    #Check that it worked
    assert result["exitcode"] == 0, f"Error converting {phase_filepath} to {output_filepath}"
    assert result["stderr"] == b"", f"Error collecting information from {phase_filepath} to {output_filepath}"

    logging.info("Conversion successful")

    return output_filepath

def mtz_to_map(mtz_filename, output_filename):
    """Convert .mtz file to map using cfft utility and return the new output file location."""

    try:
        mtz_filepath = Path(mtz_filename)
        output_filepath = Path(output_filename)
    except:
        raise Exception("Inputs must be paths of input mtz file and output map file.")

    logging.info(f"Converting mtz to map")
    logging.info(f"Input file at {mtz_filepath}")
    logging.info(f"Output file at {output_filepath}")

    # Check parameters coming in
    assert mtz_filepath.suffix == ".mtz",\
        "Please provide an mtz_filename which points to the .mtz file you wish to convert."
    assert mtz_filepath.exists(), f"Could not find a valid file at {mtz_filepath}"
    assert output_filepath.suffix == ".map", "Please provide an output_filename with a .map extension."
    assert output_filepath.parent.exists(), f"Could not find output directory at {output_filepath.parent}"

    # Build up standard input for cfft utility
    keywords = "\n".join([
        f"mtzin {mtz_filename}",
        "colin-fc /*/*/[F,PHI]",
        f"mapout {output_filename}",
        "stats",
        "stats-radius 4.0"
    ])

    logging.info(f"Keywords: {keywords}")

    # Convert to bytes
    b_keywords = bytes(keywords, "utf-8")

    # Get location of shell script
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    cfft_shell = os.path.join(__location__, 'shell_scripts/cfft.sh')

    result = procrunner.run([cfft_shell, '-stdin'], stdin=b_keywords)

    #Check that it worked
    assert result["exitcode"] == 0, f"Error converting {mtz_filepath} to {output_filepath}"
    assert result["stderr"] == b"", f"Error collecting information from {mtz_filepath} to {output_filepath}"

    logging.info("Conversion successful")

    return output_filepath

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    phs_to_mtz('/dls/science/users/riw56156/topaz_test_data/python_test/4PUC.phs',
               '/dls/science/users/riw56156/topaz_test_data/python_test/4PUC.mtz',
               [66.45, 112.123, 149.896, 90, 90, 90], 19)

    mtz_to_map('/dls/science/users/riw56156/topaz_test_data/python_test/4PUC.mtz',
               '/dls/science/users/riw56156/topaz_test_data/python_test/4PUC.map')