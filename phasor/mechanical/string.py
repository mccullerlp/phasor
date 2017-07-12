"""
The zM_termination uses mechanical mobility in its calculations, folling the electrical/mechanical impedance analogy. ps_In this case using mobility/admittance rather than impedance to preserve the mechanical topology.

https://en.wikipedia.org/wiki/Impedance_analogy
https://en.wikipedia.org/wiki/Mobility_analogy

This implementation is more interested in measuring displacements rather than velocities so that the DC term may be
calculated. ps_In the standard mobility analogy, current becomes force and voltage becomes velocity and admittance [ps_In/V] is [kg/s]. This allows wave parameters to carry W as in the electrical case and the ports may be easily converted to vel and force. Displacement can be calculated as charge is, which requires knowing the DC force on all spring (capacitive) elements.

Instead this implementation uses a different convention, where voltage->displacement current->force. This means all of the wave parameters carry J and mobility is in units of [kg/s^2].

This does complicate johnson_noise, but the correspondance shouldn't be too bad

For convenience, multiple kinds of mobility are used, and formulas are modified. This is to prevent division by zero

mobility  [kg/s^2]
Vmobility [kg/s]
Amobility [kg]

and their inverses for reactance
"""
from __future__ import (division, print_function)

from ..base.bases import (
    SystemElementBase,
    NoiseBase,
    CouplerBase,
)

import declarative

from . import elements
from . import ports
from . import smatrix


class String(elements.MechanicalElementBase):
    """
    Basically a longitudinal wave string with. This should be designed to have certain characteristic mobility
    """
    @declarative.dproperty
    def length_m(self, val = 0):
        return val

    @declarative.dproperty
    def tension_N(self, N = 0):
        return N

    @declarative.dproperty
    def mass_density_kg_m(self, rho = 0):
        return rho

    @declarative.dproperty
    def Loss(self, val = 0):
        return val

    @declarative.dproperty
    def _mobility_Ns_m(self):
        return (self.tension_N * self.mass_density_kg_m)**.5

    @declarative.dproperty
    def _sound_velocity(self):
        return (self.tension_N / self.mass_density_kg_m)**.5

    @declarative.dproperty
    def ZconvA(self):
        return ZConverter(
            mobility_Ns_m = self._mobility_Ns_m,
        )

    @declarative.dproperty
    def ZconvB(self):
        return ZConverter(
            mobility_Ns_m = self._mobility_Ns_m,
        )

    @declarative.dproperty
    def cable(self):
        return elements.Cable(
            delay_s = self.length_m / self._sound_velocity,
            Loss    = self.Loss,
        )

    def __build__(self):
        self.ZconvA.pm_B.bond(self.cable.pm_A)
        self.cable.pm_B.bond(self.ZconvB.pm_B)

        self.pm_A = self.ZconvA.pm_A
        self.pm_B = self.ZconvB.pm_A
        return

    #Z12 = (Z2 - Z1) / (Z1 + Z2)
    #Z11 = 4 * (Z2 * Z1.conjugate()).real / |(Z1 + Z2)|**2

class ZConverter(smatrix.SMatrix2PortBase):
    #http://users.physics.harvard.edu/~schwartz/15cFiles/Lecture9-Impedance.pdf

    @declarative.dproperty
    def mobility_Ns_m(self, val):
        return val

    def S11_by_freq(self, F):
        Y1 = self.symbols.i2pi * F * 1/self.zM_termination + 1e-18
        Y2 = self.symbols.i2pi * F * self.mobility_Ns_m + 1e-18
        return (Y1 - Y2) / (Y1 + Y2)

    def S12_by_freq(self, F):
        Y1 = self.symbols.i2pi * F * 1/self.zM_termination + 1e-18
        Y2 = self.symbols.i2pi * F * self.mobility_Ns_m + 1e-18
        return 2 * Y1/(Y1 + Y2)

    def S21_by_freq(self, F):
        Y1 = self.symbols.i2pi * F * 1/self.zM_termination + 1e-18
        Y2 = self.symbols.i2pi * F * self.mobility_Ns_m + 1e-18
        return 2 * Y2/(Y1 + Y2)

    def S22_by_freq(self, F):
        Y1 = self.symbols.i2pi * F * 1/self.zM_termination + 1e-18
        Y2 = self.symbols.i2pi * F * self.mobility_Ns_m + 1e-18
        return (Y2 - Y1) / (Y1 + Y2)

