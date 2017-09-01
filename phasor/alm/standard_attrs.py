# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from builtins import str
#from builtins import range

import declarative as decl
from ..base.multi_unit_args import (
    generate_refval_attribute,
    #unitless_refval_attribute,
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
            ctree_name = 'location',
            preferred_attr = 'loc_preferred',
            default_attr = '_loc_default',
            prototypes = ['full'],
        )
    return loc_m


def generate_reference_m():
    @decl.group_dproperty
    def ref_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['ref', ],
            ctree_name = 'reference',
            preferred_attr = 'ref_preferred',
            default_attr = '_ref_default',
            prototypes = ['full', 'base'],
        )
    return ref_m


def generate_boundary_left_m():
    @decl.group_dproperty
    def boundary_left_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['boundary_left', ],
            ctree_name = 'boundary_left',
            preferred_attr = 'boundary_left_preferred',
            default_attr = '_boundary_left_default',
            prototypes = ['full', 'base'],
        )
    return boundary_left_m


def generate_boundary_right_m():
    @decl.group_dproperty
    def boundary_right_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['boundary_right', ],
            ctree_name = 'boundary_right',
            preferred_attr = 'boundary_right_preferred',
            default_attr = '_boundary_right_default',
            prototypes = ['full', 'base'],
        )
    return boundary_right_m


def generate_f_m():
    @decl.group_dproperty
    def f_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['f'],
            ctree_name = 'focal_length',
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
            ctree_name = 'length',
            preferred_attr = 'L_preferred',
            default_attr = '_length_default',
            prototypes = ['full', 'base'],
        )
    return L_m

def generate_R_m(variant = ''):
    @decl.group_dproperty
    def R_m(desc):
        desc.name_change('R{0}_m'.format(variant))
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['R{0}'.format(variant), 'ROC{0}'.format(variant)],
            ctree_name = 'ROC{0}'.format(variant),
            preferred_attr = 'ROC{0}_preferred'.format(variant),
            default_attr = '_ROC{0}_default'.format(variant),
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
            ctree_name = 'detune',
            preferred_attr = 'detune_preferred',
            prototypes = ['full', 'base'],
        )
    return detune_m
