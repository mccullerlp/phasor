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

    def __build__(self):
        super(VCO, self).__build__()
        self.generate.Out.bond(
            self.modulate.In,
        )
        self.Out = self.modulate.Out

