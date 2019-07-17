"""
Pipeline for training models with cross validation, recording parameters and performing evaluation.

Designed to make it easier to create and evaluate models with different architectures with the
same training parameters.
"""

# Necessary to make the run as consistent as possible
from numpy.random import seed

seed(1)
from tensorflow import set_random_seed

set_random_seed(2)

import logging
import sqlite3
import re
from pathlib import Path
import os
import sys
from datetime import datetime
import yaml

import configargparse
import pandas

from topaz3.training_models.plot_history import history_to_csv
from topaz3.training_models.k_fold_boundaries import k_fold_boundaries
from topaz3.evaluate_model import evaluate


def pipeline(model, rgb=False):
    """Execute the pipeline on the model provided.

    :param model: Keras model to train and evaluate
    :param rgb: set this to true only if the model you have provided is expecting an rgb image
    """

    pass


def get_pipeline_parameters():
    """
    Extract the parameters from a mixture of config file and command line using configargparse

    :return parameters_dict: dictionary containing all parameters necessary for pipeline
    """

    logging.basicConfig(level=logging.INFO)

    # Set up parser to work with command line argument or yaml file
    parser = configargparse.ArgParser(
        config_file_parser_class=configargparse.YAMLConfigFileParser
    )

    parser.add_argument(
        "-c",
        "--config",
        required=True,
        is_config_file=True,
        help="config file to specify the following options in",
    )
    parser.add_argument("--parameters", required=True, help="test parameters")

    (known_args, unknown_args) = parser.parse_known_args()

    print(known_args)
    print(unknown_args)

    with open(known_args.config, "r") as f:
        print(yaml.load(f.read()))


if __name__ == "__main__":
    get_pipeline_parameters()
