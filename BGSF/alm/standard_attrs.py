"""
"""
from __future__ import division, print_function
from builtins import str
from builtins import range

import declarative as decl
from ..base.multi_unit_args import (
    generate_refval_attribute,
)

from ..base.units import (
    lengths_small,
)


def generate_loc_m():
    @decl.group_dproperty
    def loc_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['loc', ],
            ooa_name = 'location',
            preferred_attr = 'loc_preferred',
            default_attr = '_loc_default',
            prototypes = ['full'],
        )
    return loc_m


def generate_f_m():
    @decl.group_dproperty
    def f_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['f'],
            ooa_name = 'focal_length',
            preferred_attr = 'f_preferred',
            prototypes = ['full', 'base'],
        )
    return f_m

def generate_L_m():
    @decl.group_dproperty
    def L_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['L', 'length'],
            ooa_name = 'length',
            preferred_attr = 'L_preferred',
            prototypes = ['full', 'base'],
        )
    return L_m

def generate_R_m(variant = ''):
    @decl.group_dproperty
    def R_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['R{0}'.format(variant), 'ROC{0}'.format(variant)],
            ooa_name = 'ROC{0}'.format(variant),
            preferred_attr = 'ROC{0}_preferred'.format(variant),
            prototypes = ['full', 'base'],
        )
    return R_m

def generate_detune_m():
    @decl.group_dproperty
    def detune_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['detune', ],
            ooa_name = 'detune',
            preferred_attr = 'detune_preferred',
            prototypes = ['full', 'base'],
        )
    return detune_m
