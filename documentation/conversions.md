# Conversions

This file contains information about specific file conversions which may be necessary as part of the topaz3 processing and prediction pipeline.

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
from topaz3.conversions import files_to_map
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
from topaz3.conversions import phase_to_map
phase_to_map("/location/of/phase/file/structure.phs",
             [66.45, 112.123, 149.896, 90, 90, 90],
             "P212121",
             [200, 200, 200],
             "/location/of/output/output.map")
```
