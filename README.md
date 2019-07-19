[![LGTM alerts](https://img.shields.io/lgtm/alerts/g/DiamondLightSource/python-topaz3.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/DiamondLightSource/python-topaz3/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/DiamondLightSource/python-topaz3.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/DiamondLightSource/python-topaz3/context:python)
![Black Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Documentation Status](https://readthedocs.org/projects/python-topaz3/badge/?version=latest)](https://python-topaz3.readthedocs.io/en/latest/?badge=latest)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

# Topaz3

A data manipulation and machine learning package for Macromolecular Crystallography (MX) at [**Diamond Light Source**](https://www.diamond.ac.uk/Home.html).

Specifically, it transforms electron density map data obtained from diffraction experiments and uses machine learning to estimate whether the original or inverse hand has clearer information.

Read the documentation about how it works at: https://python-topaz3.readthedocs.io/en/latest/

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

## Contributing

Changes to this project should use pre-commit with flake8 and black checks