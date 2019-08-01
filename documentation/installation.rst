===============
Getting Started
===============

Prerequisites
-------------

To use the machine learning side of Topaz3, `tensorflow-gpu <https://www.tensorflow.org/install/gpu>`_ is required.
This speeds up the training and use of neural networks.
However, there are some restrictions regarding what version of tensorflow-gpu can be used, depending on the version of
CUDA supported by the GPU. Use the table on `this page <https://www.tensorflow.org/install/source#tested_build_configurations>`_
to make sure that the setup you plan to run on is installed correctly.

**Topaz3** was developed and tested with *tensorflow-gpu 1.12.0* and *CUDA 9.*

Installation
------------

Clone the repository from the `source code <https://github.com/DiamondLightSource/python-topaz3.git>`_ on Github:

.. code-block:: bash

    git clone https://github.com/DiamondLightSource/python-topaz3.git

It is good practice to create a `virtual environment <https://realpython.com/python-virtual-environments-a-primer>`_ for development:

.. code-block:: bash

    python3 -m venv topaz3_venv

Now activate the venv. *This is the only step to repeat after installation*.

.. code-block:: bash

    source topaz3_venv/bin/activate

**Note:** topaz3_venv/bin/activate is a file so can be accessed the same way as any other file
(via absolute or relative path) -
*source* puts the environment in your terminal session.

Install an editable version of the package:

.. code-block:: bash

    # Make sure to point this to the top level of the package
    pip install -e topaz3

Development
^^^^^^^^^^^

This will install the dependencies required to use Topaz3.
If you want to develop and contribute, follow these steps:

- Go to the top level of the package:

    .. code-block:: bash

        cd topaz3

- Install all necessary packages from *requirements.txt*

    .. code-block:: bash

        pip install -r requirements.txt

- Install precommit hooks which will help keep the code maintainable:

    .. code-block:: bash

        pre-commit install

