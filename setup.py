# these lines allow the version to be specified in Makefile.private
import os

from setuptools import setup

version = os.environ.get("MODULEVER", "0.0")

setup(
    #    install_requires = ['cothread'], # require statements go here
    name="topaz3",
    version=version,
    description="Module",
    author="Tim Guite",
    author_email="tim.guite@diamond.ac.uk",
    packages=["topaz3", "topaz3.training_models"],
    install_requires=[
        "tensorflow==2.12.1",
        "Keras",
        "Pillow",
        "procrunner",
        "PyYaml",
        "scikit-learn",
        "mrcfile",
        "pandas",
        "logconfig",
        "matplotlib",
        "configargparse",
    ],
    entry_points={
        "console_scripts": [
            "topaz3.prepare = topaz3.command_line_preparation:main",
            "topaz3.test_split = topaz3.train_test_split:command_line",
            "topaz3.predict_from_maps = topaz3.predictions:command_line",
            "topaz3.filter = topaz3.filters:filter_command_line",
        ]
    },
    #    entry_points = {'console_scripts': ['test-python-hello-world = topaz3.topaz3:main']}, # this makes a script
    #    include_package_data = True, # use this to include non python files
    zip_safe=False,
)
