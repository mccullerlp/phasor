# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from builtins import object
import numpy as np

import declarative as decl

from . import smatrix
from . import elements
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
                port = self.pe_A,
                Vsq_Hz_by_freq = lambda F : 4 * self.resistance_Ohms * self.symbols.temp_K * self.symbols.kB_J_K,
                sided = 'one-sided',
            )
        return None


class CapacitorBase(object):
    @decl.dproperty
    def capacitance_Farads(self, val):
        return val

    def admittance_by_freq(self, F):
        return (self.symbols.i2pi * F * self.capacitance_Farads)


class InductorBase(object):
    @decl.dproperty
    def inductance_Henries(self, val):
        return val

    @decl.dproperty
    def resistance_Ohms(self, val = 0):
        return val

    def impedance_by_freq(self, F):
        return (self.resistance_Ohms + self.symbols.i2pi * F * self.inductance_Henries)

    @decl.dproperty
    def johnson_noise(self):
        if self.system.include_johnson_noise and self.resistance_Ohms != 0:
            return noise.VoltageFluctuation(
                port = self.pe_A,
                Vsq_Hz_by_freq = lambda F : 4 * self.resistance_Ohms * self.symbols.temp_K * self.symbols.kB_J_K,
                sided = 'one-sided',
            )
        return None


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


class Z2x2To4Port(elements.Electrical4PortBase):
    def Z11_by_freq(self, F):
        return 0

    def Z12_by_freq(self, F):
        return 0

    def Z21_by_freq(self, F):
        return 0

    def Z22_by_freq(self, F):
        return 0

    @decl.mproperty
    def ports_electrical(self):
        return [
            self.pe_A,
            self.pe_B,
            self.pe_C,
            self.pe_D,
        ]

    def system_setup_ports(self, ports_algorithm):
        #TODO could reduce these with more information about used S-matrix elements
        for port1 in self.ports_electrical:
            for port2 in self.ports_electrical:
                for kfrom in ports_algorithm.port_update_get(port1.i):
                    ports_algorithm.port_coupling_needed(port2.o, kfrom)
                for kto in ports_algorithm.port_update_get(port2.o):
                    ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #assumes that all ports have the same setup/keys
        for kfrom in matrix_algorithm.port_set_get(self.pe_A.i):
            Y = 1/self.Z_termination
            freq = self.system.classical_frequency_extract(kfrom)
            Z11 = self.Z11_by_freq(freq)
            Z22 = self.Z22_by_freq(freq)
            Z12 = self.Z12_by_freq(freq)
            Z21 = self.Z21_by_freq(freq)
            det = (Z11 * Z22 - Z12 * Z12)
            tr = (Z11 + Z22)
            N11 = Y * Z11 * Z12 * Z21 * (Y * Z22 + 2)
            N12 = 2 * Y * Z12 * Z21 * Z22 - 4 * det
            N33 = Y * Z22 * Z12 * Z21 * (Y * Z11 + 2)
            N34 = 2 * Y * Z12 * Z21 * Z11 - 4 * det
            N13 = -2 * Y * Z11 * Z22 * Z21
            N31 = -2 * Y * Z11 * Z22 * Z12
            pe_D   = Y**2 * (Z11 * Z22 * Z12 * Z21) + 2 * Y * (Z12 * Z21) * tr - 4 * det
            for port1, port2, num in [
                (self.pe_A, self.pe_A, N11),
                (self.pe_A, self.pe_B, N12),
                (self.pe_B, self.pe_A, N12),
                (self.pe_B, self.pe_B, N11),
                (self.pe_C, self.pe_C, N33),
                (self.pe_C, self.pe_D, N34),
                (self.pe_D, self.pe_C, N34),
                (self.pe_D, self.pe_D, N33),
                (self.pe_A, self.pe_C, N13),
                (self.pe_A, self.pe_D, -N13),
                (self.pe_B, self.pe_C, -N13),
                (self.pe_B, self.pe_D, N13),
                (self.pe_C, self.pe_A, N31),
                (self.pe_C, self.pe_B, -N31),
                (self.pe_D, self.pe_A, -N31),
                (self.pe_D, self.pe_B, N31),
            ]:
                @np.vectorize
                def ddiv(num, pe_D):
                    if num != 0:
                        pgain = num / pe_D
                    else:
                        pgain = 0
                    return pgain
                pgain = ddiv(num, pe_D)
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    pgain,
                )


class Transformer(Z2x2To4Port):

    @decl.dproperty
    def L1_inductance_Henries(self, val):
        return val

    @decl.dproperty
    def L2_inductance_Henries(self, val):
        return val

    def transformer_k_by_freq(self, F_Hz):
        return 1

    @decl.dproperty
    def L1_resistance_Ohms(self, val = 0):
        return val

    @decl.dproperty
    def L1_johnson_noise(self):
        if self.system.include_johnson_noise and self.L1_resistance_Ohms != 0:
            return noise.VoltageFluctuation(
                port = self.pe_A,
                Vsq_Hz_by_freq = lambda F : 4 * self.L1_resistance_Ohms * self.symbols.temp_K * self.symbols.kB_J_K,
                sided = 'one-sided',
            )
        return None

    @decl.dproperty
    def L2_resistance_Ohms(self, val = 0):
        return val

    @decl.dproperty
    def L2_johnson_noise(self):
        if self.system.include_johnson_noise and self.L2_resistance_Ohms != 0:
            return noise.VoltageFluctuation(
                port = self.pe_C,
                Vsq_Hz_by_freq = lambda F : 4 * self.L2_resistance_Ohms * self.symbols.temp_K * self.symbols.kB_J_K,
                sided = 'one-sided',
            )
        return None

    def Z11_by_freq(self, F):
        return (self.L1_resistance_Ohms + self.symbols.i2pi * F * self.L1_inductance_Henries)

    def Z12_by_freq(self, F):
        M = self.transformer_k_by_freq(F) * (self.L1_inductance_Henries * self.L2_inductance_Henries)**.5
        return (self.symbols.i2pi * F * M)

    def Z21_by_freq(self, F):
        return self.Z12_by_freq(F)

    def Z22_by_freq(self, F):
        return (self.L2_resistance_Ohms + self.symbols.i2pi * F * self.L2_inductance_Henries)




