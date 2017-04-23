"""
"""
from __future__ import division, print_function
import numpy as np
import declarative

from ... import optics
from ... import signals
#from ... import system

class VCO(optics.OpticalCouplerBase):
    f_dict = None

    @declarative.dproperty
    def generate(self):
        val = signals.SignalGenerator(
            f_dict    = self.f_dict,
            amplitude = 1,
        )
        return val

    @declarative.dproperty
    def modulate(self):
        val = signals.Modulator()
        return val

    @declarative.dproperty
    def AM_SPEC(self):
        #FROM E1101019
        return signals.SRationalFilter(
            gain = 10**(-150/20.),
        )

    @declarative.dproperty
    def FM_SPEC(self):
        #FROM G1000703
        return signals.SRationalFilter(
            poles_r = (-1e-4, -1e-4),
            zeros_r = (-1e5, ),
            gain = 10**(-160/20.),
            gain_F_Hz = 1e5,
        )

    @declarative.dproperty
    def noise_FM(self):
        return signals.WhiteNoise(
            name_noise = 'VCO FM',
            sided = 'single',
            port = self.FM_SPEC.In,
        )

    @declarative.dproperty
    def noise_AM(self):
        return signals.WhiteNoise(
            name_noise = 'VCO AM',
            sided = 'single',
            port = self.AM_SPEC.In,
        )

    def __build__(self):
        super(VCO, self).__build__()
        self.generate.Out.bond(
            self.modulate.In,
        )
        self.modulate.Mod_amp.bond(self.AM_SPEC.Out)
        self.modulate.Mod_phase.bond(self.FM_SPEC.Out)
        self.Out = self.modulate.Out

