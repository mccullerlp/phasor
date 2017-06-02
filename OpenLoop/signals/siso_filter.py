# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from OpenLoop.utilities.print import print
import declarative

import numpy as np

#from numbers import Number
#import warnings

from . import ports

from .bases import (
    SignalElementBase,
    OOA_ASSIGN,
)


class TransferFunctionSISOBase(SignalElementBase):
    @declarative.dproperty
    def no_DC(self, val = False):
        val = self.ooa_params.setdefault('no_DC', val)
        return val

    @declarative.dproperty
    def F_cutoff(self, val = float('inf')):
        val = self.ooa_params.setdefault('F_cutoff', val)
        return val

    @declarative.dproperty
    def In(self):
        return ports.SignalInPort(pchain = lambda : self.Out)

    @declarative.dproperty
    def Out(self):
        return ports.SignalOutPort(pchain = lambda : self.In)

    def filter_func(self, freq):
        return 0

    def filter_func_run(self, freq):
        xfer = self.filter_func(freq)
        if self.no_DC:
            xfer = np.asarray(xfer)
            freq = np.asarray(freq)
            zfreq = (freq == 0)
            xfer[zfreq] = 0
        return xfer

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.In.i):
            if abs(self.system.classical_frequency_extract_center(kfrom[ports.ClassicalFreqKey])) > self.F_cutoff:
                continue
            if self.no_DC and self.system.classical_frequency_extract_center(kfrom[ports.ClassicalFreqKey]) == 0:
                continue
            ports_algorithm.port_coupling_needed(self.Out.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.Out.o):
            if abs(self.system.classical_frequency_extract_center(kto[ports.ClassicalFreqKey])) > self.F_cutoff:
                continue
            if self.no_DC and self.system.classical_frequency_extract_center(kto[ports.ClassicalFreqKey]) == 0:
                continue
            ports_algorithm.port_coupling_needed(self.In.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.In.i):
            if abs(self.system.classical_frequency_extract_center(kfrom[ports.ClassicalFreqKey])) > self.F_cutoff:
                continue
            if self.no_DC and self.system.classical_frequency_extract_center(kfrom[ports.ClassicalFreqKey]) == 0:
                continue
            freq = self.system.classical_frequency_extract(kfrom)
            pgain = self.filter_func_run(freq)
            matrix_algorithm.port_coupling_insert(
                self.In.i,
                kfrom,
                self.Out.o,
                kfrom,
                pgain,
            )
        return


class TransferFunctionSISO(TransferFunctionSISOBase):
    def __init__(
            self,
            filter_func,
            **kwargs
    ):
        super(TransferFunctionSISO, self).__init__(**kwargs)
        OOA_ASSIGN(self).filter = filter
        return

    def filter_func(self, freq):
        freq = np.asarray(freq)
        rval = self.filter(freq)
        return rval


class Integrator(TransferFunctionSISOBase):
    def filter_func(self, freq):
        freq = np.asarray(freq)
        return 1/freq

    @declarative.dproperty
    def no_DC(self, val = True):
        val = self.ooa_params.setdefault('no_DC', val)
        return val


class Gain(TransferFunctionSISOBase):
    def gain(self, val = 1):
        return val

    def filter_func(self, freq):
        return self.gain


class TransferFunctionSISOMechSingleResonance(TransferFunctionSISOBase):
    def __init__(
            self,
            mass_kg,
            center_Hz,
            q_factor = None,
            FWHM_Hz     = None,
            **kwargs
    ):
        super(TransferFunctionSISOMechSingleResonance, self).__init__(**kwargs)
        OOA_ASSIGN(self).mass_kg   = mass_kg
        OOA_ASSIGN(self).center_Hz = center_Hz

        if FWHM_Hz is not None:
            OOA_ASSIGN(self).FWHM_Hz = FWHM_Hz

        if q_factor is not None:
            OOA_ASSIGN(self).q_factor = q_factor
            _FWHM = self.center_Hz / self.q_factor
            OOA_ASSIGN(self).FWHM_Hz = _FWHM
        elif FWHM_Hz is not None:
            q_factor = self.center_Hz / self.FWHM_Hz
            OOA_ASSIGN(self).q_factor = q_factor
        else:
            raise RuntimeError("Must specify at least q_factor or FWHM_Hz")

        _FWHM = self.center_Hz / self.q_factor
        assert(((_FWHM / self.FWHM_Hz) - 1) < 1e-8)

        return

    def filter_func(self, freq):
        gain = 1/(self.mass_kg * (2 * np.pi)**2)
        xfer = gain / (-freq**2 + self.symbols.i * self.FWHM_Hz * freq + self.center_Hz**2)
        return xfer

