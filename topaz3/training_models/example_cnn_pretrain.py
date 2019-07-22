"""Testing with training_pipeline"""

import logging
from typing import Tuple

from keras import Sequential, optimizers
from keras.applications import vgg16
from keras.models import Model
from keras.layers import Dense, Dropout, Flatten

from topaz3.training_models.training_pipeline import pipeline_from_command_line


def create_pretrained_cnn_model(input_shape: Tuple[int, int, int]):
    """Create and return a new cnn, assuring that the weights have been reinitialised"""
    # Set up pretrained model with frozen weights
    vgg = vgg16.VGG16(include_top=False, weights="imagenet", input_shape=input_shape)

    output = vgg.layers[-1].output
    output = Flatten()(output)
    vgg_model = Model(vgg.input, output)

    logging.info(f"VGG Model Summary: {vgg_model.summary()}")

    # Build model
    model = Sequential()
    model.add(vgg_model)
    model.add(Dense(512, activation="relu", input_dim=input_shape))
    model.add(Dropout(0.3))
    model.add(Dense(512, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(2, activation="softmax"))

    model.compile(
        loss="categorical_crossentropy",
        optimizer=optimizers.adam(lr=1e-5),
        metrics=["accuracy"],
    )

    return model


if __name__ == "__main__":

    pipeline_from_command_line(create_pretrained_cnn_model, rgb=True)
