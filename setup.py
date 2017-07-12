#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
import os
import sys
from distutils.sysconfig import get_python_lib

from setuptools import find_packages, setup


version = '1.0.0dev1'

extra_install_requires = []
if sys.version_info < (3,0):
    extra_install_requires.append('future')

setup(
    name='phasor',
    version=version,
    url='',
    author='Lee McCuller',
    author_email='Lee.McCuller@gmail.com',
    description=(
        'Scientific modeling of linearized optics, electronics, mechanics, and signal flow in the frequency domain'
    ),
    license='Apache v2',
    packages=find_packages(exclude=['doc']),
    #include_package_data=True,
    #scripts=[''],
    #entry_points={'console_scripts': ['',]},
    setup_requires = [
        'pytest-runner'
    ],
    install_requires = [
        'pint',
        'numpy',
        'scipy',
        'matplotlib',
        'IPython',
        'pyyaml',
        'declarative',
        'scikit-umfpack',
    ] + extra_install_requires,
    tests_require = [
        'pytest',
        'pytest-runner',
        'pytest-benchmark',
    ],
    extras_require = {
        "fitting" : ["casadi"],
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
        'Topic :: Scientific/Engineering :: Physics',
    ],
)

