# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from . import dispatched
import functools
import numpy as np
import operator

import casadi
#import casadi.SX

from .complex import Complex

dispatched.module_by_typemodule[('casadi',)] = [casadi]
dispatched.module_by_type[casadi.MX] = [casadi.MX]
dispatched.module_by_type[casadi.SX] = [casadi.SX]


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

    def null_conjugate(self):
        return self

    otype.conjugate = null_conjugate

    #TODO: does this need to be wrapper with a method descriptor?
    otype.__abs__ = lambda self: (self**2).sqrt()

    otype.real = property(lambda self : self)
    otype.imag = property(lambda self : 0)


fix_many(casadi.MX)
fix_many(casadi.SX)
#fix_many(casadi.DVector)

casadi.abs = abs

def zero_check_heuristic(arg):
    return arg.is_zero()


#monkey patch
casadi.MX.zero_check_heuristic = zero_check_heuristic
casadi.SX.zero_check_heuristic = zero_check_heuristic
#casadi.zero_check_heuristic = zero_check_heuristic


def check_symbolic_type_MX(arg):
    return casadi.MX


casadi.MX.check_symbolic_type = check_symbolic_type_MX


def check_symbolic_type_SX(arg):
    return casadi.SX


casadi.SX.check_symbolic_type = check_symbolic_type_SX


