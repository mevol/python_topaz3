Training & Evaluation
---------------------

Training the AI is a very important step in creating something useful from the data.

It can also be very challenging, require lots of compute time/energy and just when it looks
like everything is coming together, the accuracy drops at the last second and the model
doesn't look much better than it did several days or weeks ago.

Therefore, it is important to establish good metrics and practices.

**Topaz3** provides a training pipeline which performs
`k-fold cross-validation <https://machinelearningmastery.com/k-fold-cross-validation/>`_
and records the input parameters, model architecture, training histories and results and
stores copies of the finished models.

This allows you to concentrate on defining the best model without having to worry about
boilerplate code to properly record the results.

Example
^^^^^^^

Here is the code for a simple neural network (which turned out to be quite effective) being trained through the
training pipeline:

.. code-block:: python

    # https://github.com/DiamondLightSource/python-topaz3/blob/master/topaz3/training_models/example_cnn_basic.py
    from typing import Tuple

    from keras import Sequential, optimizers
    from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D

    from topaz3.training_models.training_pipeline import pipeline_from_command_line


    def create_basic_cnn_model(input_shape: Tuple[int, int, int]):
        """Define the basic cnn model"""

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
            optimizer=optimizers.adam(lr=1e-5),
            metrics=["accuracy"],
        )

        return model


    if __name__ == "__main__":

        pipeline_from_command_line(create_basic_cnn_model, rgb=False)

As you can see, the function *create_basic_cnn_model* returns a `Keras <https://www.keras.io/>`_ model which can
be defined as any other model, with an input parameter of the expected input shape as a 3-dimensional array.

This function is then passed to the *pipeline_from_command_line* function along with whether the model
is designed to use a 3-channel RGB input or a single channel grayscale input.

See the following examples:

- `Example Basic CNN <https://github.com/DiamondLightSource/python-topaz3/blob/master/topaz3/training_models/example_cnn_basic.py>`_
- `Example Pretrained CNN <https://github.com/DiamondLightSource/python-topaz3/blob/master/topaz3/training_models/example_pretrain_basic.py>`_

Underlying Training Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: topaz3.training_models.training_pipeline.pipeline

.. autofunction:: topaz3.training_models.training_pipeline.pipeline_from_command_line

.. autofunction:: topaz3.training_models.training_pipeline.get_pipeline_parameters