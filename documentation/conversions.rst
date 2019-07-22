Conversions
------------

Functions used during data preparation to convert phase information which is collected from experiments to maps
which can then be sliced into 2d images for training.

High Level Functions
^^^^^^^^^^^^^^^^^^^^
.. autofunction:: topaz3.conversions.files_to_map

.. autofunction:: topaz3.conversions.phase_to_map

.. autofunction:: topaz3.conversions.phase_remove_bad_values


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