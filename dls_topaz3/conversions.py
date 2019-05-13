"""This file contains the main script for converting phase information into a regularly sized electron density
 map using tools from CCP4"""

import procrunner
import os
import logging

from pathlib import Path

def phs_to_mtz():
    """Use the CCP4 f2mtz utility to convert files"""

    result = procrunner.run(['f2mtz', "hklin", "/dls/mx-scratch/melanie/for_METRIX/results_20190326/AI_training/topaz_test/EP_phasing/traced/4PUC/P212121/4PUC.phs", "hklout", "test_mtz_python.mtz"], stdin="CELL 66.45 112.123 149.896 90 90 90\nSYMM 19\nlabout H K L F FOM PHI SGF\nCTYPOUT H H H F W P Q\n", print_stdout=False, print_stderr=False)

def mtz_to_map(mtz_filename, output_filename):
    """Convert .mtz file to map using cfft utility"""

    try:
        mtz_filepath = Path(mtz_filename)
        output_filepath = Path(output_filename)
    except:
        raise Exception("Inputs must be paths of input mtz file and output map file.")

    logging.info(f"Converting mtz to map")
    logging.info(f"Input file at {mtz_filepath}")
    logging.info(f"Output file at {output_filepath}")

    # Check parameters coming in
    assert mtz_filepath.suffix == ".mtz", "Please provide an mtz_filename which points to the .mtz file you wish to convert"
    assert mtz_filepath.exists(), f"Could not find a valid file at {mtz_filepath}"
    assert output_filepath.suffix == ".map", "Please provide an output_filename with a .map extension"
    assert output_filepath.parent.exists(), f"Could not find output directory at {output_filepath.parent}"

    # Build up standard input for cfft utility
    keywords = "\n".join([
        f"mtzin {mtz_filename}",
        "colin-fc /*/*/[F,PHI]",
        f"mapout {output_filename}",
        "stats",
        "stats-radius 4.0"
    ])

    b_keywords = bytes(keywords, "utf-8")

    logging.info(f"Keywords: {keywords}")

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

    mtz_to_map('/dls/science/users/riw56156/topaz_test_data/python_test/4PUC.mtz',
               '/dls/science/users/riw56156/topaz_test_data/python_test/4PUC.map')