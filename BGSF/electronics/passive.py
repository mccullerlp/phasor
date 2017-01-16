"""
"""
from __future__ import division
from builtins import object

import declarative as decl

from . import smatrix
from . import noise


class ResistorBase(object):
    @decl.dproperty
    def resistance_Ohms(self, val):
        return val

    def impedance_by_freq(self, F):
        return self.resistance_Ohms

    @decl.dproperty
    def johnson_noise(self):
        if self.system.include_johnson_noise:
            return noise.VoltageFluctuation(
                port = self.A,
                Vsq_Hz_by_freq = lambda F : 4 * self.resistance_Ohms * self.system.temp_K * self.system.kB_J_K,
                sided = 'one-sided',
            )
        return None


class CapacitorBase(object):
    @decl.dproperty
    def capacitance_Farads(self, val):
        return val

    def admittance_by_freq(self, F):
        return (2 * self.math.i * self.math.pi * F * self.capacitance_Farads)


class InductorBase(object):
    @decl.dproperty
    def inductance_Henries(self, val):
        return val

    def impedance_by_freq(self, F):
        return (2 * self.math.i * self.math.pi * F * self.inductance_Henries)


class TerminatorImpedance(smatrix.SMatrix1PortBase):
    def impedance_by_freq(self, F):
        raise NotImplementedError()

    def S11_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return ((Z - self.Z_termination) / (Z + self.Z_termination))


class TerminatorAdmittance(smatrix.SMatrix1PortBase):
    def admittance_by_freq(self, F):
        raise NotImplementedError()

    def S11_by_freq(self, F):
        Y = self.admittance_by_freq(F)
        return ((1 - Y * self.Z_termination) / (1 + Y * self.Z_termination))


class TerminatorResistor(ResistorBase, TerminatorImpedance):
    pass


class TerminatorCapacitor(CapacitorBase, TerminatorAdmittance):
    pass


class TerminatorInductor(InductorBase, TerminatorImpedance):
    pass


class SeriesImpedance(smatrix.SMatrix2PortBase):
    def impedance_by_freq(self, F):
        raise NotImplementedError()

    def S11_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return (Z / (Z + self.Z_termination * 2))

    def S12_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return ((2 * self.Z_termination) / (Z + self.Z_termination * 2))

    def S21_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return ((2 * self.Z_termination) / (Z + self.Z_termination * 2))

    def S22_by_freq(self, F):
        Z = self.impedance_by_freq(F)
        return (Z / (Z + self.Z_termination * 2))


class SeriesAdmittance(smatrix.SMatrix2PortBase):
    def admittance_by_freq(self, F):
        raise NotImplementedError()

    def S11_by_freq(self, F):
        Y = self.admittance_by_freq(F)
        return (1 / (1 + Y * self.Z_termination * 2))

    def S12_by_freq(self, F):
        Y = self.admittance_by_freq(F)
        return ((2 * Y * self.Z_termination) / (1 + Y * self.Z_termination * 2))

    def S21_by_freq(self, F):
        Y = self.admittance_by_freq(F)
        return ((2 * Y * self.Z_termination) / (1 + Y * self.Z_termination * 2))

    def S22_by_freq(self, F):
        Y = self.admittance_by_freq(F)
        return (1 / (1 + Y * self.Z_termination * 2))


class SeriesResistor(ResistorBase, SeriesImpedance):
    pass


class SeriesCapacitor(CapacitorBase, SeriesAdmittance):
    pass


class SeriesInductor(InductorBase, SeriesImpedance):
    pass


