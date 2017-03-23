# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from BGSF.utilities.print import print
import declarative

import numpy as np

#from numbers import Number
#import warnings
from ..base import units

from . import ports

from . import siso_filter

from ..base.multi_unit_args import (
    unitless_refval_attribute,
    generate_refval_attribute,
)

class SRealZPCascade(siso_filter.TransferFunctionSISOBase):

    @declarative.dproperty
    def poles(self, plist):
        return plist

    @declarative.dproperty
    def zeros(self, zlist):
        return zlist

    @declarative.dproperty
    def N_poles(self):
        val = self.ooa_params.setdefault('N_poles', len(self.poles))
        return val

    @declarative.dproperty
    def N_zeros(self):
        val = self.ooa_params.setdefault('N_zeros', len(self.poles))
        return val

    def __build__(self):
        super(SRealZPCascade, self).__build__()
        return

    @declarative.mproperty
    def fitter_data(self):
        """
        Combination of all subordinate fitter parameters to fully fit this function
        """
        fitters = []
        return fitters

class SBQFCascade(siso_filter.TransferFunctionSISOBase):
    @declarative.dproperty
    def poles(self, plist):
        return plist

    @declarative.dproperty
    def zeros(self, zlist):
        return zlist

    @declarative.dproperty
    def N_poles(self):
        val = self.ooa_params.setdefault('N_poles', len(self.poles))
        return val

    @declarative.dproperty
    def N_zeros(self):
        val = self.ooa_params.setdefault('N_zeros', len(self.poles))
        return val

    def __build__(self):
        super(SRealZPCascade, self).__build__()
        return

    @declarative.mproperty
    def fitter_data(self):
        """
        Combination of all subordinate fitter parameters to fully fit this function
        """
        fitters = []
        return fitters


class SRationalFilter(siso_filter.TransferFunctionSISOBase):

    delay_default = ('delay_s', 0)
    @declarative.declarative_adv_group
    def delay(desc):
        name = desc.__name__
        return generate_refval_attribute(
            desc,
            ubunch = units.time_small,
            stems = [name, ],
            ooa_name = name,
            preferred_attr = name,
            default_attr = '{0}_default'.format(name),
            prototypes = ['full', 'base'],
        )

    @declarative.dproperty_adv
    def gain(desc):
        return unitless_refval_attribute(desc)

    @declarative.dproperty
    def cpoles(self, plist):
        return plist

    @declarative.dproperty
    def czeros(self, zlist):
        return zlist

    @declarative.dproperty
    def rpoles(self, plist):
        return plist

    @declarative.dproperty
    def rzeros(self, zlist):
        return zlist

    def cplx(self):
        return SBQFCascade(
            poles = self.cpoles,
            zeros = self.czeros,
        )

    def real(self):
        return SRealZPCascade(
            poles = self.rpoles,
            zeros = self.rzeros,
        )

    def filter_func(self, freq):
        pre = self.gain.val * self.symbols.math.exp(self.symbols.i2pi * freq * self.delay_s.val)
        real = self.real.filter_func(freq)
        cplx = self.cplx.filter_func(freq)
        return pre * real * cplx

    @declarative.mproperty
    def fitter_data(self):
        """
        Combination of all subordinate fitter parameters to fully fit this function
        """
        fitters = []
        fitters.extend(self.delay.fitter_data)
        fitters.extend(self.gain.fitter_data)
        fitters.extend(self.real.fitter_data)
        fitters.extend(self.cplx.fitter_data)
        return fitters

    def __build__(self):
        super(SRationalFilter, self).__build__()
        return


