# Maps to Images

Now that you have generated all of your map files, it is necessary to slice them up into many images for training, validating and testing the machine learning model.

This is a relatively easy process, although it can take some time.

Run the process with this command:
```bash
python dls_topaz3/maps_to_images.py /path/to/maps/input/directory /output/directory --slices=20
```

The number of slices per axis is defaulted to 20.
This will generate 60 images for each map in the output_directory file.

The function itself is implemented like this:

```python
def directory_to_images(
    input_directory: str,
    slices_per_axis: int,
    output_directory: str
)
```

