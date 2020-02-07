import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, __, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='trackpipe',
    version='1.0.2',
    description='Pipeline Implementation of trackbar from: https://github.gatech.edu/bkerner3/trackbar',
    packages=[
        'trackpipe',
    ],
    install_requires=[
    ],
    package_data=package_data("trackpipe", []),
)

