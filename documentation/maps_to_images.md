# Maps to Images

Now that you have generated all of your map files, it is necessary to slice them up into many images for training, validating and testing the machine learning model.

This is a relatively easy process, although it can take some time.
By default, the program will display output to the terminal to let you know it is working.

```bash
python dls_topaz3/maps_to_images.py --help
usage: maps_to_images.py [-h] [--slices SLICES] [--quiet] [--test]
                         maps_directory output_directory

Converts directory of map files to image slices.

positional arguments:
  maps_directory    directory which contains map files
  output_directory  directory to output image files to

optional arguments:
  -h, --help        show this help message and exit
  --slices SLICES   optionally specify the number of slices per axis,
                    default=20
  --quiet           no terminal output during healthy execution
  --test            run test of sphere with graphical output
```

The number of slices per axis is defaulted to 20.
This will generate 60 images for each map in the output_directory file.

The function itself is implemented like this:

```python
def directory_to_images(
    input_directory: str,
    slices_per_axis: int,
    output_directory: str,
    output: bool =False
)
```

