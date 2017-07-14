# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import declarative as decl
from ..base.multi_unit_args import (
    generate_refval_attribute,
    unitless_refval_attribute,
)

from ..base import units


def generate_power(name = 'power'):
    @decl.group_dproperty
    def power(desc):
        return generate_refval_attribute(
            desc,
            ubunch = units.laser_power,
            stems = [name, ],
            ctree_name = name,
            preferred_attr = name,
            default_attr = '_{0}_default'.format(name),
            prototypes = ['full', 'base'],
        )
    power.__name__ = name
    return power


def generate_L_detune(name = 'L_detune'):
    @decl.group_dproperty
    def L_detune(desc):
        return generate_refval_attribute(
            desc,
            ubunch = units.lengths_small,
            stems = [name, ],
            ctree_name = name,
            preferred_attr = name,
            default_attr = '_{0}_default'.format(name),
            prototypes = ['full', 'base'],
        )
    L_detune.__name__ = name
    return L_detune


def generate_length(name = 'length'):
    return generate_L_detune(name = name)


def generate_rotate(name = 'rotate', default = True):
    @decl.group_dproperty
    def rotate(desc):
        return generate_refval_attribute(
            desc,
            ubunch = units.rotation_deg,
            stems = [name, ],
            ctree_name = name,
            preferred_attr = name,
            default_attr = '_{0}_default'.format(name) if default else None,
            prototypes = ['full', 'base'],
        )
    rotate.__name__ = name
    return rotate

