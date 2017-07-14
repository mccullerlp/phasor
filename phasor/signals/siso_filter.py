# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from phasor.utilities.print import print
import declarative

import numpy as np

#from numbers import Number
#import warnings

from . import ports

from .bases import (
    SignalElementBase,
    PTREE_ASSIGN,
)


class TransferFunctionSISOBase(SignalElementBase):
    @declarative.dproperty
    def no_DC(self, val = False):
        val = self.ctree.setdefault('no_DC', val)
        return val

    @declarative.dproperty
    def F_cutoff(self, val = float('inf')):
        val = self.ctree.setdefault('F_cutoff', val)
        return val

    @declarative.dproperty
    def F_cutoff_low(self, val = 0):
        #this is INCLUSIVE
        val = self.ctree.setdefault('F_cutoff_low', val)
        return val

    @declarative.dproperty
    def ps_In(self):
        return ports.SignalInPort(pchain = lambda : self.ps_Out)

    @declarative.dproperty
    def ps_Out(self):
        return ports.SignalOutPort(pchain = lambda : self.ps_In)

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
        for kfrom in ports_algorithm.port_update_get(self.ps_In.i):
            if abs(self.system.classical_frequency_extract_center(kfrom[ports.ClassicalFreqKey])) > self.F_cutoff:
                continue
            if abs(self.system.classical_frequency_extract_center(kfrom[ports.ClassicalFreqKey])) < self.F_cutoff_low:
                continue
            if self.no_DC and self.system.classical_frequency_extract_center(kfrom[ports.ClassicalFreqKey]) == 0:
                continue
            ports_algorithm.port_coupling_needed(self.ps_Out.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.ps_Out.o):
            if abs(self.system.classical_frequency_extract_center(kto[ports.ClassicalFreqKey])) > self.F_cutoff:
                continue
            if abs(self.system.classical_frequency_extract_center(kto[ports.ClassicalFreqKey])) < self.F_cutoff_low:
                continue
            if self.no_DC and self.system.classical_frequency_extract_center(kto[ports.ClassicalFreqKey]) == 0:
                continue
            ports_algorithm.port_coupling_needed(self.ps_In.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.ps_In.i):
            F_center_Hz = self.system.classical_frequency_extract_center(kfrom[ports.ClassicalFreqKey])
            if abs(F_center_Hz) > self.F_cutoff:
                continue
            if abs(F_center_Hz) < self.F_cutoff_low:
                continue
            if self.no_DC and F_center_Hz == 0:
                continue
            freq = self.system.classical_frequency_extract(kfrom)
            pgain = self.filter_func_run(freq)
            matrix_algorithm.port_coupling_insert(
                self.ps_In.i,
                kfrom,
                self.ps_Out.o,
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
        PTREE_ASSIGN(self).filter = filter
        return

    def filter_func(self, freq):
        freq = np.asarray(freq)
        rval = self.filter(freq)
        return rval


class Integrator(TransferFunctionSISOBase):
    def filter_func(self, freq):
        freq = np.asarray(freq)
        return 1/(-1j * freq)

    @declarative.dproperty
    def no_DC(self, val = True):
        val = self.ctree.setdefault('no_DC', val)
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
        PTREE_ASSIGN(self).mass_kg   = mass_kg
        PTREE_ASSIGN(self).center_Hz = center_Hz

        if FWHM_Hz is not None:
            PTREE_ASSIGN(self).FWHM_Hz = FWHM_Hz

        if q_factor is not None:
            PTREE_ASSIGN(self).q_factor = q_factor
            _FWHM = self.center_Hz / self.q_factor
            PTREE_ASSIGN(self).FWHM_Hz = _FWHM
        elif FWHM_Hz is not None:
            q_factor = self.center_Hz / self.FWHM_Hz
            PTREE_ASSIGN(self).q_factor = q_factor
        else:
            raise RuntimeError("Must specify at least q_factor or FWHM_Hz")

        _FWHM = self.center_Hz / self.q_factor
        assert(((_FWHM / self.FWHM_Hz) - 1) < 1e-8)

        return

    def filter_func(self, freq):
        gain = 1/(self.mass_kg * (2 * np.pi)**2)
        xfer = gain / (-freq**2 + self.symbols.i * self.FWHM_Hz * freq + self.center_Hz**2)
        return xfer


class TFACArray(SignalElementBase):
    @declarative.dproperty
    def ps_In(self):
        return ports.SignalInPort(pchain = lambda : self.ps_Out)

    @declarative.dproperty
    def ps_Out(self):
        return ports.SignalOutPort(pchain = lambda : self.ps_In)

    @declarative.dproperty
    def gain_array(self, arr):
        return arr

    @declarative.dproperty
    def gain_arrayC(self, arr = None):
        if arr is None:
            arr = self.gain_array.conjugate()
        return arr

    @declarative.dproperty
    def F_AC(self, val = None):
        #TODO make this able to handle regeneration
        if val is None:
            val = self.system.environment.F_AC
        return val

    def check_F_AC_only(self, kfrom):
        ffrom = kfrom[ports.ClassicalFreqKey]
        AC_level = 0
        proceed = True
        for Fobj, Fnum in ffrom.F_dict.items():
            if Fobj is self.F_AC:
                AC_level = Fnum
            else:
                if Fnum != 0:
                    proceed = False
        if AC_level not in [1, -1]:
            proceed = False
        return proceed

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.ps_In.i):
            if not self.check_F_AC_only(kfrom):
                continue

            ports_algorithm.port_coupling_needed(self.ps_Out.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.ps_Out.o):
            if not self.check_F_AC_only(kto):
                continue
            ports_algorithm.port_coupling_needed(self.ps_In.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.ps_In.i):
            if not self.check_F_AC_only(kfrom):
                continue

            ffrom = kfrom[ports.ClassicalFreqKey]
            count = ffrom.F_dict[self.F_AC]
            if count > 0:
                pgain = self.gain_array
            elif count < 0:
                pgain = self.gain_arrayC

            matrix_algorithm.port_coupling_insert(
                self.ps_In.i,
                kfrom,
                self.ps_Out.o,
                kfrom,
                pgain,
            )
        return

