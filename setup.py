# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

from setuptools import setup, find_packages

def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name="yaskawa-convert-status-into-event",
    version="0.0.1",
    author="Latona",
    packages=find_packages("./src"),
    package_dir={"":"src"},
    install_requires=_requires_from_file('requirements.txt'),
    tests_require=[]
)
