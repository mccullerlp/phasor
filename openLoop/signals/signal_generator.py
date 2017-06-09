# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from openLoop.utilities.print import print
import declarative

import numpy as np

#from numbers import Number
#import warnings

from . import bases
from . import ports

from ..optics import standard_attrs as standard_attrs_opt


class SignalGenerator(bases.SignalElementBase):

    phase = standard_attrs_opt.generate_rotate(name = 'phase')
    _phase_default = ('phase_rad', 0)

    @declarative.dproperty
    def F(self, val = None):
        return val

    @declarative.dproperty
    def multiple(self, val = 1):
        return val

    @declarative.dproperty
    def f_dict(self, val = None):
        if val is None:
            val = {self.F : self.multiple}
        return val

    @declarative.dproperty
    def harmonic_gains(self, val = None):
        if val is None:
            val = dict()
        return val

    @declarative.dproperty
    def amplitude(self, val = 1):
        val = self.ooa_params.setdefault('amplitude', val)
        return val

    @declarative.dproperty
    def amplitudeC(self, val = None):
        val = self.ooa_params.setdefault('amplitudeC', val)
        if val is None:
            val = self.symbols.math.conjugate(self.amplitude)
        return val

    @declarative.dproperty
    def f_key(self):
        return ports.FrequencyKey(self.f_dict)

    def __build__(self):
        super(SignalGenerator, self).__build__()
        self.own.Out = ports.SignalOutPort(sname = 'Out')

        for Hidx, gain in list(self.harmonic_gains.items()):
            #just to check that it is a number
            Hidx + 1
            self.insert(
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

