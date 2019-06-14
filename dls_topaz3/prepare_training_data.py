import logging
import argparse
import yaml

from pathlib import Path
from mtz_info import mtz_get_cell
from space_group import textfile_find_space_group, mtz_find_space_group
from conversions import phase_to_map
from delete_temp_files import delete_temp_files
from get_cc import get_cc
from database_ops import prepare_training_database, prepare_labels_database


def prepare_training_data(
    phase_directory,
    cell_info_directory,
    cell_info_path,
    space_group_directory,
    space_group_path,
    xyz_limits,
    database,
    output_directory,
    delete_temp=True,
):
    """Convert both the original and inverse hands of a structure into a regular map file based on information
    about the cell info and space group and the xyz dimensions. Return True if no exceptions"""

    logging.info("Preparing training data")

    # Check all directories exist
    try:
        phase_dir = Path(phase_directory)
        assert phase_dir.exists()
    except:
        logging.error(f"Could not find phase directory at {phase_directory}")
        raise

    try:
        cell_info_dir = Path(cell_info_directory)
        assert cell_info_dir.exists()
    except:
        logging.error(f"Could not find cell info directory at {cell_info_directory}")
        raise

    try:
        space_group_dir = Path(space_group_directory)
        assert space_group_dir.exists()
    except:
        logging.error(
            f"Could not find space group directory at {space_group_directory}"
        )
        raise

    try:
        database_path = Path(database)
        assert database_path.exists()
    except:
        logging.error(f"Could not find database at {database}")
        raise

    try:
        database_path = Path(database)
        assert database_path.exists()
    except:
        logging.error(f"Could not find database at {database}")
        raise

    try:
        output_dir = Path(output_directory)
        assert output_dir.exists()
    except:
        logging.error(f"Could not find output directory at {output_directory}")
        raise

    # Check xyz limits are of correct format
    try:
        assert type(xyz_limits) == list or type(xyz_limits) == tuple
        assert len(xyz_limits) == 3
        assert all(type(values) == int for values in xyz_limits)
    except AssertionError:
        logging.error(
            "xyz_limits muste be provided as a list or tupls of three integer values"
        )
        raise

    # Get lists of child directories
    phase_structs = [struct.stem for struct in phase_dir.iterdir()]
    cell_info_structs = [struct.stem for struct in cell_info_dir.iterdir()]
    space_group_structs = [struct.stem for struct in space_group_dir.iterdir()]

    assert (
        phase_structs == cell_info_structs == space_group_structs
    ), "Same structures not found in all given directories"
    phase_structs = sorted(phase_structs)
    logging.debug(f"Following structures found to transform: {phase_structs}")

    # Get cell info and space group
    cell_info_dict = {}
    space_group_dict = {}

    # Set up function to get space group depending on suffix
    if Path(space_group_path).suffix == ".mtz":
        find_space_group = mtz_find_space_group
    else:
        find_space_group = textfile_find_space_group

    for struct in phase_structs:
        logging.info(
            f"Collecting info from {struct}, {phase_structs.index(struct)+1}/{len(phase_structs)}"
        )
        try:
            cell_info_file = cell_info_dir / Path(struct) / Path(cell_info_path)
            assert cell_info_file.exists()
        except:
            logging.error(f"Could not find cell info file at {cell_info_dir}")
            raise

        try:
            cell_info_dict[struct] = mtz_get_cell(cell_info_file)
        except:
            logging.error(f"Could not get cell info from {cell_info_file}")
            raise

        try:
            space_group_file = space_group_dir / Path(struct) / Path(space_group_path)
            assert space_group_file.exists()
        except:
            logging.error(f"Could not find space group file at {space_group_dir}")
            raise

        try:
            space_group_dict[struct] = find_space_group(space_group_file)
        except:
            logging.error(f"Could not get space group from {space_group_file}")
            raise

    logging.info("Collected cell info and space group")

    # Begin transformation
    for struct in phase_structs:
        logging.info(
            f"Converting {struct}, {phase_structs.index(struct)+1}/{len(phase_structs)}"
        )
        # Create original and inverse hands
        try:
            original_hand = Path(
                phase_dir / struct / space_group_dict[struct] / (struct + ".phs")
            )
            inverse_hand = Path(
                phase_dir / struct / space_group_dict[struct] / (struct + "_i.phs")
            )

            # Catch a weird situation where some space groups RXX can also be called RXX:H
            if (space_group_dict[struct][0] == "R") and (
                original_hand.exists() == False
            ):
                original_hand = Path(
                    phase_dir
                    / struct
                    / (space_group_dict[struct] + ":H")
                    / (struct + ".phs")
                )
                inverse_hand = Path(
                    phase_dir
                    / struct
                    / (space_group_dict[struct] + ":H")
                    / (struct + "_i.phs")
                )

            assert original_hand.exists(), f"Could not find original hand for {struct}"
            assert inverse_hand.exists(), f"Could not find inverse hand for {struct}"
        except:
            logging.error(
                f"Could not find phase files of {struct} in space group {space_group_dict[struct]}"
            )
            raise

        # Convert original
        try:
            phase_to_map(
                original_hand,
                cell_info_dict[struct],
                space_group_dict[struct],
                xyz_limits,
                output_dir / (struct + ".map"),
            )
        except:
            logging.error(f"Could not convert original hand for {struct}")
            raise

        # Convert inverse
        try:
            phase_to_map(
                inverse_hand,
                cell_info_dict[struct],
                space_group_dict[struct],
                xyz_limits,
                output_dir / (struct + "_i.map"),
            )
        except:
            logging.error(f"Could not convert original hand for {struct}")
            raise

        logging.info(f"Successfully converted {struct}")

    logging.info("Finished conversions")

    # Build up database - collect all cc information first then put it into database
    logging.info("Collecting CC information")

    # Dictionary of correlation coefficients
    cc_original_dict = {}
    cc_inverse_dict = {}

    for struct in phase_structs:
        # Create original and inverse hands
        try:
            original_hand = Path(
                phase_dir / struct / space_group_dict[struct] / (struct + ".lst")
            )
            inverse_hand = Path(
                phase_dir / struct / space_group_dict[struct] / (struct + "_i.lst")
            )

            # Catch a weird situation where some space groups RXX can also be called RXX:H
            if (space_group_dict[struct][0] == "R") and (
                original_hand.exists() == False
            ):
                original_hand = Path(
                    phase_dir
                    / struct
                    / (space_group_dict[struct] + ":H")
                    / (struct + ".lst")
                )
                inverse_hand = Path(
                    phase_dir
                    / struct
                    / (space_group_dict[struct] + ":H")
                    / (struct + "_i.lst")
                )

            assert original_hand.exists(), f"Could not find original hand for {struct}"
            assert inverse_hand.exists(), f"Could not find inverse hand for {struct}"
        except:
            logging.error(
                f"Could not find lst files of {struct} in space group {space_group_dict[struct]}"
            )
            raise

        try:
            cc_original_dict[struct] = get_cc(original_hand)
            cc_inverse_dict[struct] = get_cc(inverse_hand)
        except:
            logging.error(
                f"Could not get CC info of {struct} in space group {space_group_dict[struct]}"
            )

    # Generate list of results
    cc_results = []
    for struct in phase_structs:
        cc_results.append(
            (
                struct,
                cc_original_dict[struct],
                cc_inverse_dict[struct],
                (cc_original_dict[struct] > cc_inverse_dict[struct]),
                (cc_original_dict[struct] < cc_inverse_dict[struct]),
            )
        )

    # Put in database
    prepare_training_database(str(database_path), cc_results)
    prepare_labels_database(str(database_path))

    # Delete temporary files if requested
    if delete_temp == True:
        delete_temp_files(output_directory)
        logging.info("Deleted temporary files in output directory")

    return True


def params_from_yaml(args):
    """Extract the parameters for prepare_training_data from a yaml file and return a dict"""
    # Check the path exists
    try:
        config_file_path = Path(args.config_file)
        assert config_file_path.exists()
    except Exception:
        logging.error(f"Could not find config file at {args.config_file}")
        raise

    # Load the data from the config file
    try:
        with open(config_file_path, "r") as f:
            params = yaml.safe_load(f)
    except:
        logging.error(
            f"Could not extract parameters from yaml file at {config_file_path}"
        )

    if "delete_temp" not in params.keys():
        params["delete_temp"] = True

    return params


def params_from_cmd(args):
    """Extract the parameters for prepare_training_data from the command line and return a dict"""
    params = {
        "phase_dir": args.phase_dir,
        "cell_info_dir": args.cell_info_dir,
        "cell_info_path": args.cell_info_path,
        "space_group_dir": args.space_group_dir,
        "space_group_path": args.space_group_path,
        "xyz_limits": args.xyz,
        "db_path": args.db,
        "output_dir": args.output_dir,
        "delete_temp": True,
    }
    if args.keep_temp:
        params["delete_temp"] = False

    return params


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(name="debug_log")
    userlog = logging.getLogger(name="usermessages")

    # Parser for command line interface
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    yaml_parser = subparsers.add_parser("yaml")
    yaml_parser.add_argument(
        "config_file",
        type=str,
        help="yaml file with configuration information for this program",
    )
    yaml_parser.set_defaults(func=params_from_yaml)

    cmd_parser = subparsers.add_parser("cmd")
    cmd_parser.add_argument(
        "phase_dir", type=str, help="top level directory for phase information"
    )
    cmd_parser.add_argument(
        "cell_info_dir", type=str, help="top level directory for cell info"
    )
    cmd_parser.add_argument(
        "cell_info_path", type=str, help="cell info file within each structure folder"
    )
    cmd_parser.add_argument(
        "space_group_dir", type=str, help="top level directory for space group"
    )
    cmd_parser.add_argument(
        "space_group_path",
        type=str,
        help="space group file within each structure folder",
    )
    cmd_parser.add_argument(
        "xyz", type=int, nargs=3, help="xyz size of the output map file"
    )
    cmd_parser.add_argument(
        "db",
        type=str,
        help="location of the sqlite3 database to store training information",
    )
    cmd_parser.add_argument(
        "output_dir", type=str, help="directory to output all map files to"
    )
    cmd_parser.add_argument(
        "--keep_temp",
        action="store_false",
        help="keep the temporary files after processing",
    )
    cmd_parser.set_defaults(func=params_from_cmd)

    # Extract the parameters based on the yaml/command line argument
    args = parser.parse_args()
    parameters = args.func(args)

    print(parameters)

    # Execute the command
    try:
        prepare_training_data(
            parameters["phase_dir"],
            parameters["cell_info_dir"],
            parameters["cell_info_path"],
            parameters["space_group_dir"],
            parameters["space_group_path"],
            parameters["xyz_limits"],
            parameters["db_path"],
            parameters["output_dir"],
            parameters["delete_temp"],
        )
    except KeyError as e:
        logging.error(f"Could not find parameter {e} to prepare training data")
