"""Module containing useful functions for getting predictions on
images from a model and outputting the predictions in a useful format"""

import sys
import logging
import mrcfile
import json
import numpy as np
import keras.models
from topaz3.maps_to_images import slice_map
from pathlib import Path

IMG_DIM = (201, 201)


def predictions_from_images(image_stack: np.ndarray, model_file: str) -> np.ndarray:
    """Get predictions from a model on the image stack provided"""
    try:
        model = keras.models.load_model(model_file)
    except OSError:
        logging.exception(f"Could not find .h5 model at {model_file}")
        raise

    predictions = model.predict(image_stack)

    return predictions


def map_to_images(map_file: str, slices_per_axis: int, rgb: bool = False) -> np.ndarray:
    """Convert a map to an image stack and scale it properly"""
    logging.info(f"Extracting data from {map_file}")
    try:
        with mrcfile.open(map_file) as mrc:
            volume = mrc.data
    except ValueError:
        logging.exception(f"Expected a .map file, not {map}")
        raise
    except FileNotFoundError:
        logging.exception(f"No file found at {map_file}, please provide .map file path")
        raise
    except Exception:
        logging.exception(
            f"Could not get data from {map_file}, please provide .map file path"
        )
        raise

    # Get image slices
    logging.info(f"Slicing map into {slices_per_axis} images on each axis")
    image_stack = slice_map(volume, slices_per_axis)

    # Check dimensions are correct
    assert (
        image_stack.shape[1],
        image_stack.shape[2],
    ) == IMG_DIM, f"Expected image slices of {IMG_DIM}, not {(image_stack.shape[1], image_stack.shape[2])}"

    logging.info(f"Got {image_stack.shape[0]} slices for prediction")

    # Scale slices for input to neural network
    for slice_num in range(image_stack.shape[0]):
        # Get slice
        slice = image_stack[slice_num, :, :]
        # Scale slice
        slice = (slice - slice.min()) / (slice.max() - slice.min())

        # Return to image_stack (in place)
        image_stack[slice_num, :, :] = slice

    if rgb:
        # Turn into RGB image array
        image_stack_rgb = np.stack((image_stack,) * 3, axis=3)
        return image_stack_rgb
    else:
        # Add a 4th dimension for the benefit of keras and return
        return np.expand_dims(image_stack, 3)


def predictions_from_map(
    map_file: str, slices_per_axis: int, model_file: str
) -> np.ndarray:
    """Get the image slices from a map file and get their predictions"""
    image_stack = map_to_images(map_file, slices_per_axis)

    # Get predictions
    predictions = predictions_from_images(image_stack, model_file)

    return predictions


def predict_original_inverse(
    original_map_file: str,
    inverse_map_file: str,
    slices_per_axis: int,
    model_file: str,
    output_dir: str,
    raw_pred_filename: str = "raw_predictions.json",
    average_pred_filename: str = "avg_predictions.json",
    rgb: bool = False,
) -> np.ndarray:
    """Get predictions for the original and inverse files at the same time and output to json file"""
    logging.info("Getting predictions for original and inverse maps pair")
    logging.info(f"Original at: {original_map_file}")
    logging.info(f"Inverse at: {inverse_map_file}")

    # Get image stacks
    original_image_stack = map_to_images(original_map_file, slices_per_axis, rgb=rgb)
    inverse_image_stack = map_to_images(inverse_map_file, slices_per_axis, rgb=rgb)
    # Add image stacks together with original first, should have shape
    # of (6*slices_per_axis, 201, 201, 1) for easy input to neural network
    total_image_stack = np.concatenate(
        (original_image_stack, inverse_image_stack), axis=0
    )

    # Get predictions
    logging.info(f"Getting predictions from model at {model_file}")
    predictions = predictions_from_images(total_image_stack, model_file)

    # Record raw predictions
    assert Path(
        output_dir
    ).is_dir(), f"Could not find expected directory at {output_dir}"
    # Split the predictions in half to match the original and inverse pairs
    raw_predictions = {
        "Original": predictions[: int(len(predictions) / 2)].tolist(),
        "Inverse": predictions[int(len(predictions) / 2) :].tolist(),
    }
    try:
        with open(Path(output_dir) / raw_pred_filename, "w") as raw_pred_file:
            json.dump(raw_predictions, raw_pred_file, indent=4)
    except Exception:
        logging.exception(f"Could not write raw predictions to {raw_pred_file.name}")
        raise

    # Record the average predictions
    avg_predictions = {
        "Original": {
            0: np.mean([pred[0] for pred in raw_predictions["Original"]]),
            1: np.mean([pred[1] for pred in raw_predictions["Original"]]),
        },
        "Inverse": {
            0: np.mean([pred[0] for pred in raw_predictions["Inverse"]]),
            1: np.mean([pred[1] for pred in raw_predictions["Inverse"]]),
        },
    }
    try:
        with open(Path(output_dir) / average_pred_filename, "w") as avg_pred_file:
            json.dump(avg_predictions, avg_pred_file, indent=4)
    except Exception:
        logging.exception(
            f"Could not write average predictions to {avg_pred_file.name}"
        )
        raise

    return avg_predictions


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print(sys.argv)

    print(
        predict_original_inverse(
            sys.argv[1],
            sys.argv[2],
            int(sys.argv[3]),
            sys.argv[4],
            sys.argv[5],
            rgb=bool(sys.argv[6]),
        )
    )