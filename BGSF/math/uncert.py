"""
"""
from __future__ import division
from past.utils import old_div

import uncertainties
import uncertainties.umath
from .complex import Complex
import functools
import numpy as np

from . import dispatched

dispatched.module_by_type[uncertainties.AffineScalarFunc] = [uncertainties.umath]

#mul_orig = uncertainties.AffineScalarFunc.__mul__
#
#
#def mul_wrap(self, other):
#    if isinstance(other, complex):
#        other = Complex(other)
#        return self * other
#    else:
#        return mul_orig(self, other)
#
#uncertainties.AffineScalarFunc.__mul__ = mul_wrap


def fix_op(opname, lambda_syntax):
    op_orig = getattr(uncertainties.AffineScalarFunc, opname)

    def op_wrap(self, other):
        if isinstance(other, (complex, np.complex, np.complex64, np.complex128)):
            other = Complex(other.real, other.imag)
            return lambda_syntax(self, other)
        else:
            return op_orig(self, other)
    functools.update_wrapper(op_wrap, op_orig)

    setattr(uncertainties.AffineScalarFunc, opname, op_wrap)
    return


fix_op('__mul__'  , lambda s, o: s * o)
fix_op('__rmul__' , lambda s, o: o * s)
fix_op('__div__'  , lambda s, o: old_div(s, o))
fix_op('__rdiv__' , lambda s, o: old_div(o, s))
fix_op('__add__'  , lambda s, o: s + o)
fix_op('__radd__' , lambda s, o: o + s)
fix_op('__sub__'  , lambda s, o: s - o)
fix_op('__rsub__' , lambda s, o: o - s)

uncertainties.AffineScalarFunc.conjugate = lambda self: self
















