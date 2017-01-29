"""
"""
from __future__ import division, print_function

import declarative as decl
from ..base.multi_unit_args import (
    generate_refval_attribute,
)

from ..base.units import (
    lengths_small,
)


def generate_power_W():
    @decl.group_dproperty
    def power_W(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['power', ],
            ooa_name = 'power',
            preferred_attr = 'power',
            default_attr = '_power_default',
            prototypes = ['full', 'base'],
        )
    return power_W


def generate_L_detune_m():
    @decl.group_dproperty
    def L_detune_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['L_detune', ],
            ooa_name = 'L_detune',
            preferred_attr = 'L_detune',
            prototypes = ['full', 'base'],
        )
    return L_detune_m


def generate_length_m():
    @decl.group_dproperty
    def length_m(desc):
        return generate_refval_attribute(
            desc,
            ubunch = lengths_small,
            stems = ['length', 'L'],
            ooa_name = 'length',
            preferred_attr = ('length', 'L'),
            prototypes = ['full', 'base'],
        )
    return length_m
