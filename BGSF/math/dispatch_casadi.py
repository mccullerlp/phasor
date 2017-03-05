from __future__ import division, print_function
from . import dispatched
import functools
import numpy as np
import operator

import casadi

from .complex import Complex

dispatched.module_by_typemodule[('casadi',)] = [casadi]
dispatched.module_by_type[casadi.SX] = [casadi.SX]
dispatched.module_by_type[casadi.MX] = [casadi.MX]


def fix_custom_complex(otype, opname, lambda_syntax):
    op_orig = getattr(otype, opname, None)
    if op_orig is None:
        return

    def op_wrap(self, other):
        if isinstance(other, (complex, np.complex, np.complex64, np.complex128)):
            other = Complex(other.real, other.imag)
            return lambda_syntax(Complex(self), other)
        elif isinstance(other, (Complex)):
            return lambda_syntax(Complex(self), other)
        else:
            dtype = getattr(other, 'dtype', None)
            if dtype is not None:
                if np.issubdtype(dtype, complex):
                    other = Complex(other.real, other.imag)
                    return lambda_syntax(Complex(self), other)
                if dtype is object:
                    print(other)
            try:
                return op_orig(self, other)
            except TypeError:
                print(("Other Type: ", type(other)))
                #print other
                raise
    functools.update_wrapper(op_wrap, op_orig)

    setattr(otype, opname, op_wrap)
    return


def fix_many(otype):
    def null_conjugate(self):
        return self
    fix_custom_complex(otype, '__mul__'  , lambda s, o: s * o)
    fix_custom_complex(otype, '__rmul__' , lambda s, o: o * s)
    fix_custom_complex(otype, '__div__'  , lambda s, o: s / o)
    fix_custom_complex(otype, '__rdiv__' , lambda s, o: o / s)
    fix_custom_complex(otype, '__truediv__'  , operator.truediv)
    fix_custom_complex(otype, '__rtruediv__' , lambda s, o: operator.truediv(o, s))
    fix_custom_complex(otype, '__add__'  , lambda s, o: s + o)
    fix_custom_complex(otype, '__radd__' , lambda s, o: o + s)
    fix_custom_complex(otype, '__sub__'  , lambda s, o: s - o)
    fix_custom_complex(otype, '__rsub__' , lambda s, o: o - s)
    otype.conjugate = null_conjugate
    otype.__abs__ = lambda self: (self**2).sqrt()

fix_many(casadi.MX)
fix_many(casadi.SX)
#fix_many(casadi.DVector)

casadi.abs = abs
