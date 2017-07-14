# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import sys
from ..utilities.future_from_2 import repr_compat

from collections import namedtuple
from .dispatched import sin, cos, atan
from . import dispatched
from declarative.utilities.representations import ReprMixin
from math import pi
import numpy as np

ComplexTuple = namedtuple('ComplexTuple', ['real', 'imag'])


#class Complex(ComplexTuple):
#    def __new__(cls, real, imag=None):
#        if imag is None:
#            inst = super(Complex, cls).__new__(cls, real.real, real.imag)
#        else:
#            inst = super(Complex, cls).__new__(cls, real, imag)
#        return inst

class Complex(ReprMixin):
    #__slots__ = ['real', 'imag']

    def __init__(self, real, imag=None):
        if imag is None:
            #try to adapt argument if it could be a complex object
            try:
                imag = real.imag
            except AttributeError:
                pass
            else:
                real = real.real
        rdtype = getattr(real, 'dtype', None)
        if rdtype is not None:
            if rdtype == np.object:
                #print real
                raise RuntimeError("Complex is supposed to remove the need for object arrays")
        self.real = real
        if imag is not None:
            self.imag = imag
        else:
            self.imag = 0.
        return

    @repr_compat
    def __repr__(self):
        return ''.join((self.__class__.__name__, "(", repr(self.real), ", ", repr(self.imag), ")"))

    def __str__(self):
        return ''.join((self.__class__.__name__,"(", str(self.real), " + ", str(self.imag), "j)"))

    def __add__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        return self.__class__(
            self.real + o_real,
            self.imag + o_imag
        )

    def __radd__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        return self.__class__(
            o_real + self.real,
            o_imag + self.imag
        )

    def __sub__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        return self.__class__(
            self.real - o_real,
            self.imag - o_imag
        )

    def __rsub__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        return self.__class__(
            o_real - self.real,
            o_imag - self.imag
        )

    def __mul__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        return self.__class__(
            self.real * o_real - self.imag * o_imag,
            self.real * o_imag + self.imag * o_real,
        )

    def __rmul__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        return self.__class__(
            o_real * self.real - o_imag * self.imag,
            o_real * self.imag + o_imag * self.real,
        )

    def __div__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        den = o_real * o_real + o_imag * o_imag
        return self.__class__(
            ((self.real * o_real + self.imag * o_imag) / den),
            ((self.imag * o_real - self.real * o_imag) / den),
        )

    def __rdiv__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        den = self.real * self.real + self.imag * self.imag
        return self.__class__(
            ((o_real * self.real + o_imag * self.imag) / den),
            ((o_imag * self.real - o_real * self.imag) / den),
        )

    def __truediv__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        den = o_real * o_real + o_imag * o_imag
        return self.__class__(
            ((self.real * o_real + self.imag * o_imag) / den),
            ((self.imag * o_real - self.real * o_imag) / den),
        )

    def __rtruediv__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        den = self.real * self.real + self.imag * self.imag
        return self.__class__(
            ((o_real * self.real + o_imag * self.imag) / den),
            ((o_imag * self.real - o_real * self.imag) / den),
        )

    def __eq__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        return (
            (self.real == other.real) and
            (self.imag == other.imag)
        )

    def __ne__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        return (
            (self.real != other.real) or
            (self.imag != other.imag)
        )

    def __pow__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = None
        #print o_real, o_imag
        if o_imag is None or o_imag == 0:
            val = self
            if isinstance(o_real, int) or (isinstance(o_real, float) and (int(o_real) == o_real)):
                o_real = int(o_real)
                while o_real % 2 == 0:
                    o_real = (o_real / 2)
                    val = val * val
                for _ in range(o_real - 1):
                    val = val * self
                return val
            if isinstance(o_real, float) and o_real == .5:
                aval = abs(self)
                rval_sq = ((aval + self.real) / 2)
                ival_sq = ((aval - self.real) / 2)
                #this is weird, but needed to work with uncertainties
                if rval_sq == 0:
                    rval_sq = 0
                if ival_sq == 0:
                    ival_sq = 0
                if self.imag >= 0:
                    return Complex(rval_sq**.5, ival_sq**.5)
                else:
                    return Complex(rval_sq**.5, -ival_sq**.5)

        aval = abs(self)
        if self.real == 0:
            if self.imag >= 0:
                phase = (pi / 2)
            else:
                phase = (-pi / 2)
        else:
            phase = atan(self.imag / self.real)
        if self.real < 0:
            if self.imag >= 0:
                phase += pi
            else:
                phase -= pi

        aval = aval ** o_real
        phase = phase * o_real
        if o_imag is None:
            return Complex(aval * cos(phase), -aval * sin(phase))
        return NotImplemented

    def __rpow__(self, other):
        try:
            o_real = other.real
            o_imag = other.imag
        except AttributeError:
            o_real = other
            o_imag = 0
        if self.imag == 0:
            return other**self.real
        return NotImplemented

    def __neg__(self):
        return self.__class__(-self.real, -self.imag)

    def __pos__(self):
        return self

    def __abs__(self):
        return (self.real * self.real + self.imag * self.imag)**.5

    def abs_sq(self):
        return (self.real * self.real + self.imag * self.imag)

    def __hash__(self):
        return hash(self.real) ^ hash(self.imag)

    def __numpy_ufunc__(ufunc, method_name, self_idx, in_tup, **kwargs):
        print("UFUNC: ", ufunc)
        return NotImplemented

    def conjugate(self):
        return self.__class__(
            self.real,
            -self.imag,
        )

    def __getitem__(self, idx):
        return self.__class__(
            self.real[idx],
            self.imag[idx],
        )

    #def exp(self):
    #    return exp(self)


def exp(arg):
    mag = dispatched.exp(arg.real)
    retval = Complex(mag * dispatched.cos(arg.imag), mag * dispatched.sin(arg.imag))
    return retval

def angle(arg, deg = False):
    if arg.real == 0:
        if arg.imag >= 0:
            phase = (pi / 2)
        else:
            phase = (-pi / 2)
    else:
        phase = atan(arg.imag / arg.real)
    if arg.real < 0:
        if arg.imag >= 0:
            phase += pi
        else:
            phase -= pi
    if deg:
        return phase * 180 / pi
    else:
        return phase

def zero_check_heuristic(arg):
    return dispatched.zero_check_heuristic(arg.real) and dispatched.zero_check_heuristic(arg.imag)


dispatched.module_by_type[Complex] = [sys.modules[__name__]]


def check_symbolic_type(arg):
    sym = dispatched.check_symbolic_type(arg.real)
    if not sym:
        return dispatched.check_symbolic_type(arg.imag)
    else:
        return sym

