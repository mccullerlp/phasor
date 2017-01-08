# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

import numpy as np

#from numbers import Number
#import warnings

from ..base import (
    CouplerBase,
)

from .ports import (
    SignalPortHolderIn,
    SignalPortHolderOut,
)

from .bases import (
    SystemElementBase,
    OOA_ASSIGN,
)


class TransferFunctionSISOBase(CouplerBase, SystemElementBase):
    def __init__(
            self,
            max_freq         = None,
            no_DC            = False,
            fluct_diss_noise = False,
            **kwargs
    ):
        super(TransferFunctionSISOBase, self).__init__(**kwargs)
        OOA_ASSIGN(self).max_freq = max_freq
        OOA_ASSIGN(self).no_DC       = no_DC

        self.In  = SignalPortHolderIn(self, x = 'In')
        self.Out = SignalPortHolderOut(self, x = 'Out')

        return

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
            if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                continue
            ports_algorithm.port_coupling_needed(self.Out.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.Out.o):
            if self.system.classical_frequency_test_max(kto, self.max_freq):
                continue
            ports_algorithm.port_coupling_needed(self.In.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.In.i):
            if self.system.classical_frequency_test_max(kfrom, self.max_freq):
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
        xfer = gain / (-freq**2 + self.system.i * self.FWHM_Hz * freq + self.center_Hz**2)
        return xfer

