"""
"""
from __future__ import division
#from builtins import object
import numpy as np

import declarative as decl

from . import smatrix
from . import elements
from . import noise

from .smatrix import (
    TerminatorOpen,
    TerminatorShorted,
)

class DamperBase(object):
    @decl.dproperty
    def resistance_Ns_m(self, val):
        return val

    def mobility_by_freq(self, F):
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

    def mobility_by_freq(self, F):
        #TODO
        return self.elasticity_N_m


class MassBase(object):
    @decl.dproperty
    def mass_kg(self, val):
        return val

    def mobility_by_freq(self, F):
        return (self.symbols.i2pi * F)**2 * self.mass_kg


class TerminatorMobility(smatrix.SMatrix1PortBase):
    def mobility_by_freq(self, F):
        raise NotImplementedError()

    def S11_by_freq(self, F):
        Y = self.mobility_by_freq(F)
        return ((1 - Y * self.zM_termination) / (1 + Y * self.zM_termination))


class TerminatorDamper(DamperBase, TerminatorMobility):
    pass


class TerminatorSpring(SpringBase, TerminatorMobility):
    pass


class Mass(MassBase, TerminatorMobility):
    pass


class SeriesMobility(smatrix.SMatrix2PortBase):
    def mobility_by_freq(self, F):
        raise NotImplementedError()

    def S11_by_freq(self, F):
        Y = self.mobility_by_freq(F)
        return (1 / (1 + Y * self.zM_termination * 2))

    def S12_by_freq(self, F):
        Y = self.mobility_by_freq(F)
        return ((2 * Y * self.zM_termination) / (1 + Y * self.zM_termination * 2))

    def S21_by_freq(self, F):
        Y = self.mobility_by_freq(F)
        return ((2 * Y * self.zM_termination) / (1 + Y * self.zM_termination * 2))

    def S22_by_freq(self, F):
        Y = self.mobility_by_freq(F)
        return (1 / (1 + Y * self.zM_termination * 2))


class SeriesDamper(DamperBase, SeriesMobility):
    pass


class SeriesSpring(SpringBase, SeriesMobility):
    pass


class SeriesMass(MassBase, SeriesMobility):
    """
    Also known as an "inerter"
    """
    pass
