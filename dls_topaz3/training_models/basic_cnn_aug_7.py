"""
Implement a basic cnn with data augmentation on the data with cross validation
and softmax activation layer
Also implement the evaluation stage at the end of each model training step
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

from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.models import Sequential
import keras
import pandas
from plot_history import history_to_csv
from k_fold_boundaries import k_fold_boundaries
from dls_topaz3.evaluate_model import evaluate


IMG_DIM = (201, 201)


def create_model(input_shape):
    """Create and return a new cnn, assuring that the weights have been reinitialised"""
    model = Sequential()

    model.add(
        Conv2D(16, kernel_size=(3, 3), activation="relu", input_shape=input_shape)
    )
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, kernel_size=(3, 3), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(128, kernel_size=(3, 3), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(512, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(512, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(2, activation="softmax"))

    model.compile(
        loss="categorical_crossentropy",
        optimizer=keras.optimizers.adam(lr=5e-5),
        metrics=["accuracy"],
    )

    return model


def train(training_dir: str, database_file: str, test_dir: str, output_dir: str):
    # Load files
    training_dir_path = Path(training_dir)
    assert (
        training_dir_path.exists()
    ), f"Could not find directory at {training_dir_path}"
    train_files = [str(file) for file in training_dir_path.iterdir()]
    assert len(train_files) > 0, f"Found no files in {training_dir_path}"
    logging.info(f"Found {len(train_files)} files for training")

    # Initiate connection to the database
    try:
        conn = sqlite3.connect(database_file)
    except Exception:
        logging.error(f"Could not connect to database at {database_file}")
        raise

    # Read table into pandas dataframe
    data = pandas.read_sql(f"SELECT * FROM ai_labels", conn)
    data_indexed = data.set_index("Name")

    names = [re.findall("(.*)(?=_[0-9]+)", Path(file).stem)[0] for file in train_files]
    train_labels = [data_indexed.at[name, "Label"] for name in names]
    train_categories = [(label, int(not label)) for label in train_labels]

    logging.info(train_categories[1495:1505])

    # Prepare data generators to get data out
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        horizontal_flip=True,
        vertical_flip=True,
        shear_range=0.3,
        height_shift_range=0.2,
        width_shift_range=0.2,
        fill_mode="wrap",
    )
    validation_datagen = ImageDataGenerator(rescale=1.0 / 255)

    # Build model
    input_shape = (201, 201, 1)

    # Create training dataframe
    training_dataframe = pandas.DataFrame(
        {"Files": train_files, "Labels": [str(label) for label in train_labels]}
    )
    training_dataframe.set_index("Files")
    training_data_shuffled = training_dataframe.sample(frac=1)

    # Create an output directory if it doesn't exist
    output_dir_path = Path(output_dir + "_" + datetime.now().strftime("%Y%m%d_%H%M"))
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
        except Exception as e:
            logging.error(
                f"Could not create directory at {output_dir_path}.\n"
                f"Please check permissions and location."
            )
            logging.error(e)
            raise

    # Train the model k-fold number of times on different folds and record the output
    # Model run parameters
    k_folds = 5
    runs = 5
    epochs = 50
    batch_size = 50

    fold_boundaries = k_fold_boundaries(train_files, k_folds)
    for k in range(runs):
        logging.info(f"Running cross validation set {k+1}")

        # New model
        model = create_model(input_shape)

        # Separate the active training and validations set based on the fold boundaries
        active_training_set = pandas.concat(
            [
                training_data_shuffled[: fold_boundaries[k][0]],
                training_data_shuffled[fold_boundaries[k][1] :],
            ]
        )
        active_validation_set = training_data_shuffled[
            fold_boundaries[k][0] : fold_boundaries[k][1]
        ]

        logging.info(f"Active training set of {len(active_training_set['Files'])}")
        logging.info(f"Active validation set of {len(active_validation_set['Files'])}")

        # Create generators
        train_generator = train_datagen.flow_from_dataframe(
            active_training_set,
            x_col="Files",
            y_col="Labels",
            target_size=IMG_DIM,
            color_mode="grayscale",
            shuffle=True,
            batch_size=batch_size,
            class_mode="categorical",
        )

        val_generator = validation_datagen.flow_from_dataframe(
            active_validation_set,
            x_col="Files",
            y_col="Labels",
            target_size=IMG_DIM,
            color_mode="grayscale",
            shuffle=True,
            batch_size=batch_size,
            class_mode="categorical",
        )

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
        evaluation_dir_path = str(evaluations_path / f"evaluation_{k}")
        if not Path(evaluation_dir_path).exists():
            os.mkdir(evaluation_dir_path)
        evaluate(
            str(models_path / f"model_{k}.h5"),
            test_dir,
            database_file,
            evaluation_dir_path,
        )

    # Log the key information about the model and run
    key_info = {
        "Epochs": epochs,
        "Folds": k_folds,
        "Runs": runs,
        "Training files (Total)": len(train_files),
        "Model": model.get_config(),
    }
    with open(output_dir_path / "info.yaml", "w") as f:
        yaml.dump(key_info, f)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(f"{__file__}")
    train(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
