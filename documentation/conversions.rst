Conversions
------------

Functions used during data preparation to convert phase information which is collected from experiments to maps
which can then be sliced into 2d images for training.

High Level Functions
^^^^^^^^^^^^^^^^^^^^
.. autofunction:: topaz3.conversions.files_to_map

.. autofunction:: topaz3.conversions.phase_to_map

.. autofunction:: topaz3.conversions.phase_remove_bad_values

Train Test Split Tool
~~~~~~~~~~~~~~~~~~~~~

This is a helpful tool to randomly select a number of files or subdirectories as test objects
and remove them from your main directory.

Get help with the command line interface by using:

.. code-block::

    topaz3.test_split -h
    # Example usage
    topaz3.test_split /path/to/training/files /keeep/test/files/here

.. autofunction:: topaz3.train_test_split.test_split_directory


Low Level Functions
^^^^^^^^^^^^^^^^^^^

The processing of the phase file is broken up into 3 sections:

* transforming the phase file to an mtz file
* transforming the mtz file to a map file
* transforming the map to a map which is equal in x, y, z dimensions

The api for these functions is listed below, please note that they all use the **Shell Scripts**.

.. autofunction:: topaz3.conversions.phs_to_mtz

.. autofunction:: topaz3.conversions.mtz_to_map

.. autofunction:: topaz3.conversions.map_to_map