"""
"""
from __future__ import division, print_function

import declarative as decl

from . import elements
from . import noise


class SMatrix1PortBase(elements.Electrical1PortBase):

    def S11_by_freq(self, F):
        raise NotImplementedError()

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.pe_A.i):
            #if self.system.classical_frequency_test_max(kfrom, self.max_freq):
            #    continue
            freq = self.system.classical_frequency_extract(kfrom)
            pgain = self.S11_by_freq(freq)
            matrix_algorithm.port_coupling_insert(
                self.pe_A.i,
                kfrom,
                self.pe_A.o,
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
            self.pe_A,
            self.pe_B,
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
            (self.pe_A, self.pe_A, self.S11_by_freq),
            (self.pe_A, self.pe_B, self.S12_by_freq),
            (self.pe_B, self.pe_A, self.S21_by_freq),
            (self.pe_B, self.pe_B, self.S22_by_freq),
        ]:
            for kfrom in matrix_algorithm.port_set_get(port1.i):
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

    @decl.dproperty
    def johnson_noise(self):
        if self.system.include_johnson_noise:
            return noise.VoltageFluctuation(
                port = self.pe_A,
                Vsq_Hz_by_freq = lambda F : 4 * self.Z_termination.real * self.symbols.temp_K * self.symbols.kB_J_K,
                sided = 'one-sided',
            )
        return None


class TerminatorOpen(SMatrix1PortBase):
    def S11_by_freq(self, F):
        return 1


class TerminatorShorted(SMatrix1PortBase):
    def S11_by_freq(self, F):
        return -1

