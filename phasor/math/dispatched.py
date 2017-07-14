# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import math
import cmath
import numpy as np
import scipy.special
from . import dispatch_defaults

npmath = [np, scipy.special]

module_by_type = {
    int           : [math, cmath, scipy.special],
    float         : [math, cmath, scipy.special],
    float         : [math, cmath, scipy.special],
    np.float      : npmath,
    np.int        : npmath,
    np.float32    : npmath,
    np.float64    : npmath,
    np.int8       : npmath,
    np.int16      : npmath,
    np.int32      : npmath,
    np.int64      : npmath,
    np.complex    : npmath,
    np.complex64  : npmath,
    np.complex128 : npmath,
    complex       : [cmath, scipy.special, np],
    np.ndarray    : [np, scipy.special],
}

module_by_typemodule = {
}


def generate_dispatched(func_name):
    def func(arg, **kwargs):
        atype = type(arg)
        mod_list = module_by_type.get(atype, None)
        if mod_list is None:
            amods = tuple(atype.__module__.split('.'))
            while amods:
                mod_list = module_by_typemodule.get(amods, None)
                if mod_list is not None:
                    module_by_type[amods] = atype
                    break
                amods = amods[:-1]
        if mod_list is None:
            mod_list = []
        for mod in mod_list + [dispatch_defaults]:
            try:
                act_func = getattr(mod, func_name)
                break
            except AttributeError:
                pass
        else:
            raise RuntimeError("Could not find function {0} for argument of type {1}".format(func_name, type(arg)))
        return act_func(arg, **kwargs)
    func.__name__ = str(func_name)
    return func


def re(obj):
    return obj.real

def im(obj):
    return obj.imag

def conjugate(obj):
    try:
        return obj.conjugate()
    except AttributeError:
        pass

    try:
        r = re(obj)
        i = im(obj)
        return obj.__class__(r, i)
    except AttributeError:
        pass

    return obj


_abs = abs
abs = _abs


def abs_sq(obj):
    from .complex import Complex
    cobj = Complex(obj)
    return cobj.abs_sq()

def zero_check_heuristic_np(arg):
    return np.all(arg == 0)

np.abs_sq = abs_sq
np.zero_check_heuristic = zero_check_heuristic_np

#shouldn't be allowed?!
mod_locals = locals()

def inject_dispatched(func_name):
    mod_locals[func_name] = generate_dispatched(func_name)


for name in dir(cmath):
    if name[0] != '_':
        inject_dispatched(name)

for name in dir(dispatch_defaults):
    if name[0] != '_':
        inject_dispatched(name)

for name in dir(math):
    if name[0] != '_':
        inject_dispatched(name)

for name in dir(scipy.special):
    if name[0] != '_':
        inject_dispatched(name)

inject_dispatched('angle')

zero_check_heuristic_run = generate_dispatched('zero_check_heuristic')

def zero_check_heuristic(arg):
    if isinstance(arg, (int, float, complex)):
        return arg == 0
    elif isinstance(arg, np.ndarray):
        if np.issubdtype(arg.dtype, np.number):
            return np.all(arg == 0)
        else:
            raise NotImplementedError("Can't handle such dtypes")
    else:
        return zero_check_heuristic_run(arg)


check_symbolic_type_run = generate_dispatched('check_symbolic_type')

def check_symbolic_type(arg):
    if isinstance(arg, (int, float, complex)):
        return False
    elif isinstance(arg, np.ndarray):
        if np.issubdtype(arg.dtype, np.number):
            return False
        else:
            raise NotImplementedError("Can't handle such dtypes")
    else:
        return check_symbolic_type_run(arg)

#doing this here to prevent a weird error where np is overridden
import numpy as np


