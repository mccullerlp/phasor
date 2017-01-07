"""
"""
from __future__ import division, print_function

from declarative.bunch import Bunch

#TODO convert this to yaml

units = [
    Bunch(
        short = 'm',
        names = ['meter', 'meters', ],
        dim = 'length',
        scale = 1,
    ),
    Bunch(
        short = 'cm',
        names = ['centimeter', 'centimeters', ],
        dim = 'length',
        scale = 1e-2,
    ),
    Bunch(
        short = 'mm',
        names = ['millimeter', 'millimeters', ],
        dim = 'length',
        scale = 1e-3,
    ),
    Bunch(
        short = 'um',
        names = ['micron', 'micrometer', 'micrometers'],
        dim = 'length',
        scale = 1e-6,
    ),
    Bunch(
        short = 'nm',
        names = ['nanometer', 'nanometers', ],
        dim = 'length',
        scale = 1e-9,
    ),
    Bunch(
        short = 'pm',
        names = ['picometer', 'picometers', ],
        dim = 'length',
        scale = 1e-12,
    ),
    Bunch(
        short = 'fm',
        names = ['femtometer', 'femtometers', ],
        dim = 'length',
        scale = 1e-15,
    ),
    Bunch(
        short = 'am',
        names = ['attometer', 'attometers', ],
        dim = 'length',
        scale = 1e-18,
    ),
    Bunch(
        short = 'zm',
        names = ['zeptometer', 'zeptometers', ],
        dim = 'length',
        scale = 1e-21,
    ),
    Bunch(
        short = 'km',
        names = ['kilometer', 'kilometers', ],
        dim = 'length',
        scale = 1e3,
    ),
    Bunch(
        short = 'in',
        names = ['inch', 'inches', ],
        dim = 'length',
        scale = .0254
    ),
    Bunch(
        short = 'ft',
        names = ['foot', 'feet', ],
        dim = 'length',
        scale = .3048
    ),
]

units_lookup_short = dict()
units_lookup = dict()
units_lookup_dim = dict()
units_lookup_dim_short = dict()
for ubunch in units:
    units_lookup_short[ubunch.short] = ubunch
    units_lookup[ubunch.short] = ubunch
    for name in ubunch.names:
        units_lookup[name] = ubunch
    lst = units_lookup_dim.setdefault(ubunch.dim, [])
    lst.append(ubunch)
