#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
import os
import sys
from distutils.sysconfig import get_python_lib

from setuptools import find_packages, setup


version = '1.0.0a1'


setup(
    name='OpenLoop',
    version=version,
    url='',
    author='Lee McCuller',
    author_email='Lee.McCuller@gmail.com',
    description=(
        'Scientific Modelling'
    ),
    license='Apache v2',
    packages=find_packages(exclude=['doc']),
    #include_package_data=True,
    #scripts=[''],
    #entry_points={'console_scripts': ['',]},
    install_requires=[],
    extras_require={
        "hdf" : ["h5py"],
        "test" : ["pytest"],
    },
    zip_safe=False,
    keywords = 'Controls Linear Physics',
    classifiers=[
        'Development Status :: 3 - Alpha ',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

