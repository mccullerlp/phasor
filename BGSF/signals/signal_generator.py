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


class SignalGenerator(bases.CouplerBase, bases.SystemElementBase):
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
        system.coherent_sources_insert(
            self.Out.o,
            ports.DictKey({ports.ClassicalFreqKey: self.f_key}),
            self.amplitude,
        )
        system.coherent_sources_insert(
            self.Out.o,
            ports.DictKey({ports.ClassicalFreqKey: -self.f_key}),
            self.amplitudeC,
        )
        for Hidx, gain in list(self.harmonic_gains.items()):
            port = getattr(self, 'OutH{0}'.format(Hidx))
            system.coherent_sources_insert(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: Hidx * self.f_key}),
                gain,
            )
            system.coherent_sources_insert(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: -Hidx * self.f_key}),
                np.conjugate(gain),
            )

