# -*- coding: utf-8 -*-
"""
"""
from __future__ import absolute_import, division, print_function, unicode_literals
from ..utilities.future_from_2 import str
import pint

ureg = pint.UnitRegistry()

def mag1_units(pint_quantity):
    if isinstance(pint_quantity, ureg.Quantity):
        #TODO make this a real float check with an epsilon
        if pint_quantity.magnitude == 1:
            return str(pint_quantity.units)
    if isinstance(pint_quantity, str):
        assert(False)
    return str(pint_quantity)

