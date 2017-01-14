"""
"""
from __future__ import (division, print_function)

import declarative as decl
from . import ports
from . import elements


class OpAmp(elements.ElectricalElementBase):

    @decl.mproperty
    def in_p(self):
        return ports.ElectricalPortHolderInOut(self, 'in_p')

    @decl.mproperty
    def in_n(self):
        return ports.ElectricalPortHolderInOut(self, 'in_n')

    @decl.mproperty
    def out(self):
        return ports.ElectricalPortHolderInOut(self, 'out')

    def gain_by_freq(self, F):
        return 1

    def system_setup_ports(self, ports_algorithm):
        #TODO could reduce these with more information about used S-matrix elements
        for port1, port2 in (
            (self.in_p.i, self.out.o),
            (self.in_p.o, self.out.o),
            (self.in_n.i, self.out.o),
            (self.in_n.o, self.out.o),
            (self.in_p.i, self.in_p.o),
            (self.in_n.i, self.in_n.o),
            (self.out.i, self.out.o),
        ):
            for kfrom in ports_algorithm.port_update_get(port1):
                ports_algorithm.port_coupling_needed(port2, kfrom)
            for kto in ports_algorithm.port_update_get(port2):
                ports_algorithm.port_coupling_needed(port1, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #Should use two for-loops, but the .i and .o of port1 have the same kfrom's
        for port1, port2 in (
            (self.in_p, self.out),
            (self.in_n, self.out),
        ):
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                #if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                #    continue
                freq = self.system.classical_frequency_extract(kfrom)
                if port1 is self.in_p:
                    pgain = self.gain_by_freq(freq)
                elif port1 is self.in_n:
                    pgain = -self.gain_by_freq(freq)
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    pgain,
                )
                matrix_algorithm.port_coupling_insert(
                    port1.o,
                    kfrom,
                    port2.o,
                    kfrom,
                    pgain,
                )

        #terminated like an OPEN/CURRENT SOURCE
        for port1, port2 in (
            (self.in_p, self.in_p),
            (self.in_n, self.in_n),
        ):
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    1,
                )

        #terminated like an SHORT/VOLTAGE SOURCE
        for port1, port2 in (
            (self.out, self.out),
        ):
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    -1,
                )


class VAmp(elements.ElectricalElementBase):
    Y_input = 0
    Z_output = 0

    @decl.mproperty
    def in_n(self):
        return ports.ElectricalPortHolderInOut(self, 'in_n')

    @decl.mproperty
    def out(self):
        return ports.ElectricalPortHolderInOut(self, 'out')

    def gain_by_freq(self, F):
        return 1

    def system_setup_ports(self, ports_algorithm):
        #TODO could reduce these with more information about used S-matrix elements
        for port1, port2 in (
            (self.in_n.i, self.out.o),
            (self.in_n.o, self.out.o),
            (self.in_n.i, self.in_n.o),
            (self.out.i, self.out.o),
        ):
            for kfrom in ports_algorithm.port_update_get(port1.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for port1, port2 in (
            (self.in_n, self.out),
        ):
            #Should use two for-loops, but the .i and .o of port1 have the same kfrom's
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                #if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                #    continue
                freq = self.system.classical_frequency_extract(kfrom)
                pgain = self.gain_by_freq(freq)
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    -pgain,
                )
                matrix_algorithm.port_coupling_insert(
                    port1.o,
                    kfrom,
                    port2.o,
                    kfrom,
                    -pgain,
                )

        #terminated like an OPEN/CURRENT SOURCE
        for port1, port2 in (
            (self.in_n, self.in_n),
        ):
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                pgain = ((1 - self.Y_input * self.Z_termination) / (1 + self.Y_input * self.Z_termination))
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    pgain,
                )

        #terminated like an SHORT/VOLTAGE SOURCE
        for port1, port2 in (
            (self.out, self.out),
        ):
            pgain = ((self.Z_output - self.Z_termination) / (self.Z_output + self.Z_termination))
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    pgain,
                )





