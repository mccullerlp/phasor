"""
"""
from __future__ import division

import declarative as decl

from ..math.key_matrix.dictionary_keys import (
    DictKey,
    FrequencyKey,
)

from . import ports
from . import elements


class SMatrix1PortBase(elements.Electrical1PortBase):

    def S11_by_freq(self, F):
        raise NotImplementedError()

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.A.i):
            #if self.system.classical_frequency_test_max(kfrom, self.max_freq):
            #    continue
            freq = self.system.classical_frequency_extract(kfrom)
            pgain = self.S11_by_freq(freq)
            matrix_algorithm.port_coupling_insert(
                self.A.i,
                kfrom,
                self.A.o,
                kfrom,
                pgain,
            )


class SMatrix2PortBase(elements.Electrical2PortBase):

    def S11_by_freq(self, F):
        return 0

    def S12_by_freq(self, F):
        return 0

    def S21_by_freq(self, F):
        return 0

    def S22_by_freq(self, F):
        return 0

    @decl.mproperty
    def ports_electrical(self):
        return [
            self.A,
            self.B,
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
        for port1, port2, func in [
            (self.A, self.A, self.S11_by_freq),
            (self.A, self.B, self.S12_by_freq),
            (self.B, self.A, self.S21_by_freq),
            (self.B, self.B, self.S22_by_freq),
        ]:
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                #if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                #    continue
                freq = self.system.classical_frequency_extract(kfrom)
                pgain = self.S11_by_freq(freq)
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    pgain,
                )


class TerminatorMatched(SMatrix1PortBase):
    def S11_by_freq(self, F):
        return 0


class TerminatorOpen(SMatrix1PortBase):
    def S11_by_freq(self, F):
        return 1


class TerminatorShorted(SMatrix1PortBase):
    def S11_by_freq(self, F):
        return -1


class VoltageSource(SMatrix1PortBase):
    def S11_by_freq(self, F):
        return -1

    @decl.mproperty
    def V_DC(self, val = 0):
        return val

    @decl.dproperty
    def V(self):
        return ports.SignalPortHolderIn(self, x = 'V')

    @decl.mproperty
    def fkey(self):
        return DictKey({
            ports.ClassicalFreqKey: FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        ports_algorithm.coherent_sources_needed(self.A.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(VoltageSource, self).system_setup_ports(ports_algorithm)
        for kfrom in ports_algorithm.port_update_get(self.V.i):
            ports_algorithm.port_coupling_needed(self.A.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.A.o):
            ports_algorithm.port_coupling_needed(self.V.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(VoltageSource, self).system_setup_coupling(matrix_algorithm)

        matrix_algorithm.coherent_sources_insert(
            self.A.o,
            self.fkey,
            self.V_DC
        )

        for kfrom in matrix_algorithm.port_set_get(self.V.i):
            matrix_algorithm.port_coupling_insert(
                self.V.i,
                kfrom,
                self.A.o,
                kfrom,
                1,
            )
        return


class CurrentSource(SMatrix1PortBase):
    def S11_by_freq(self, F):
        return 1

    @decl.mproperty
    def I_DC(self, val = 0):
        #TODO set I_DC
        return val

    @decl.dproperty
    def I(self):
        return ports.SignalPortHolderIn(self, x = 'I')

    @decl.mproperty
    def fkey(self):
        return DictKey({
            ports.ClassicalFreqKey: FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        ports_algorithm.coherent_sources_needed(self.A.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(CurrentSource, self).system_setup_ports(ports_algorithm)
        for kfrom in ports_algorithm.port_update_get(self.I.i):
            ports_algorithm.port_coupling_needed(self.A.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.A.o):
            ports_algorithm.port_coupling_needed(self.I.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(CurrentSource, self).system_setup_coupling(matrix_algorithm)

        matrix_algorithm.coherent_sources_insert(
            self.A.o,
            self.fkey,
            self.I_DC * self.Z_termination
        )

        for kfrom in matrix_algorithm.port_set_get(self.I.i):
            matrix_algorithm.port_coupling_insert(
                self.I.i,
                kfrom,
                self.A.o,
                kfrom,
                self.Z_termination,
            )
        return


class VoltageSourceBalanced(SMatrix2PortBase):
    def S11_by_freq(self, F):
        return 0

    def S12_by_freq(self, F):
        return 1

    def S21_by_freq(self, F):
        return 1

    def S22_by_freq(self, F):
        return 0

    @decl.mproperty
    def V_DC(self, val = 0):
        return val

    @decl.dproperty
    def V(self):
        return ports.SignalPortHolderIn(self, x = 'V')

    @decl.mproperty
    def I_DC(self, val = 0):
        return val

    @decl.dproperty
    def I(self):
        return ports.SignalPortHolderIn(self, x = 'I')

    def system_setup_ports(self, ports_algorithm):
        super(VoltageSourceBalanced, self).system_setup_ports(ports_algorithm)
        for port2 in [self.A, self.B]:
            for kfrom in ports_algorithm.port_update_get(self.V.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(self.V.i, kto)
            for kfrom in ports_algorithm.port_update_get(self.I.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(self.I.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(VoltageSourceBalanced, self).system_setup_coupling(matrix_algorithm)
        #TODO, not sure about the 1/2 everywhere
        _2 = self.math.number(2)
        for kfrom in matrix_algorithm.port_set_get(self.V.i):
            matrix_algorithm.port_coupling_insert(
                self.V.i,
                kfrom,
                self.A.o,
                kfrom,
                1 / _2,
            )
            matrix_algorithm.port_coupling_insert(
                self.V.i,
                kfrom,
                self.B.o,
                kfrom,
                -1 / _2,
            )
        for kfrom in matrix_algorithm.port_set_get(self.I.i):
            matrix_algorithm.port_coupling_insert(
                self.I.i,
                kfrom,
                self.A.o,
                kfrom,
                self.Z_termination / _2,
            )
            matrix_algorithm.port_coupling_insert(
                self.I.i,
                kfrom,
                self.B.o,
                kfrom,
                self.Z_termination / _2,
            )


class CurrentSourceBalanced(SMatrix2PortBase):
    def S11_by_freq(self, F):
        return 1

    def S12_by_freq(self, F):
        return 0

    def S21_by_freq(self, F):
        return 0

    def S22_by_freq(self, F):
        return 1

    @decl.mproperty
    def I_DC(self, val = 0):
        return val

    @decl.dproperty
    def I(self):
        return ports.SignalPortHolderIn(self, x = 'I')

    def system_setup_ports(self, ports_algorithm):
        super(VoltageSourceBalanced, self).system_setup_ports(ports_algorithm)
        for port2 in [self.A, self.B]:
            for kfrom in ports_algorithm.port_update_get(self.I.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(self.I.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(VoltageSourceBalanced, self).system_setup_coupling(matrix_algorithm)
        #TODO, not sure about the 1/2 everywhere
        _2 = self.math.number(2)
        for kfrom in matrix_algorithm.port_set_get(self.I.i):
            matrix_algorithm.port_coupling_insert(
                self.I.i,
                kfrom,
                self.A.o,
                kfrom,
                self.Z_termination / _2,
            )
            matrix_algorithm.port_coupling_insert(
                self.I.i,
                kfrom,
                self.B.o,
                kfrom,
                self.Z_termination / _2,
            )


