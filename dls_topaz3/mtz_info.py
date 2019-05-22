"""Functions for extracting information from an mtz file"""

import os
import procrunner
import re
import argparse


def mtz_get_xdata(mtz_filename):
    """Get the xdata out of an mtz file"""

    # Get location of shell script
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    mtzinfo_shell = os.path.join(__location__, "shell_scripts/mtzinfo.sh")

    # Run script and get the standard output or raise an exception
    result = procrunner.run(
        [mtzinfo_shell, mtz_filename], print_stdout=False, timeout=5
    )

    # Check that it worked
    assert result["exitcode"] == 0, f"Error collecting information from {mtz_filename}"
    assert result["stderr"] == b"", f"Error collecting information from {mtz_filename}"
    assert (
        result["timeout"] == False
    ), f"Error collecting information from {mtz_filename}"

    # print(result)

    output = str(result["stdout"])
    # print(f"Output: {output}")

    search_regex = re.compile("(?<=XDATA)[ a-z0-9.]+")
    xdata = search_regex.findall(output)
    # print(xdata)

    if len(xdata) > 1:
        print(
            f"{len(xdata):d} lines of xdata found in {mtz_filename}, using first occurence"
        )

    list_num = xdata[0].split()
    numbers = [float(num) for num in list_num]
    # print(numbers)

    return tuple(numbers)


def mtz_get_cell(mtz_filename):
    """Gets the cell information out of the xdata from the mtz file"""

    xdata = mtz_get_xdata(mtz_filename)

    return xdata[0:6]


def mtz_get_group(mtz_filename):
    """Get the group information out of the xdata from the mtz file"""

    xdata = mtz_get_xdata(mtz_filename)

    try:
        group = int(xdata[-2])
    except:
        raise Exception("Could not extract group number from xdata")

    try:
        assert group == xdata[-2]
    except:
        # print("Exception")
        raise Exception(f"Expected integer group number, got {group} from {xdata[-2]}")

    return int(group)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Get an MTZ file from the command line input."
    )

    parser.add_argument(
        "--test_file", help="Use this option to use a test file.", action="store_true"
    )

    parser.add_argument(
        "mtz_filename",
        type=str,
        metavar="mtz_filename",
        help="MTZ file to get information from",
    )

    args = parser.parse_args()

    # If testing, use test file
    if args.test_file:
        print("Testing")
        mtz_filename = (
            "/dls/science/users/riw56156/topaz_test_data/AUTOMATIC_DEFAULT_free.mtz"
        )
    else:
        mtz_filename = args.mtz_filename

    print(f"Collecting information from {mtz_filename}")

    cell_info = mtz_get_cell(mtz_filename)
    group_info = mtz_get_group(mtz_filename)

    print(f"MTZ Cell Info: {cell_info}")
    print(f"MTZ Group: {group_info}")
