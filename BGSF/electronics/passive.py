"""
"""
from __future__ import division
from builtins import object

import declarative as decl
#import numpy as np
#import warnings

#from . import ports
#from . import elements
from . import smatrix


class ResistorBase(object):
    @decl.dproperty
    def resistance_Ohms(self, val):
        return val

    def impedance_by_freq(self, F):
        return self.resistance_Ohms


class CapacitorBase(object):
    @decl.dproperty
    def capacitance_Farads(self, val):
        return val

    def impedance_by_freq(self, F):
        return (1 / (2 * self.math.i * self.math.pi * F * self.capacitance_Farads))


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


class TerminatorResistor(ResistorBase, TerminatorImpedance):
    pass


class TerminatorCapacitor(CapacitorBase, TerminatorImpedance):
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


class SeriesResistor(ResistorBase, SeriesImpedance):
    pass


class SeriesCapacitor(CapacitorBase, SeriesImpedance):
    pass


class SeriesInductor(InductorBase, SeriesImpedance):
    pass


