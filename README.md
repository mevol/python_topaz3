# dls_topaz3

This is a python 3 refactoring of the existing topaz module for converting phase information into a regularly sized map for machine learning at Diamond Light Source.

## Usage
###Prepare training data
Before reading about how to use this function, take a moment to look at the diagram below which shows the expected directory structure.
This is based on the initial training set at Diamond and may change in the future.
Input parameters are in ***bold italics***.
![Prepare training data diagram](documentation/images/prepare_training_data.png?raw=true "Inputs to prepare training data")

**Inputs**
- *phase_directory* - directory with phase information for all the structures you wish to turn into map data ready for training
- *cell_info_directory* - directory with cell info file for all structures
- *cell_info_path* - path for cell info file within each structure directory
- *space_group_directory* - directory with space space group file for all structures
- *space_group_path* - path for space group file within each structure directory
- *xyz_limits* - list or tuple of three integers specifying the size of the output map
- *database* - location of the database from which to store the truth values
- *output_directory* - directory in which to put all of the output files, must exist before runtime
- *delete_temp* - binary on whether or not to delete files produced during the intermediate steps, True by default

**NOTE:** Absolute paths are used for directories, relative paths below the structure directory are used for ***cell_info_path*** and ***space_group_path*** (no leading slash)

**Outputs**
- *Output files* - .map files with the specified dimensions
- *Temporary files* - some files marked with *_temp* which are the files created during the intermediate steps of the transformation
- If the function ran properly, it should return *True*

**From yaml file**

As there are so many inputs which are likely to be long filepaths, it will be easier to execute with the aid of a yaml file.
Use the below template (keys are correct, values are not):
```yaml
phase_dir: /phase/directory/path
cell_info_dir: cell/info/directory
cell_info_path: /cell/info/path
space_group_dir: space/group/directory
space_group_path: space/group/path
xyz_limits:
  - 200
  - 200
  - 200
db_path: /db/is/here
output_dir: /output/directory/path
```
You may then execute the command with
```bash
python3 prepare_training_data.py yaml {config_file_path.yaml}
```

**From command line**

To execute directly from the command line, use the same module but with *cmd* keyword before the positional arguments.
Here is the help text:
```bash
usage: prepare_training_data.py cmd [-h] [--keep_temp]
                                    phase_dir cell_info_dir cell_info_path
                                    space_group_dir space_group_path xyz xyz
                                    xyz db output_dir

positional arguments:
  phase_dir         top level directory for phase information
  cell_info_dir     top level directory for cell info
  cell_info_path    cell info file within each structure folder
  space_group_dir   top level directory for space group
  space_group_path  space group file within each structure folder
  xyz               xyz size of the output map file
  db                location of the sqlite3 database to store training
                    information
  output_dir        directory to output all map files to

optional arguments:
  -h, --help        show this help message and exit
  --keep_temp       keep the temporary files after processing
```

### Files to map
The high level conversion for a phase file to a regularized map file is as follows:

**Inputs**
- *phase_filename* - absolute file location of the phase file you wish to transform. Must be .phs or .pha
- *cell_info_filepath* - absolute file location of the file with cell information (lengths and angles) which will be used to calculate the transformation.
- *space_group_filepath* - absolute file location of the file which contains the correct space group for the phase file. Can be a .mtz or some other file.
- *xyz_limits* - list with three integer values which are the dimensions of the map file to be outputted.
- *output_filename* - absolute file location of the output file, must be in an already existing directory.

**Outputs**
- *Ouptut file* - .map file with the specified dimensions
- *Temporary files* - some files marked with *_temp* which are the files created during the intermediate steps of the transformation
- If the function ran properly, it should return *True*

**Example**
```python
from dls_topaz3 import files_to_map
files_to_map("/location/of/phase/file/structure.phs",
             "/location/of/cell/info/cell_info.mtz",
             "/location/of/space/group/simple_xia2_to_shelxcde.log",
             [200, 200, 200],
             "/location/of/output/output.map")
```

### Phase to map
This is the function which sits inside *files_to_map* and it can be accessed directly if so wished.

**Inputs**
- *phase_filename* - absolute file location of the phase file you wish to transform. Must be .phs or .pha
- *cell_info* - list of 6 values for the cell lengths and angles in the form *[a, b, c, alpha, beta, gamma]* 
- *space_group* - string of the space group, e.g *"P121"*, but can also be an integer for the standard space group number. String preferred as more exact.
- *xyz_limits* - list with three integer values which are the dimensions of the map file to be outputted.
- *output_filename* - absolute file location of the output file, must be in an already existing directory.

**Outputs**
- *Output file* - .map file with the specified dimensions
- *Temporary files* - some files marked with *_temp* which are the files created during the intermediate steps of the transformation
- If the function ran properly, it should return *True*

**Example**
```python
from dls_topaz3 import files_to_map
phase_to_map("/location/of/phase/file/structure.phs",
             [66.45, 112.123, 149.896, 90, 90, 90],
             "P212121",
             [200, 200, 200]
             "/location/of/output/output.map",)
```