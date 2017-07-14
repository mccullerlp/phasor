# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

#import declarative as decl
#from phasor import electronics

from .. import opamps


class Ope_27(opamps.ImperfectOpAmp):

    def V_spectrum_one_sided(self, F):
        return (3e-9)**2 * abs(2.7j / F + 1)

    def I_spectrum_one_sided(self, F):
        return (0.4e-12)**2 * abs(140j / F + 1)

    def gain_by_freq(self, F):
        return 10**(6) * (1 / (1 - F/8j) ) * self.symbols.math.exp(- self.symbols.i2pi * F / (4 * 10e6))


class Ope_827(opamps.ImperfectOpAmp):

    def V_spectrum_one_sided(self, F):
        return (3.8e-9)**2 * abs(((20/3.8)**2 - 1) * 1j / F + 1)

    def I_spectrum_one_sided(self, F):
        return (2.2e-15)**2 * abs(1e3j / F + 1)

    def gain_by_freq(self, F):
        return 10**(6) * (1 / (1 - F/20j) ) * self.symbols.math.exp(- self.symbols.i2pi * F / (360/90 * 100e6))


class Ope_209(opamps.ImperfectOpAmp):

    def V_spectrum_one_sided(self, F):
        return (2.2e-9)**2 * abs(((3.3/2.2)**2 - 1) * 1j / F + 1)

    def I_spectrum_one_sided(self, F):
        return (.5e-12)**2 * abs(((1.5/.5)**2 - 1) * 1j / F + 1)

    def gain_by_freq(self, F):
        return 10**(130/20) * (1 / (1 - F/10j) ) * self.symbols.math.exp(- self.symbols.i2pi * F / (360/90 * 100e6))


class TLE2027(opamps.ImperfectOpAmp):

    def V_spectrum_one_sided(self, F):
        return (2.5e-9)**2 * abs(((3.3/2.5)**2 - 1) * 10j / F + 1)

    def I_spectrum_one_sided(self, F):
        return (0.8e-12)**2 * abs(((10/.8)**2 - 1) * 10j / F + 1)

    def gain_by_freq(self, F):
        return 10**(6) * (1 / (1 - F/8j) ) * self.symbols.math.exp(- self.symbols.i2pi * F / (4 * 10e6))


class AD8675(opamps.ImperfectOpAmp):

    def V_spectrum_one_sided(self, F):
        return (2.8e-9)**2 * abs(((6.5/2.8)**2 - 1) * 1j / F + 1)

    def I_spectrum_one_sided(self, F):
        return (.3e-12)**2 * abs(10j / F + 1)

    def gain_by_freq(self, F):
        return 10**(6) * (1 / (1 - F/10j) ) * self.symbols.math.exp(- self.symbols.i2pi * (F / (360/90 * 30e6)))

class LMH6609(opamps.ImperfectOpAmp):

    def V_spectrum_one_sided(self, F):
        return (3.2e-9)**2 * abs(1e3j / F + 1)

    def I_spectrum_one_sided(self, F):
        return (1.5e-12)**2 * abs(10e3j / F + 1)

    def gain_by_freq(self, F):
        return 10**(70/20) * (1 / (1 - F/100e3j) ) * self.symbols.math.exp(- self.symbols.i2pi * ((F / (360/90 * 300e6))))


class AD743(opamps.ImperfectOpAmp):

    def V_spectrum_one_sided(self, F):
        return (2.9e-9)**2 # * abs(1e3j / F + 1)

    def I_spectrum_one_sided(self, F):
        return (6.9e-15)**2 # * abs(10e3j / F + 1)

    def gain_by_freq(self, F):
        return 10**(90/20) * (1 / (1 - F/100e3j) ) * self.symbols.math.exp(- self.symbols.i2pi * ((F / (360/90 * 20e6))))


class AD8429(opamps.ImperfectInAmp):
    def V_spectrum_one_sided(self, F):
        return (1e-9)**2

    def Vout_spectrum_one_sided(self, F):
        return (45e-9)**2

    def I_spectrum_one_sided(self, F):
        return (1.8e-12)**2 * abs(15**2 * 1j / F + 1)

    def gain_by_freq(self, F):
        raise NotImplementedError()


