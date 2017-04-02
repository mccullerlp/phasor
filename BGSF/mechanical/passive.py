"""
"""
from __future__ import division
#from builtins import object
import numpy as np

import declarative as decl

from . import smatrix
from . import elements
from . import noise


class DamperBase(object):
    @decl.dproperty
    def resistance_Ns_m(self, val):
        return val

    def impedance_by_freq(self, F):
        return self.symbols.i2pi * F * self.resistance_Ns_m

    @decl.dproperty
    def johnson_noise(self):
        if self.system.include_johnson_noise:
            return noise.ForceFluctuation(
                port = self.A,
                Fsq_Hz_by_freq = lambda F : 4 * self.resistance_Ns_m * self.symbols.temp_K * self.symbols.kB_J_K,
                sided = 'one-sided',
            )
        return None


class SpringBase(object):
    @decl.dproperty
    def elasticity_N_m(self, val):
        return val

    def impedance_by_freq(self, F):
        #TODO
        return self.elasticity_N_m


class MassBase(object):
    @decl.dproperty
    def mass_kg(self, val):
        return val

    def impedance_by_freq(self, F):
        return (self.symbols.i2pi * F)**2 * self.mass_kg


class TerminatorImpedance(smatrix.SMatrix1PortBase):
    def impedance_by_freq(self, F):
        raise NotImplementedError()

    def S11_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return ((Z - self.zM_termination) / (Z + self.zM_termination))


class TerminatorDamper(DamperBase, TerminatorImpedance):
    pass


class TerminatorSpring(SpringBase, TerminatorImpedance):
    pass


class Mass(MassBase, TerminatorImpedance):
    pass


class SeriesImpedance(smatrix.SMatrix2PortBase):
    def impedance_by_freq(self, F):
        raise NotImplementedError()

    def S11_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return (Z / (Z + self.zM_termination * 2))

    def S12_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return ((2 * self.zM_termination) / (Z + self.zM_termination * 2))

    def S21_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return ((2 * self.zM_termination) / (Z + self.zM_termination * 2))

    def S22_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return (Z / (Z + self.zM_termination * 2))


class SeriesDamper(DamperBase, SeriesImpedance):
    pass


class SeriesSpring(SpringBase, SeriesImpedance):
    pass


class SeriesMass(MassBase, SeriesImpedance):
    """
    Also known as an "inerter"
    """
    pass
