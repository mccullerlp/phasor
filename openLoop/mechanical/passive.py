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

    include_johnson_noise = True

    @decl.dproperty
    def johnson_noise(self):
        if self.include_johnson_noise and self.system.include_johnson_noise:
            return noise.DisplacementFluctuation(
                port = self.pm_A,
                dsq_Hz_by_freq = lambda F : 4 * self.symbols.temp_K * self.symbols.kB_J_K / (self.resistance_Ns_m * (2 * self.symbols.pi * F)**2),
                sided = 'one-sided',
            )
        return None


class SpringBase(object):
    @decl.dproperty
    def elasticity_N_m(self, val):
        return val

    @decl.dproperty
    def loss_angle_by_freq(self, val = None):
        if val is None:
            return None
        if not callable(val):
            return lambda F : val
        return val

    include_johnson_noise = True

    @decl.dproperty
    def johnson_noise(self):
        if self.loss_angle_by_freq is not None:
            if self.include_johnson_noise and self.system.include_johnson_noise:
                #this formula is the conversion of loss angle to equivalent viscous damping
                return noise.DisplacementFluctuation(
                    port = self.pm_A,
                    dsq_Hz_by_freq = lambda F : 4 * self.symbols.temp_K * self.symbols.kB_J_K * self.loss_angle_by_freq(F)  / ((2 * self.symbols.pi * F) * self.elasticity_N_m),
                    sided = 'one-sided',
                )
        return None

    def mobility_by_freq(self, F):
        #TODO
        if self.loss_angle_by_freq is not None:
            return self.elasticity_N_m * (1 + self.symbols.i * self.loss_angle_by_freq(F))
        else:
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
