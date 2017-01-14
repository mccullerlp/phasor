"""
"""
from __future__ import division
from builtins import object

import declarative as decl
#import numpy as np
#import warnings

from YALL.natsci.optics.dictionary_keys import (
    DictKey,
)

from YALL.natsci.optics.keyed_linear_algebra import (
    ForewardDictMatrix,
)

from collections import namedtuple




class ElectricalElementBase(object):
    pass


ElectricalWireBase = namedtuple('ElectricalWireBase', ('element', 'port_name'))


class Electrical1PortBase(ElectricalElementBase):
    @decl.mproperty
    def A(self):
        return ElectricalPort(self, 'A')


class Electrical2PortBase(ElectricalElementBase):
    @decl.mproperty
    def A(self):
        return ElectricalPort(self, 'A')

    @decl.mproperty
    def B(self):
        return ElectricalPort(self, 'B')


class SMatrix1PortBase(Electrical1PortBase):
    Z_termination = 50

    def S11_by_freq(self, F, system):
        raise NotImplementedError()

    def system_setup_coupling(self, system):
        couplings = ForewardDictMatrix()
        couplings[self.A.i, self.A.o] = 1

        F_matrix = ForewardDictMatrix()
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            F_matrix[df_key, df_key] = self.S11_by_freq(f_key.frequency(), system)

        couplings.tensor_product(
            F_matrix,
            validate = system.dk_validate,
            into = system.coupling_matrix,
        )
        return


class SMatrix2PortBase(Electrical2PortBase):
    Z_termination = 50

    def S11_by_freq(self, F, system):
        return 0

    def S12_by_freq(self, F, system):
        return 0

    def S21_by_freq(self, F, system):
        return 0

    def S22_by_freq(self, F, system):
        return 0

    def system_setup_coupling(self, system):
        matrix = ForewardDictMatrix()
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            matrix[
                df_key | self.A.i,
                df_key | self.A.o
            ] = self.S11_by_freq(f_key.frequency(), system)
            matrix[
                df_key | self.A.i,
                df_key | self.B.o
            ] = self.S12_by_freq(f_key.frequency(), system)
            matrix[
                df_key | self.B.i,
                df_key | self.A.o
            ] = self.S21_by_freq(f_key.frequency(), system)
            matrix[
                df_key | self.B.i,
                df_key | self.B.o
            ] = self.S22_by_freq(f_key.frequency(), system)

        matrix.insert(
            into = system.coupling_matrix,
            validate = system.dk_validate,
        )
        return


class VoltageSource(SMatrix1PortBase):
    def S11_by_freq(self, F, system):
        return -1

    @decl.mproperty
    def V(self):
        return DictKey(virtual = self)

    def system_setup_coupling(self, system):
        super(VoltageSource, self).system_setup_coupling(system)
        matrix = ForewardDictMatrix()
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            matrix[
                df_key | self.V,
                df_key | self.A.o
            ] = 1

        matrix.insert(
            into = system.coupling_matrix,
        )
        return


class CurrentSource(SMatrix1PortBase):
    def S11_by_freq(self, F, system):
        return 1

    @decl.mproperty
    def I(self):
        return DictKey(virtual = self)

    def system_setup_coupling(self, system):
        super(CurrentSource, self).system_setup_coupling(system)
        matrix = ForewardDictMatrix()
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            matrix[
                df_key | self.I,
                df_key | self.A.o
            ] = system.Z_termination

        matrix.insert(
            into = system.coupling_matrix,
        )
        return


class VoltageSourceBalanced(SMatrix2PortBase):
    def S11_by_freq(self, F, system):
        return 0

    def S12_by_freq(self, F, system):
        return 1

    def S21_by_freq(self, F, system):
        return 1

    def S22_by_freq(self, F, system):
        return 0

    @decl.mproperty
    def V(self):
        return DictKey(virtual = self, val = 'voltage')

    @decl.mproperty
    def I(self):
        return DictKey(virtual = self, val = 'current')

    def system_setup_coupling(self, system):
        super(VoltageSourceBalanced, self).system_setup_coupling(system)
        matrix = ForewardDictMatrix()
        _2 = system.number(2)
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            matrix[
                df_key | self.V,
                df_key | self.A.o
            ] = 1 / _2
            matrix[
                df_key | self.V,
                df_key | self.B.o
            ] = -1 / _2
            matrix[
                df_key | self.I,
                df_key | self.A.o
            ] = system.Z_termination / _2
            matrix[
                df_key | self.I,
                df_key | self.B.o
            ] = system.Z_termination / _2

        matrix.insert(
            into = system.coupling_matrix,
        )
        return


class CurrentSourceBalanced(SMatrix2PortBase):
    def S11_by_freq(self, F, system):
        return 1

    def S12_by_freq(self, F, system):
        return 0

    def S21_by_freq(self, F, system):
        return 0

    def S22_by_freq(self, F, system):
        return 1

    @decl.mproperty
    def I(self):
        return DictKey(virtual = self)

    def system_setup_coupling(self, system):
        super(CurrentSourceBalanced, self).system_setup_coupling(system)
        matrix = ForewardDictMatrix()
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            matrix[
                df_key | self.I,
                df_key | self.A.o
            ] = system.Z_termination
            matrix[
                df_key | self.I,
                df_key | self.B.o
            ] = -system.Z_termination

        matrix.insert(
            into = system.coupling_matrix,
        )
        return


class TerminatorMatched(SMatrix1PortBase):
    def S11_by_freq(self, F, system):
        return 0


class TerminatorOpen(SMatrix1PortBase):
    def S11_by_freq(self, F, system):
        return 1


class TerminatorShorted(SMatrix1PortBase):
    def S11_by_freq(self, F, system):
        return -1


class Connection(ElectricalElementBase):
    def __init__(
        self,
        *port_list,
        **kwargs
    ):
        super(Connection, self).__init__(**kwargs)
        self.port_list = tuple(port_list)
        return

    def system_setup_coupling(self, system):
        _2 = system.number(2)
        N_wires = system.number(len(self.port_list))
        couplings = ForewardDictMatrix()
        for portA in self.port_list:
            for portB in self.port_list:
                if portA is portB:
                    couplings[portA.o, portB.i] = (_2 - N_wires) / N_wires
                else:
                    couplings[portA.o, portB.i] = (_2 / N_wires)

        delay_matrix = ForewardDictMatrix()
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            delay_matrix[df_key, df_key] = 1

        couplings.tensor_product(
            delay_matrix,
            validate = system.dk_validate,
            into = system.coupling_matrix,
        )
        return


class Cable(ElectricalElementBase):
    def __init__(
        self,
        length_ns,
        **kwargs
    ):
        super(Connection, self).__init__(**kwargs)
        self.length_ns = length_ns
        return

    def phase_advance(self, system, F):
        return system.math.exp(-2 * system.i * system.pi * F * self.length_ns)

    @decl.mproperty
    def A(self):
        return ElectricalPort(self, 'A')

    @decl.mproperty
    def B(self):
        return ElectricalPort(self, 'B')

    def system_setup_coupling(self, system):
        couplings = ForewardDictMatrix()
        couplings[self.B.i, self.A.i] = 1
        couplings[self.A.o, self.B.o] = 1

        delay_matrix = ForewardDictMatrix()
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            delay_matrix[df_key, df_key] = (
                self.phase_advance(system, f_key.frequency())
            )

        couplings.tensor_product(
            delay_matrix,
            validate = system.dk_validate,
            into = system.coupling_matrix,
        )
        return


class ResistorBase(object):
    def __init__(self, resistance_Ohms, **kwargs):
        super(ResistorBase, self).__init__(**kwargs)
        self.resistance_Ohms = resistance_Ohms

    def impedance_by_freq(self, F, system):
        return self.resistance_Ohms


class CapacitorBase(object):
    def __init__(self, capacitance_Farads, **kwargs):
        super(CapacitorBase, self).__init__(**kwargs)
        self.capacitance_Farads = capacitance_Farads

    def impedance_by_freq(self, F, system):
        return (1 / (2 * system.i * system.pi * F * self.capacitance_Farads))


class InductorBase(object):
    def __init__(self, inductance_Henries, **kwargs):
        super(InductorBase, self).__init__(**kwargs)
        self.inductance_Henries = inductance_Henries

    def impedance_by_freq(self, F, system):
        return (2 * system.i * system.pi * F * self.inductance_Henries)


class TerminatorImpedance(SMatrix1PortBase):
    def impedance_by_freq(self, F, system):
        raise NotImplementedError()

    def S11_by_freq(self, F, system):
        Z = self.impedance_by_freq(F, system)
        return ((Z - system.Z_termination) / (Z + system.Z_termination))


class TerminatorResistor(ResistorBase, TerminatorImpedance):
    pass


class TerminatorCapacitor(CapacitorBase, TerminatorImpedance):
    pass


class TerminatorInductor(InductorBase, TerminatorImpedance):
    pass


class SeriesImpedance(SMatrix2PortBase):
    def __init__(
        self,
        **kwargs
    ):
        super(SeriesImpedance, self).__init__(**kwargs)
        return

    def impedance_by_freq(self, F, system):
        raise NotImplementedError()

    def S11_by_freq(self, F, system):
        Z = self.impedance_by_freq(F, system)
        return (Z / (Z + system.Z_termination * 2))

    def S12_by_freq(self, F, system):
        Z = self.impedance_by_freq(F, system)
        return ((2 * system.Z_termination) / (Z + system.Z_termination * 2))

    def S21_by_freq(self, F, system):
        Z = self.impedance_by_freq(F, system)
        return ((2 * system.Z_termination) / (Z + system.Z_termination * 2))

    def S22_by_freq(self, F, system):
        Z = self.impedance_by_freq(F, system)
        return (Z / (Z + system.Z_termination * 2))


class SeriesResistor(ResistorBase, SeriesImpedance):
    pass


class SeriesCapacitor(CapacitorBase, SeriesImpedance):
    pass


class SeriesInductor(InductorBase, SeriesImpedance):
    pass


class OpAmp(ElectricalElementBase):

    @decl.mproperty
    def in_p(self):
        return ElectricalPort(self, 'in_p')

    @decl.mproperty
    def in_n(self):
        return ElectricalPort(self, 'in_n')

    @decl.mproperty
    def out(self):
        return ElectricalPort(self, 'out')

    def gain_by_freq(self, F, system):
        return 1

    def system_setup_coupling(self, system):
        matrix = ForewardDictMatrix()
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            matrix[
                df_key | self.in_p.i,
                df_key | self.in_p.o
            ] = 1
            matrix[
                df_key | self.in_n.i,
                df_key | self.in_n.o
            ] = 1
            matrix[
                df_key | self.out.i,
                df_key | self.out.o
            ] = -1
            gbf = self.gain_by_freq(
                F = f_key.frequency(),
                system = system
            )
            matrix[
                df_key | self.in_p.i,
                df_key | self.out.o
            ] = gbf
            matrix[
                df_key | self.in_p.o,
                df_key | self.out.o
            ] = gbf
            matrix[
                df_key | self.in_n.i,
                df_key | self.out.o
            ] = -gbf
            matrix[
                df_key | self.in_n.o,
                df_key | self.out.o
            ] = -gbf

        matrix.insert(
            into = system.coupling_matrix,
            validate = system.dk_validate,
        )
        return


class VAmp(ElectricalElementBase):
    Y_input = 0
    Z_output = 0

    @decl.mproperty
    def in_n(self):
        return ElectricalPort(self, 'in_n')

    @decl.mproperty
    def out(self):
        return ElectricalPort(self, 'out')

    def gain_by_freq(self, F, system):
        return 1

    def system_setup_coupling(self, system):
        matrix = ForewardDictMatrix()
        for f_key in system.F_key_basis:
            df_key = DictKey(F = f_key)
            matrix[
                df_key | self.in_n.i,
                df_key | self.in_n.o
            ] = ((1 - self.Y_input * system.Z_termination) / (1 + self.Y_input * system.Z_termination))
            matrix[
                df_key | self.out.i,
                df_key | self.out.o
            ] = ((self.Z_output - system.Z_termination) / (self.Z_output + system.Z_termination))

            gbf = self.gain_by_freq(
                F = f_key.frequency(),
                system = system
            )

            matrix[
                df_key | self.in_n.i,
                df_key | self.out.o
            ] = -gbf
            matrix[
                df_key | self.in_n.o,
                df_key | self.out.o
            ] = -gbf

        matrix.insert(
            into = system.coupling_matrix,
            validate = system.dk_validate,
        )
        return





