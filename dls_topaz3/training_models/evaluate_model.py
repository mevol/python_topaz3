"""Load a model and evaluate its performance against an unknown test set"""
import sys
import logging
import glob
import numpy as np
import sqlite3
import pandas
import re

# encode text category labels
from pathlib import Path
from keras.preprocessing.image import ImageDataGenerator
import keras.models
from sklearn.metrics import classification_report, confusion_matrix

IMG_DIM = (201, 201)


def evaluate(model_file: str, test_dir: str, database_file: str):
    # Load model
    try:
        model = keras.models.load_model(model_file)
    except Exception:
        logging.error(f"Failed to load model from {model_file}")
        raise

    logging.debug("Model loaded")

    # Get test files prepared
    # Load files
    train_files = glob.glob(f"{test_dir}/*")
    print(f"Found {len(train_files)} files for training")

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

    # Create training dataframe
    testing_dataframe = pandas.DataFrame({"Files": train_files, "Labels": train_labels})

    test_datagen = ImageDataGenerator(rescale=1.0 / 255)

    test_batch_size = 60

    test_generator = test_datagen.flow_from_dataframe(
        testing_dataframe,
        x_col="Files",
        y_col="Labels",
        target_size=IMG_DIM,
        class_mode=None,
        color_mode="grayscale",
        batch_size=test_batch_size,
        shuffle=False,
    )

    predictions = model.predict_generator(
        test_generator, steps=int(len(testing_dataframe["Files"]) / test_batch_size)
    )

    # Per image analysis
    predictions_1 = [x for x in predictions if x[1] > x[0]]
    predictions_0 = [x for x in predictions if x[1] < x[0]]
    print(f"Predicted good value {len(predictions_1)} times")
    print(f"Predicted bad value {len(predictions_0)} times")

    predictions_decoded = [int(pred[1] > pred[0]) for pred in predictions]

    print("Per image analysis:")
    print(classification_report(predictions_decoded, testing_dataframe["Labels"]))
    print(confusion_matrix(predictions_decoded, testing_dataframe["Labels"]))

    # Per structure analysis
    predictions_1 = predictions[0:60, 1]
    predictions_0 = predictions[0:60, 0]

    print(np.mean(predictions_0))
    print(np.mean(predictions_1))

    predictions_structure_avg = np.array(
        [
            (
                np.mean(predictions[60 * i : 60 * i + 60, 0]),
                np.mean(predictions[60 * i : 60 * i + 60, 1]),
            )
            for i in range(int(len(predictions) / 60))
        ]
    )

    predictions_by_result = np.array(
        [(int(pred[0] > pred[1]), int(pred[1] > pred[0])) for pred in predictions]
    )
    predictions_structure_count = np.array(
        [
            (
                np.sum(predictions_by_result[60 * i : 60 * i + 60, 0]) / 60,
                np.sum(predictions_by_result[60 * i : 60 * i + 60, 1]) / 60,
            )
            for i in range(int(len(predictions) / 60))
        ]
    )

    predictions_struct_avg_flat = [
        int(pred > 0.5) for pred in predictions_structure_avg[:, 1]
    ]
    predictions_struct_count_flat = [
        int(pred > 0.5) for pred in predictions_structure_count[:, 1]
    ]

    labels = testing_dataframe["Labels"]
    testing_info_by_structure = [labels[60 * i] for i in range(int(len(labels) / 60))]

    print("Classification by structure using average:")
    print(classification_report(predictions_struct_avg_flat, testing_info_by_structure))
    print(confusion_matrix(predictions_struct_avg_flat, testing_info_by_structure))

    print("Classification by structure using count:")
    print(
        classification_report(predictions_struct_count_flat, testing_info_by_structure)
    )
    print(confusion_matrix(predictions_struct_count_flat, testing_info_by_structure))

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    evaluate(sys.argv[1], sys.argv[2], sys.argv[3])
