"""
"""
from __future__ import (division, print_function)

import declarative as decl
from . import ports
from . import elements
from . import opamps
from . import noise


class Op27(opamps.OpAmp):

    @decl.dproperty
    def V_noise(self):
        return noise.VoltageFluctuation(
            port = self.in_n,
            Vsq_Hz_by_freq = lambda F : (3e-9)**2 * abs(2.7j / F + 1)**2,
            sided = 'one-sided',
        )

    @decl.dproperty
    def I_noise(self):
        return noise.CurrentFluctuation(
            port = self.in_n,
            Isq_Hz_by_freq = lambda F : (.4e-12)**2 * abs(140j / F + 1)**2,
            sided = 'one-sided',
        )

    def gain_by_freq(self, F):
        #TODO check phase
        return 10**(6) * (1 / (1 - F/8j) ) * self.math.math.exp(- self.math.i2pi * F / (4 * 10e6))


class AD8675(opamps.OpAmp):

    @decl.dproperty
    def V_noise(self):
        return noise.VoltageFluctuation(
            port = self.in_n,
            Vsq_Hz_by_freq = lambda F : (2.8e-9)**2 * abs(1j / F + 1),
            sided = 'one-sided',
        )
        return None

    @decl.dproperty
    def I_noise(self):
        return noise.CurrentFluctuation(
            port = self.in_n,
            Isq_Hz_by_freq = lambda F : (.3e-12)**2,
            sided = 'one-sided',
        )

    def gain_by_freq(self, F):
        #TODO check phase
        return 10**(6) * (1 / (1 - F/10j) ) * self.math.math.exp(- self.math.i2pi * (30/360 + F / (360/60 * 30e6)))

class LMH6609(opamps.OpAmp):

    @decl.dproperty
    def V_noise(self):
        return noise.VoltageFluctuation(
            port = self.in_n,
            Vsq_Hz_by_freq = lambda F : (3.2e-9)**2 * abs(1e3j / F + 1),
            sided = 'one-sided',
        )
        return None

    @decl.dproperty
    def I_noise(self):
        return noise.CurrentFluctuation(
            port = self.in_n,
            Isq_Hz_by_freq = lambda F : (1.5e-12)**2 * abs(10e3j / F + 1),
            sided = 'one-sided',
        )

    def gain_by_freq(self, F):
        #TODO check phase
        return 10**(70/20) * (1 / (1 - F/100e3j) ) * self.math.math.exp(- self.math.i2pi * (50/360 + (F / (360/40 * 100e6))))
