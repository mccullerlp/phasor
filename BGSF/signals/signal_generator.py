# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

import numpy as np

#from numbers import Number
#import warnings

from ..math.key_matrix import (
    DictKey,
    FrequencyKey,
)

from ..base import (
    CouplerBase,
    Frequency,
    type_test,
)

from .bases import (
    SystemElementBase,
    OOA_ASSIGN,
)

from .ports import (
    #SignalPortHolderIn,
    SignalPortHolderOut,
    ClassicalFreqKey,
)


class SignalGenerator(CouplerBase, SystemElementBase):
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
        OOA_ASSIGN(self).F = F
        type_test(self.F, Frequency)
        OOA_ASSIGN(self).multiple = multiple
        OOA_ASSIGN(self).amplitude = amplitude
        if amplitudeC is None:
            OOA_ASSIGN(self).amplitudeC = np.conjugate(self.amplitude)
        else:
            OOA_ASSIGN(self).amplitudeC = amplitudeC

        self.classical_f_dict = {self.F : self.multiple}
        self.f_key = FrequencyKey(self.classical_f_dict)

        self.Out = SignalPortHolderOut(self, x = 'Out')

        self.harmonic_gains = harmonic_gains
        for Hidx, gain in list(self.harmonic_gains.items()):
            #just to check that it is a number
            Hidx + 1
            port = SignalPortHolderOut(self, x = 'OutH{0}'.format(Hidx))
            setattr(
                self,
                'OutH{0}'.format(Hidx),
                port
            )
        return

    def linked_elements(self):
        return (self.F,)

    def system_setup_ports_initial(self, system):
        system.coherent_sources_needed(
            self.Out.o,
            DictKey({ClassicalFreqKey: self.f_key}),
        )
        system.coherent_sources_needed(
            self.Out.o,
            DictKey({ClassicalFreqKey: -self.f_key}),
        )
        for Hidx, gain in list(self.harmonic_gains.items()):
            port = getattr(self, 'OutH{0}'.format(Hidx))
            system.coherent_sources_needed(
                port.o,
                DictKey({ClassicalFreqKey: Hidx * self.f_key}),
            )
            system.coherent_sources_needed(
                port.o,
                DictKey({ClassicalFreqKey: -Hidx * self.f_key}),
            )
        return

    def system_setup_ports(self, system):
        return

    def system_setup_coupling(self, system):
        system.coherent_sources_insert(
            self.Out.o,
            DictKey({ClassicalFreqKey: self.f_key}),
            self.amplitude,
        )
        system.coherent_sources_insert(
            self.Out.o,
            DictKey({ClassicalFreqKey: -self.f_key}),
            self.amplitudeC,
        )
        for Hidx, gain in list(self.harmonic_gains.items()):
            port = getattr(self, 'OutH{0}'.format(Hidx))
            system.coherent_sources_insert(
                port.o,
                DictKey({ClassicalFreqKey: Hidx * self.f_key}),
                gain,
            )
            system.coherent_sources_insert(
                port.o,
                DictKey({ClassicalFreqKey: -Hidx * self.f_key}),
                np.conjugate(gain),
            )

