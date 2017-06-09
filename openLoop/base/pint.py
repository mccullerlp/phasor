"""
"""
from __future__ import division, print_function, absolute_import
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

