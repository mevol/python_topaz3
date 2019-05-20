"""Functions to get the correlation coefficients from lst files"""

import re
import logging

from pathlib import Path

def get_cc(filename):
    """Extract the cc from the file and return as a float"""
    logging.debug(f"Trying to extract CC from {filename}")
    try:
        filepath = Path(filename)
        assert filepath.exists()
    except Exception:
        logging.error(f"Could not find a file to read at {filename}")
        raise Exception(f"Could not find a file to read at {filename}")

    try:
        with open(filepath) as f:
            text = f.read()
            cc_string = re.findall("(?<=with CC)[ ]+[0-9]+.[0-9]+", text)
            cc = float(cc_string[0].replace(" ", ""))
    except Exception:
        logging.error(f"Could not find CC in {filepath}")

    return cc



if __name__ == '__main__':
    print(get_cc("/dls/mx-scratch/melanie/for_METRIX/results_20190326/EP_phasing/traced/3N6X/P41212/3N6X_i.lst"))