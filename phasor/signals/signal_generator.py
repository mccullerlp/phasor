# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from phasor.utilities.print import print
import declarative

import numpy as np

#from numbers import Number
#import warnings

from . import bases
from . import ports

from ..optics import standard_attrs as standard_attrs_opt

#from ..utilities.print import pprint


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
        val = self.ctree.setdefault('amplitude', val)
        return val

    @declarative.dproperty
    def amplitudeC(self, val = None):
        val = self.ctree.setdefault('amplitudeC', val)
        if val is None:
            val = self.symbols.math.conjugate(self.amplitude)
        return val

    @declarative.dproperty
    def f_key(self):
        return ports.FrequencyKey(self.f_dict)

    def __build__(self):
        super(SignalGenerator, self).__build__()
        self.own.ps_Out = ports.SignalOutPort(sname = 'ps_Out')

        for Hidx, gain in list(self.harmonic_gains.items()):
            #just to check that it is a number
            Hidx + 1

            self.insert(
                ports.SignalOutPort(sname = 'OutH{0}'.format(Hidx)),
                'OutH{0}'.format(Hidx),
            )
        return

    def system_setup_ports_initial(self, ports_algorithm):
        ports_algorithm.coherent_sources_needed(
            self.ps_Out.o,
            ports.DictKey({ports.ClassicalFreqKey: self.f_key}),
        )
        ports_algorithm.coherent_sources_needed(
            self.ps_Out.o,
            ports.DictKey({ports.ClassicalFreqKey: -self.f_key}),
        )
        for Hidx, gain in list(self.harmonic_gains.items()):
            port = getattr(self, 'OutH{0}'.format(Hidx))
            ports_algorithm.coherent_sources_needed(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: Hidx * self.f_key}),
            )
            ports_algorithm.coherent_sources_needed(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: -Hidx * self.f_key}),
            )
        return

    def system_setup_ports(self, ports_algorithm):
        return

    def system_setup_coupling(self, matrix_algorithm):
        if self.phase_rad.val is not 0:
            cplg = self.symbols.math.exp(self.symbols.i * self.phase_rad.val)
            cplgC = self.symbols.math.exp(-self.symbols.i * self.phase_rad.val)
        else:
            cplg = 1
            cplgC = 1
        matrix_algorithm.coherent_sources_insert(
            self.ps_Out.o,
            ports.DictKey({ports.ClassicalFreqKey: self.f_key}),
            cplg * self.amplitude,
        )
        matrix_algorithm.coherent_sources_insert(
            self.ps_Out.o,
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
            matrix_algorithm.coherent_sources_insert(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: Hidx * self.f_key}),
                cplg * gain,
            )
            matrix_algorithm.coherent_sources_insert(
                port.o,
                ports.DictKey({ports.ClassicalFreqKey: -Hidx * self.f_key}),
                cplgC * np.conjugate(gain),
            )

