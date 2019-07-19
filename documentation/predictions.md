# Predictions

This page will document how to use the command line tools to perform prediction using trained models.

Predictions using a particular model for a map file (which has been regularized to the 201x201x201 size using the provided conversion methods) can be calculated with predictions.py

To get the predictions from a single map file:
```python
from topaz3.predictions import predictions_from_map
predictions_from_map(map_file="/path/to/my/structure.map",
                     slices_per_axis=20,
                     model_file="/path/to/trained/model.h5"
)
```
More often, it is useful to get and record the average predictions of an original/inverse hand pair.
For that case, use this function:
```python
from topaz3.predictions import predict_original_inverse
predict_original_inverse(original_map_file="/path/to/structure.map",
                         inverse_map_file="/path/to/structure_i.map",
                         slices_per_axis=20,
                         model_file="/path/to/trained/model.h5",
                         output_dir="/path/to/output/dir",
                         raw_pred_filename="raw_predictions.json",
                         average_pred_filename="average_predictions.json"
)
```
This will calculate the raw and average predictions for both the original and inverse map with the same model (speeding up the process), write the predictions to json files in the *output_dir* and return the averaged predictions.
In order to move from raw .phs and .mtz type files through to a prediction, pipeline the above function with *files_to_map* from **conversions.py**

This will generate the map files for you which can then both be handed to *predict_original_inverse*

A suitable way to do this would be to run the stages separately as part of a [**Zocalo**](https://github.com/DiamondLightSource/python-zocalo) recipe.