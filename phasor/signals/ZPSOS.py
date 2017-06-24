# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from phasor.utilities.print import print
import declarative
import collections

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

def ctree_root_grab(ctree, root_key, defaults):
        #only used if the ooa params are completely missing
        ctree_roots = ctree[root_key]
        if not ctree_roots:
            if isinstance(defaults, collections.Mapping):
                roots = []
                for idx, root in defaults.items():
                    ctree_roots[str(idx)] = root
                    roots.append(root)
                return tuple(roots)

            else:
                for idx, root in enumerate(defaults):
                    ctree_roots[str(idx)] = root
                return tuple(defaults)
        else:
            rlist = []
            for pkey, root in ctree_roots.items():
                rlist.append(root)
        return tuple(rlist)


class SZPCascade(siso_filter.TransferFunctionSISOBase):

    @declarative.dproperty
    def poles_r(self, plist = []):
        #only used if the ooa params are completely missing
        poles = ctree_root_grab(self.ctree, 'poles_r', plist)
        for root in poles:
            assert(root.imag == 0)
        return poles

    @declarative.dproperty
    def zeros_r(self, zlist = []):
        #only used if the ooa params are completely missing
        zeros = ctree_root_grab(self.ctree, 'zeros_r', zlist)
        for root in zeros:
            assert(root.imag == 0)
        #print(self.ctree['zeros_r'])
        return zeros

    @declarative.dproperty
    def poles_c(self, plist = []):
        #only used if the ooa params are completely missing
        poles = ctree_root_grab(self.ctree, 'poles_c', plist)
        #print("POLES_C: ", poles)
        return poles

    @declarative.dproperty
    def zeros_c(self, zlist = []):
        #only used if the ooa params are completely missing
        zeros = ctree_root_grab(self.ctree, 'zeros_c', zlist)
        return zeros

    @declarative.dproperty
    def preserve_plane(self, val = True):
        val = self.ctree.setdefault('preserve_plane', val)
        return val

    @declarative.mproperty
    def fitter_data(self):
        return self.fitter_data_()

    def fitter_data_(self):
        """
        Combination of all subordinate fitter parameters to fully fit this function
        """
        fitters = []

        def add_fit(root_key, sub_key, usecomplex = False):
            root = self.root
            current = self.parent
            names = [root_key, self.name_child]
            while current is not root:
                names.append(current.name_child)
                current = current.parent
            fitter_parameter = tuple(names[::-1])

            #TODO: provide real units rather than the str version
            def fitter_inject(ooa, value, ivalue):
                for key in fitter_parameter:
                    ooa = ooa[key]
                ooa[sub_key]   = value

            def fitter_reinject(ooa, value):
                for key in fitter_parameter:
                    ooa = ooa[key]
                ooa[sub_key]   = value

            def fitter_initial(ooa):
                for key in fitter_parameter:
                    ooa = ooa[key]
                val = ooa[sub_key]
                return val

            if self.preserve_plane:
                #get the initial value and create the constraint for it
                if fitter_initial(self.root.ctree).real <= 0:
                    lower_bound = -float('inf')
                    upper_bound = .0001
                else:
                    lower_bound = 0
                    upper_bound = float('inf')
            else:
                lower_bound = -float('inf')
                upper_bound = float('inf')
            #TODO: fix name vs. name_global
            return declarative.FrozenBunch(
                usecomplex    = usecomplex,
                parameter_key = fitter_parameter + (sub_key, ),
                units         = 'Hz',
                name          = self.name_system + '.{0}.{1}'.format(root_key, sub_key),
                name_global   = self.name_system + '.{0}.{1}'.format(root_key, sub_key),
                initial       = fitter_initial,
                inject        = fitter_inject,
                reinject      = fitter_reinject,
                lower_bound   = lower_bound,
                upper_bound   = upper_bound,
            )
        for pname, pval in self.ctree['zeros_r'].items():
            fitters.append(
                add_fit('zeros_r', pname)
            )
        for pname, pval in self.ctree['poles_r'].items():
            fitters.append(
                add_fit('poles_r', pname)
            )
        for pname, pval in self.ctree['zeros_c'].items():
            fitters.append(
                add_fit('zeros_c', pname, usecomplex = True)
            )
        for pname, pval in self.ctree['poles_c'].items():
            fitters.append(
                add_fit('poles_c', pname, usecomplex = True)
            )
        return fitters

    def filter_func(self, freq):
        def root_xfer(rlist):
            if rlist:
                xfer = (1 - 1j * freq/rlist[0])
                for root in rlist[1:]:
                    xfer *= (1 - 1j * freq/root)
            else:
                xfer = 1
            return xfer

        def root_xfer2(rlist):
            if rlist:
                xfer = (1 - freq/rlist[0].conjugate() * 1j) * (1 - freq/rlist[0] * 1j)
                for root in rlist[1:]:
                    xfer *= (1 - freq/root.conjugate() * 1j) * (1 - freq/root * 1j)
            else:
                xfer = 1
            return xfer
        return (root_xfer(self.zeros_r) * root_xfer2(self.zeros_c)) / (root_xfer(self.poles_r) * root_xfer2(self.poles_c))


class SBQFCascade(siso_filter.TransferFunctionSISOBase):
    @declarative.dproperty
    def poles(self, plist):
        return plist

    @declarative.dproperty
    def zeros(self, zlist):
        return zlist

    @declarative.dproperty
    def N_poles(self):
        val = self.ctree.setdefault('N_poles', len(self.poles))
        return val

    @declarative.dproperty
    def N_zeros(self):
        val = self.ctree.setdefault('N_zeros', len(self.poles))
        return val

    @declarative.mproperty
    def fitter_data(self):
        """
        Combination of all subordinate fitter parameters to fully fit this function
        """
        fitters = []
        return fitters


class SRationalFilter(SZPCascade):
    delay_default = ('delay_s', 0)
    @declarative.dproperty_adv_group
    def delay(desc):
        name = desc.__name__
        return generate_refval_attribute(
            desc,
            ubunch = units.time_small,
            stems = [name, ],
            ctree_name = name,
            preferred_attr = name,
            default_attr = '{0}_default'.format(name),
            prototypes = ['full', 'base'],
        )

    @declarative.dproperty_adv
    def gain(desc):
        return unitless_refval_attribute(desc)

    @declarative.dproperty
    def gain_F_Hz(desc, val = 0):
            return val

    def filter_func(self, freq):
        #print("FREQ: ", self, freq)
        pre = self.gain.val
        if self.delay_s.val is not None:
            pre = pre * self.symbols.math.exp(-self.symbols.i2pi * freq * self.delay_s.val)
        xfer = super(SRationalFilter, self).filter_func(freq) * pre

        if self.gain_F_Hz != 0:
            xfer = xfer / abs(super(SRationalFilter, self).filter_func(self.gain_F_Hz))

        return xfer

    @declarative.mproperty
    def fitter_data(self):
        """
        Combination of all subordinate fitter parameters to fully fit this function
        """
        fitters = self.fitter_data_()
        fitters.extend(self.delay.fitter_data)
        fitters.extend(self.gain.fitter_data)
        return fitters

