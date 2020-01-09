"""
Pipeline for training models with cross validation, recording parameters and performing evaluation.

Designed to make it easier to create and evaluate models with different architectures with the
same training parameters.
"""

# Necessary to make the run as consistent as possible
from numpy.random import seed

seed(1)
from tensorflow import set_random_seed
#from tensorflow.compat.v1 import set_random_seed
set_random_seed(2)

import logging
import sqlite3
import re
from pathlib import Path
import os
import shutil
from datetime import datetime
from typing import Callable

import mrcfile
import configargparse
import pandas
import yaml
from keras import Model
from keras.preprocessing.image import ImageDataGenerator

from topaz3.training_models.plot_history import history_to_csv
from topaz3.training_models.k_fold_boundaries import k_fold_boundaries
from topaz3.evaluate_model import evaluate
from topaz3.training_models.data_generator import DataGenerator

MAP_DIM = (201, 201, 201)

logging.basicConfig(level=logging.INFO, filename="training.log", filemode="w")


def pipeline(create_model: Callable[[int, int, int, int], Model], parameters_dict: dict):
    """
    Execute the pipeline on the model provided.

    Reads all files in from the training directory path provided, gets their labels from the *ai_labels*
    table in the database provided.

    Sets up Keras ImageDataGenerator for training images with scaling and extra parameters provided,
    and for validation images with scaling only.

    Randomly mixes training data and creates k folds.

    Trains on different fold for a run for the number of runs requested.

    If test directory is provided, evaluates against test data and records that in evaluation folder.

    Records in output directory the history and saves model for each run.

    Parameters in **parameters_dict**:

    - *training_dir* (required) - directory with training images
    - *database_file* (required) - path to database with ai_labels table to get labels from
    - *output_dir* (required) - directory to output files to (this name will be appended with date and time when the training was started)
    - *k_folds* (required) - how many folds to create
    - *runs* (required) - how many training runs to perform
    - *epochs* (required) - how many epochs to use in each run
    - *batch_size* (required) - size of batch when loading files during training (usually exact multiple of number of files)
    - *test_dir* - directory with testing images
    - *rgb* - whether the model is expecting a 3 channel image
    - image_augmentation_dict - dictionary of key-value pairs to pass as parameters to the Keras ImageGenerator for training images

    :param create_model: function which returns new Keras model to train and evaluate
    :param parameters_dict: dictionary of parameters for use in pipeline
    """

    # Create an output directory if it doesn't exist
    output_dir_path = Path(
        parameters_dict["output_dir"] + "_" + datetime.now().strftime("%Y%m%d_%H%M")
    )
    histories_path = output_dir_path / "histories"
    models_path = output_dir_path / "models"
    evaluations_path = output_dir_path / "evaluations"

    if not output_dir_path.exists():
        # Make one
        try:
            # Make directories
            os.mkdir(output_dir_path)
            os.mkdir(histories_path)
            os.mkdir(models_path)
            os.mkdir(evaluations_path)
            logging.info(f"Created output directories at {output_dir_path}")
        except Exception:
            logging.exception(
                f"Could not create directory at {output_dir_path}.\n"
                f"Please check permissions and location."
            )
            raise

    # Log parameters
    logging.info(f"Running with parameters: {parameters_dict}")

    # Log the key information about the model and run
    with open(output_dir_path / "parameters.yaml", "w") as f:
        yaml.dump(parameters_dict, f)

    # Load training files
    training_dir_path = Path(parameters_dict["training_dir"])
    assert (
        training_dir_path.exists()
    ), f"Could not find directory at {training_dir_path}"
    train_files = [str(file) for file in training_dir_path.iterdir()]
    assert len(train_files) > 0, f"Found no files in {training_dir_path}"
    logging.info(f"Found {len(train_files)} files for training")

    # Load test files
    test_dir_path = Path(parameters_dict["test_dir"])
    assert (
        test_dir_path.exists()
    ), f"Could not find directory at {test_dir_path}"
    test_files = [str(file) for file in test_dir_path.iterdir()]
    assert len(test_files) > 0, f"Found no files in {test_dir_path}"
    logging.info(f"Found {len(test_files)} files for test")


    # Initiate connection to the database
    try:
        conn = sqlite3.connect(parameters_dict["database_file"])
    except Exception:
        logging.error(
            f"Could not connect to database at {parameters_dict['database_file']}"
        )
        raise

    # Read table into pandas dataframe
    data = pandas.read_sql(f"SELECT * FROM ai_labels", conn)
    data_indexed = data.set_index("Name")

    # Strip the image number from the filename
    names = [re.findall("(.*)", Path(file).stem)[0] for file in train_files]
    train_labels = [data_indexed.at[name, "Label"] for name in names]

    names = [re.findall("(.*)", Path(file).stem)[0] for file in test_files]
    test_labels = [data_indexed.at[name, "Label"] for name in names]

#    print(train_files)
#    print(test_files)


#    # Prepare data generators to get data out
#    # Always rescale and also expand dictionary provided as parameter
#    train_datagen = ImageDataGenerator(
#        rescale=1.0 / 255, **parameters_dict["image_augmentation_dict"]
#    )
#    # Only rescale validation
#    validation_datagen = ImageDataGenerator(rescale=1.0 / 255)

    # Build model
    if parameters_dict["rgb"] is True:
        logging.info("Using 3 channel image input to model")
        input_shape = (201, 201, 201, 3) #3D
        color_mode = "rgb"
    else:
        logging.info("Using single channel image input to model")
        input_shape = (201, 201, 201, 1) #3D
        color_mode = "grayscale"

    # Create training dataframe
    training_dataframe = pandas.DataFrame(
        {"Files": train_files, "Labels": [str(label) for label in train_labels]}
    )

    # Create training dataframe
    testing_dataframe = pandas.DataFrame(
        {"Files": test_files, "Labels": [str(label) for label in test_labels]}
    )

#    print(training_dataframe.head())
#    print(testing_dataframe.head())

    training_dict = training_dataframe.to_dict()
    testing_dict = testing_dataframe.to_dict()
    
#    print(training_dict)
#    print(testing_dict)

    # Model run parameters
    epochs = parameters_dict["epochs"]
    batch_size = parameters_dict["batch_size"]

    # New model
    model = create_model(input_shape)
    model_info = model.get_config()

    training_generator = DataGenerator(#training_dict,
                                       training_dict['Files'],
                                       training_dict['Labels'],
                                       dim=MAP_DIM,
                                       batch_size=batch_size,
                                       n_classes=2,
                                       #n_channels=1,
                                       shuffle=True)

    testing_generator = DataGenerator(testing_dict['Files'],
                                       testing_dict['Labels'],
                                      # testing_dict,
                                       dim=MAP_DIM,
                                       batch_size=batch_size,
                                       n_classes=2,
                                       #n_channels=1,
                                       shuffle=True)

    history = model.fit_generator(
        training_generator,
        steps_per_epoch=int((len(training_dict["Files"]) / batch_size)),
        epochs=epochs,
        validation_data=testing_generator,
        validation_steps=(len(testing_dict["Files"]) / batch_size),
        use_multiprocessing=True,
        workers=1)


#    # Create input data dict
#    partition = {'train' : train_files,
#                 'test' : test_files}
#    labels = {train_files : train_labels,
#              test_files : test_labels}

### NOTE: train and test data are being read; this is from separate directories
###       though; should combine into one dir, read all in, add the labels;
###       do this in a dataframe and then split the data frame????





#    # Create training dataframe
#    training_dataframe = pandas.DataFrame(
#        {"Files": train_files, "Labels": [str(label) for label in train_labels]}
#    )
#    
#    print(train_files)
#    print(training_dataframe.head())
#    
#    training_dataframe.set_index("Files")
#    training_data_shuffled = training_dataframe.sample(frac=1)
#
    # Train the model k-fold number of times on different folds and record the output
    # Model run parameters
    #k_folds = parameters_dict["k_folds"]
    #runs = parameters_dict["runs"]
#    epochs = parameters_dict["epochs"]
#    batch_size = parameters_dict["batch_size"]

#    fold_boundaries = k_fold_boundaries(train_files, k_folds)
#    for k in range(runs):
#        logging.info(f"Running cross validation set {k + 1}")

      # New model
#    model = create_model(input_shape)
#    model_info = model.get_config()
        
        

#        # Separate the active training and validations set based on the fold boundaries
#        active_training_set = pandas.concat(
#            [
#                training_data_shuffled[: fold_boundaries[k][0]],
#                training_data_shuffled[fold_boundaries[k][1] :],
#            ]
#        )
#        
#        #active_training_set_dict = dict(active_training_set_dict)
#        
#        active_validation_set = training_data_shuffled[
#            fold_boundaries[k][0] : fold_boundaries[k][1]
#        ]
#
#        logging.info(f"Active training set of {len(active_training_set['Files'])}")
#        logging.info(f"Active validation set of {len(active_validation_set['Files'])}")


### TO DO --> find a way create data batches that use the files listed in
###           active_training_set and active_validation_set
###           open the individual files in the batch with mrcfile to create a
###           numpy array which can directly go into training

    1/0
        # Create generators
        
#        print(active_training_set.info)
#        print(active_training_set.shape)
        
#        params = {'dim': (32,32,32),
#                  'batch_size': 64,
#                  'n_classes': 6,
#                  'n_channels': 1,
#                  'shuffle': True}



#        training_generator = DataGenerator(x = partition['train'],
#                                           y = labels,
#                                           dim=MAP_DIM,
#                                           batch_size=batch_size,
#                                           n_classes=2,
#                                           n_channels=1,
#                                           shuffle=True
#                                           **params)
                                           
                                           
#        train_input_fn = tf.estimator.inputs.numpy_input_fn(x = {"x": sourceArray},
#                                                            y = {"y": markedArray, "m": noMaskArray},
#                                                           #"w": weightArray},
#                                                            batch_size = 100,
#                                                            num_epochs = None,
#                                                            shuffle = True)
                                                            
#        validation_generator = DataGenerator(x = partition['validation'],
#                                             y = labels,
#                                             dim=MAP_DIM,
#                                             batch_size=batch_size,
#                                             n_classes=2,
#                                             n_channels=1,
#                                             shuffle=True
#                                             **params)

#        eval_input_fn = tf.estimator.inputs.numpy_input_fn(x={"x": sourceArray},
#                                                           y={"y": markedArray, "m": noMaskArray},
#                                                           num_epochs=5,
#                                                           shuffle=False)
        
#        for s in active_training_set:
#          print(s)

#          if s == "Files":
#            pass
#          else:
#            print(s)
#            with mrcfile.open(s) as mrc:
#              next(mrc)
#              volume = mrc.data

#          train_generator = train_datagen.flow_from_dataframe(
#            active_training_set,
            #volume,
#            x_col="Files",
#            y_col="Labels",
#            target_size=MAP_DIM,
#            color_mode=color_mode,
#            shuffle=True,
#            batch_size=batch_size,
#            class_mode="categorical",
#            )
#        for s in active_validation_set:
#          with mrcfile.open(s) as mrc:
#            next(mrc)
#            volume = mrc.data

#          val_generator = validation_datagen.flow_from_dataframe(
#            active_validation_set,
#            #volume,
#            x_col="Files",
#            y_col="Labels",
#            target_size=MAP_DIM,
#            color_mode=color_mode,
#            shuffle=True,
#            batch_size=batch_size,
#            class_mode="categorical",
#        )

    history = model.fit_generator(
        train_generator,
        steps_per_epoch=int((len(active_training_set["Files"]) / batch_size)),
        epochs=epochs,
        validation_data=val_generator,
        validation_steps=(len(active_validation_set["Files"]) / batch_size),
        use_multiprocessing=True,
        workers=8,
        )

    # Send history to csv
    history_to_csv(history, histories_path / f"history_{k}.csv")
    # Save model as h5
    model.save(str(models_path / f"model_{k}.h5"))

    # Make evaluation folder
    if parameters_dict["test_dir"]:
        logging.info("Performing evaluation of model")
        evaluation_dir_path = str(evaluations_path / f"evaluation_{k}")
        if not Path(evaluation_dir_path).exists():
            os.mkdir(evaluation_dir_path)
        evaluate(
            str(models_path / f"model_{k}.h5"),
            parameters_dict["test_dir"],
            parameters_dict["database_file"],
            evaluation_dir_path,
            rgb=parameters_dict["rgb"],
            )
    else:
        logging.info(
           "Requires test directory for evaluation. "
            "No evaluation performed"
            )

    # Load the model config information as a yaml file
    with open(output_dir_path / "model_info.yaml", "w") as f:
        yaml.dump(model_info, f)

    # Try to copy log file if it was created in training.log
    try:
        shutil.copy("training.log", output_dir_path)
    except FileExistsError:
        logging.warning("Could not find training.log to copy")
    except Exception:
        logging.warning("Could not copy training.log to output directory")


def pipeline_from_command_line(
    create_model: Callable[[int, int, int, int], Model], rgb: bool = False #3D
):
    """
    Run the training pipeline from the command line with config file

    Get parameters from the command line and pass them to training_pipeline in the parameter dict

    :param create_model: function which returns new Keras model to train and evaluate
    :param rgb: whether the model is expecting a 3 channel image
    """

    # Get from pipeline
    argument_dict = get_pipeline_parameters()

    # Add rgb parameter
    assert isinstance(
        rgb, bool
    ), f"Must provide bool for rgb, got {type(rgb)} of value {rgb}"
    argument_dict["rgb"] = rgb

    logging.info(f"Running model with parameters: {argument_dict}")

    # Send parameters to full pipeline
    pipeline(create_model, argument_dict)


def get_pipeline_parameters() -> dict:
    """
    Extract the parameters from a mixture of config file and command line using configargparse

    :return parameters_dict: dictionary containing all parameters necessary for pipeline
    """

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
#    parser.add_argument(
#        "--k_folds",
#        required=True,
#        type=int,
#        help="number of folds to create for k-fold cross-validation",
#    )
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

    (known_args, unknown_args) = parser.parse_known_args()

#    assert known_args.k_folds >= known_args.runs, (
#        f"Number of runs must be less than or equal to k_folds, "
#        f"got {known_args.runs} runs and {known_args.k_folds} folds"
#    )

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
