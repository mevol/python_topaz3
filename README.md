[![LGTM alerts](https://img.shields.io/lgtm/alerts/g/DiamondLightSource/python-topaz3.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/DiamondLightSource/python-topaz3/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/DiamondLightSource/python-topaz3.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/DiamondLightSource/python-topaz3/context:python)
![Black Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Documentation Status](https://readthedocs.org/projects/python-topaz3/badge/?version=latest)](https://python-topaz3.readthedocs.io/en/latest/?badge=latest)

# Topaz3

A data manipulation and machine learning package for Macromolecular Crystallography (MX) at [**Diamond Light Source**](https://www.diamond.ac.uk/Home.html).

Specifically, it transforms electron density map data obtained from diffraction experiments 

## Installation

Clone the repository from the [source code](https://github.com/TimGuiteDiamond/topaz3) on Github:

```bash
git clone https://github.com/TimGuiteDiamond/topaz3.git
```

It is good practice to create a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) for development:

```bash
python3 -m venv topaz3_venv
```

Now activate the venv. *This is the only step to repeat after installation*.

```bash
source topaz3_venv/bin/activate
```

**Note:** topaz3_venv/bin/activate is a file so can be accessed the same way as any other file
(via absolute or relative path) 

Install an editable version of the package:

```bash
# Make sure to point this to the top level of the package
pip install -e topaz3
```

### Development
This will install the dependencies required to use Topaz3.
If you want to develop and contribute, follow these steps:

- Go to the top level of the package:
    ```bash
    cd topaz3    
    ```
- Install all necessary packages from *requirements.txt*
    ```bash
    pip install -r requirements.txt
    ```
- Install precommit hooks which will help keep the code maintainable:
    ```bash
    pre-commit install
    ```

## Usage

### Prepare some data

This package was designed for use at Diamond Light Source.
As such some assumptions have been made in encompassing scripts about file layout and information.
The Diamond use case will be discussed first and then the building blocks will be explained, which should help you implement the functionality here even if your setup is different.

It is assumed that some processing output will have provided a directory with many structures, each of which has the following information:
- original and inverse phase files
- cell group information in a .mtz file
- space group information in a .mtz or log file

This will look *roughly* like:

![Directory map](/documentation/images/prepare_training_data.png)

Note that this allows for the phase, cell and space information to be in entirely separate locations.
The important thing is that the directories all contain the same structure directories inside them.

From there, the path to the specific files can be defined relative to the structure directories.
This assumes that the cell and space files are in the same location within each structure directory.

**Example**: the cell info file for a structure with a [PDB ID](https://www.rcsb.org/pdb/staticHelp.do?p=help/advancedsearch/pdbIDs.html) of 4PIB
may be located at */scratch/ai_research/structures/4PIB/metadata/cell_info.mtz*.
In this case, the **cell_info_dir** would be */scratch/ai_research/structures* and the
**cell_info_path** would be *metadata/cell_info.mtz*.
At runtime, this will generate the full path for each structure in the cell info directory with the pattern
*{cell_info_dir}/{structure}/{cell_info_path}*.
The same process is applied for the space group prameters.

The phase information is located by searching the structure directory for a folder which matches the best space group label found in the space group file.
For example, this will be of the form "P12121".
The original and inverse phase files are both assumed to be within this directory.

From there, you must define *xyz* limits for the map file transformation.
We used 200x200x200 and a cube is required for further transformations using provided tools here.

Each phase file will produce a corresponding .map file in a folder you can define.

You may also choose to generate labels in a database based on the CC values of the original vs inverse hand.

Finally, the maps are sliced up into 2D image files and stored in the image directory for training.

As you can see, there are many parameters necessary for this processing, so the tool provided requires a [yaml](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) configuration file input.
You can generate this file now with:

``bash
topaz3.prepare --example config.yaml
``

which will generate a file that looks like this:
```yaml
phase_dir: /phase/directory/path
cell_info_dir: /cell/info/directory
cell_info_path: cell/info/path.mtx
space_group_dir: /space/group/directory
space_group_path: space/group/path.log
xyz_limits:
  - 200
  - 200
  - 200
db_path: /db/is/here.db
maps_dir: /output/maps/directory
slices_per_axis: 20
images_dir: /output/images/directory
```

From here, simple change the file paths according to the specification above and trigger the data preparation with:
```bash
topaz3.prepare config.yaml --make-output
```
*--make-output* simply generates the output directories and database if it cannot find them.
Leave it out to ensure only directories and databases which already exist are used.

If you want to perform the transformation but not produce results in a database, simply remove the *db_path* line from the config file.
You may want to do this if you have already generated your labels from well processed data and now want to repeat the data preparation and training cycle on different versions of the same structures.

You can check this has worked properly by looking in the map and images directory you specified.

Within the database there should now be two tables, ai_data and ai_labels, which can be used for training.

If you want to perform more specific versions of this transformation, please see: [Data Preparation](documentation/preparation.md)

**Note:** If you are not at Diamond, you may experience some issues with the shell scripts.
Go to topaz3/shell_scripts and alter these such that they run on your machine/system.
Most of this software is related to the [CCP4 project](http://www.ccp4.ac.uk/) and should be freely available.

### Predictions
Information about how to predict the scores from files can be found [here](documentation/predictions.md).

## Contributing

Changes to this project should use pre-commit with flake8 and black checks