# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from BGSF.utilities.print import print

import numpy as np

#from numbers import Number
#import warnings

from . import bases
from . import ports

from ..optics import standard_attrs as standard_attrs_opt


class SignalGenerator(bases.SignalElementBase):

    phase = standard_attrs_opt.generate_rotate(name = 'phase')
    _phase_default = ('phase_rad', 0)

    def __init__(
        self,
        F,
        multiple = 1,
        amplitude  = 1,
        amplitudeC = None,
        harmonic_gains = {},
        **kwargs
    ):
        super(SignalGenerator, self).__init__(**kwargs)
        bases.OOA_ASSIGN(self).F = F
        bases.OOA_ASSIGN(self).multiple = multiple
        bases.OOA_ASSIGN(self).amplitude = amplitude
        if amplitudeC is None:
            bases.OOA_ASSIGN(self).amplitudeC = np.conjugate(self.amplitude)
        else:
            bases.OOA_ASSIGN(self).amplitudeC = amplitudeC

        self.classical_f_dict = {self.F : self.multiple}
        self.f_key = ports.FrequencyKey(self.classical_f_dict)

        self.my.Out = ports.SignalOutPort(sname = 'Out')

        self.harmonic_gains = harmonic_gains
        for Hidx, gain in list(self.harmonic_gains.items()):
            #just to check that it is a number
            Hidx + 1
            port = self.insert(
                ports.SignalOutPort(sname = 'OutH{0}'.format(Hidx)),
                'OutH{0}'.format(Hidx),
            )
        return

    def system_setup_ports_initial(self, system):
        system.coherent_sources_needed(
            self.Out.o,
            ports.DictKey({ports.ClassicalFreqKey: self.f_key}),
        )
        system.coherent_sources_needed(
            self.Out.o,
            ports.DictKey({ports.ClassicalFreqKey: -self.f_key}),
        )
        for Hidx, gain in list(self.harmonic_gains.items()):
            port = getattr(self, 'OutH{0}'.format(Hidx))
            system.coherent_sources_needed(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: Hidx * self.f_key}),
            )
            system.coherent_sources_needed(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: -Hidx * self.f_key}),
            )
        return

    def system_setup_ports(self, system):
        return

    def system_setup_coupling(self, system):
        if self.phase_rad.val is not 0:
            cplg = self.symbols.math.exp(self.symbols.i * self.phase_rad.val)
            cplgC = self.symbols.math.exp(-self.symbols.i * self.phase_rad.val)
        else:
            cplg = 1
            cplgC = 1
        system.coherent_sources_insert(
            self.Out.o,
            ports.DictKey({ports.ClassicalFreqKey: self.f_key}),
            cplg * self.amplitude,
        )
        system.coherent_sources_insert(
            self.Out.o,
            ports.DictKey({ports.ClassicalFreqKey: -self.f_key}),
            cplgC * self.amplitudeC,
        )
        for Hidx, gain in list(self.harmonic_gains.items()):
            port = getattr(self, 'OutH{0}'.format(Hidx))
            if self.phase_rad.val is not 0:
                cplg = self.symbols.math.exp(self.symbols.i * Hidx * self.phase_rad.val)
                cplgC = self.symbols.math.exp(-self.symbols.i * Hidx * self.phase_rad.val)
            else:
                cplg = 1
                cplgC = 1
            system.coherent_sources_insert(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: Hidx * self.f_key}),
                cplg * gain,
            )
            system.coherent_sources_insert(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: -Hidx * self.f_key}),
                cplgC * np.conjugate(gain),
            )

