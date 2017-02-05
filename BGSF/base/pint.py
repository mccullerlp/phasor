"""
"""
from __future__ import division, print_function
import pint

ureg = pint.UnitRegistry()

def mag1_units(pint_quantity):
    if isinstance(pint_quantity, ureg.Quantity):
        if pint_quantity.m == 1:
            return str(pint_quantity.units)
    return str(pint_quantity)

