#!/usr/bin/env python3

from setuptools import setup, find_packages
from distutils.command.build_py import build_py
import os
import os.path
import glob


setup(
    name="icpfc2021",
    description="Pitiful attempt at ICPFC 2021",
    version="1.0",
    package_dir={"": "src"},
    packages=[
        "icfpc2021",
        "icfpc2021.solver",
    ],
    install_requires=[
        "requests",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "icfpc2021=icfpc2021.solver:main",
        ]
    },
)
