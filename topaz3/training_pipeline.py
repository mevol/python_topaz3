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
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.models import Sequential
import keras
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


def get_pipeline_parameters() -> dict:
    """
    Extract the parameters from a mixture of config file and command line using configargparse

    :return parameters_dict: dictionary containing all parameters necessary for pipeline
    """

    logging.basicConfig(level=logging.INFO)

    # Set up parser to work with command line argument or yaml file
    parser = configargparse.ArgParser(
        config_file_parser_class=configargparse.YAMLConfigFileParser,
        description="Training pipeline for a Keras model which is parameterized from the command line "
        "or YAML config file.\n"
        "To perform image augmentation, please provide a dictionary in the config file entitled "
        "image_augmentation_dict with kay value pair matching the parameters listed here: https://keras.io/preprocessing/image/"
        " The images will automatically be rescaled.",
    )

    parser.add_argument(
        "-c",
        "--config",
        required=True,
        is_config_file=True,
        help="config file to specify the following parameters in",
    )
    parser.add_argument(
        "--training_dir", required=True, help="directory with training images in"
    )
    parser.add_argument(
        "--database_file",
        required=True,
        help="sqlite3 database with labels for training images",
    )
    parser.add_argument(
        "--output_dir",
        required=True,
        help="directory to output results files to. Will be appended with date and time of program run",
    )
    parser.add_argument(
        "--k_folds",
        required=True,
        type=int,
        help="number of folds to create for k-fold cross-validation",
    )
    parser.add_argument(
        "--runs",
        required=True,
        type=int,
        help="number of folds to run training and validation on. Must be equal or lower than k_folds",
    )
    parser.add_argument(
        "--epochs", type=int, required=True, help="number of epochs to use in each run"
    )
    parser.add_argument(
        "--batch_size",
        required=True,
        type=int,
        help="size of batch to load during training and validation. Should be exact factor of the number of images provided",
    )
    parser.add_argument(
        "--test_dir",
        help="directory with images for testing and producing classification reports. Leave empty if you do not want to perform evaluation",
    )
    parser.add_argument(
        "--slices_per_structure",
        type=int,
        help="number of images for each structure. To be used in testing only",
    )

    (known_args, unknown_args) = parser.parse_known_args()

    assert known_args.k_folds >= known_args.runs, (
        f"Number of runs must be less than or equal to k_folds, "
        f"got {known_args.runs} runs and {known_args.k_folds} folds"
    )

    argument_dict = vars(known_args)

    # Try to extract image_augmentation_dict
    try:
        assert unknown_args
        assert "--image_augmentation_dict" in unknown_args
        # Extract values from config file
        with open(known_args.config, "r") as f:
            image_augmentation_dict = yaml.load(f.read())["image_augmentation_dict"]
    except (KeyError, AssertionError):
        logging.warning(
            f"Could not find image_augmentation_dict in {known_args.config}, performing scaling only"
        )
        image_augmentation_dict = {}
    assert isinstance(
        image_augmentation_dict, dict
    ), f"image_augmentation_dict must be provided as a dictionary in YAML, got {image_augmentation_dict}"

    argument_dict["image_augmentation_dict"] = image_augmentation_dict

    return argument_dict


if __name__ == "__main__":

    args = get_pipeline_parameters()
    print(f"Received the following arguments: {args}")
