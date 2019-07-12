from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os

version = os.environ.get("MODULEVER", "0.0")

setup(
    #    install_requires = ['cothread'], # require statements go here
    name="dls_topaz3",
    version=version,
    description="Module",
    author="riw56156",
    author_email="riw56156@fed.cclrc.ac.uk",
    packages=["dls_topaz3"],
    install_requires=[
        "tensorflow-gpu",
        "Keras",
        "Pillow",
        "procrunner",
        "PyYaml",
        "scikit-learn",
        "mrcfile",
        "pandas",
        "logconfig",
        "matplotlib",
    ],
    entry_points={
        "console_scripts": [
            "dls_topaz.prepare = dls_topaz3.command_line_preparation:main"
        ]
    },
    #    entry_points = {'console_scripts': ['test-python-hello-world = dls_topaz3.dls_topaz3:main']}, # this makes a script
    #    include_package_data = True, # use this to include non python files
    zip_safe=False,
)
