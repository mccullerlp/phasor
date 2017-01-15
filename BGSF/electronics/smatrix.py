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
                print(port1, kfrom)
                #if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                #    continue
                freq = self.system.classical_frequency_extract(kfrom)
                pgain = func(freq)
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

