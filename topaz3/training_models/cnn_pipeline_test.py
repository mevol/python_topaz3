"""Testing with training_pipeline"""

from typing import Tuple

import keras
from keras import Sequential
from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D

from topaz3.training_pipeline import pipeline_from_command_line


def create_model(input_shape: Tuple[int, int, int]):
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
        optimizer=keras.optimizers.adam(lr=1e-5),
        metrics=["accuracy"],
    )

    return model


if __name__ == "__main__":

    pipeline_from_command_line(create_model, rgb=False)
