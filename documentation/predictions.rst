Predictions
-----------

Once you have a trained model, it can be used to generate predictions for new files.

Here, there are a series of tools which can be used to generate these predictions.

They are designed mostly to work from **.map** files, rather than directly from phase files.
This is because the variety of combinations for phase files, cell info files, space group files etc.
was judged to large to design a specific wrapper function.
Instead, please see :ref:`Conversions` for how to
generate **.map** before running these tools.

Command Line Tool
^^^^^^^^^^^^^^^^^

In many cases, both the original and inverse hands will be available and require predictions.
This is useful because if the model cannot give a confident prediction for one map, it can
provide a confident prediction for the other and the user can make their determination appropriately.

With this use case in mind, use *topaz3.predict_from_maps* to generate predictions and store them:

.. code-block::

    $ topaz3.predict_from_maps -h
    Using TensorFlow backend.
    usage: topaz3.predict_from_maps [-h] [-c CONFIG] --original_map_file
                                    ORIGINAL_MAP_FILE --inverse_map_file
                                    INVERSE_MAP_FILE --slices_per_axis
                                    SLICES_PER_AXIS --model_file MODEL_FILE
                                    --output_dir OUTPUT_DIR [--rgb]

    Generate predictions from original and inverse hand map files using the model
    provided. If an output directory is provided, the raw and average predictions
    will be saved there. Otherwise they will be printed to the terminal. Args that
    start with '--' (eg. --original_map_file) can also be set in a config file
    (specified via -c). The config file uses YAML syntax and must represent a YAML
    'mapping' (for details, see http://learn.getgrav.org/advanced/yaml). If an arg
    is specified in more than one place, then commandline values override config
    file values which override defaults.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            config file to specify the following options in
      --original_map_file ORIGINAL_MAP_FILE
                            map file of original hand
      --inverse_map_file INVERSE_MAP_FILE
                            map file of inverse hand
      --slices_per_axis SLICES_PER_AXIS
                            slices to be taken of map per axis for predictions
      --model_file MODEL_FILE
                            .h5 file to load model from
      --output_dir OUTPUT_DIR
                            directory to store results in
      --rgb                 include this option if using a model which expects 3d
                            images

As with many **Topaz3** tools, the tool can be run directly from the command line
or with a yaml config file.

Raw predictions (per image) are generated for the original and inverse maps, then
these predictions are averaged for each structure.
Both sets of predictions are recorded in json files in the specified output directory.

If the output directory is not specified, the results will be printed to the terminal.

**Example config file:**

.. code-block:: yaml

    original_map_file: /path/to/maps/original.map
    inverse_map_file: /path/to/maps/inverse.map
    slices_per_axis: 20
    model_file: /path/to/models/good_model.h5
    output_dir: /record/predictions/here

Underlying Prediction Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: topaz3.predictions.predict_original_inverse

.. autofunction:: topaz3.predictions.predictions_from_map

