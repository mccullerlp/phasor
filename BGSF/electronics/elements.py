"""
"""
from __future__ import (division, print_function)

from ..base.bases import (
    ElementBase,
    NoiseBase,
    CouplerBase,
)

import declarative as decl

from . import ports


class ElectricalElementBase(CouplerBase, ElementBase):
    Z_termination = 50

    @decl.mproperty
    def math(self):
        return self.system


class ElectricalNoiseBase(NoiseBase, ElectricalElementBase):
    pass


class Electrical1PortBase(ElectricalElementBase):
    @decl.dproperty
    def A(self):
        return ports.ElectricalPortHolderInOut(self, 'A')

    @decl.mproperty
    def Fr(self):
        return self.A

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.A.i):
            ports_algorithm.port_coupling_needed(self.A.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.A.o):
            ports_algorithm.port_coupling_needed(self.A.i, kto)
        return


class Electrical2PortBase(ElectricalElementBase):
    @decl.dproperty
    def A(self):
        return ports.ElectricalPortHolderInOut(self, 'A', pchain = 'B')

    @decl.dproperty
    def B(self):
        return ports.ElectricalPortHolderInOut(self, 'B', pchain = 'A')

    @decl.mproperty
    def Fr(self):
        return self.A

    @decl.mproperty
    def Bk(self):
        return self.B

class Electrical4PortBase(ElectricalElementBase):
    @decl.dproperty
    def A(self):
        return ports.ElectricalPortHolderInOut(self, 'A')

    @decl.dproperty
    def B(self):
        return ports.ElectricalPortHolderInOut(self, 'B')

    @decl.dproperty
    def C(self):
        return ports.ElectricalPortHolderInOut(self, 'C')

    @decl.dproperty
    def D(self):
        return ports.ElectricalPortHolderInOut(self, 'D')

    @decl.mproperty
    def FrA(self):
        return self.A

    @decl.mproperty
    def FrB(self):
        return self.B

    @decl.mproperty
    def BkA(self):
        return self.C

    @decl.mproperty
    def BkB(self):
        return self.D


class Connection(ElectricalElementBase):
    @decl.dproperty
    def N_ports(self, val = 0):
        return val

    @decl.dproperty
    def connect(self, val = ()):
        return val

    def __build__(self):
        super(Connection, self).__build__()

        total_ports = self.N_ports + len(self.connect)
        ports_electrical = []
        for idx in range(total_ports):
            name = 'p{0}'.format(idx)
            pobj = ports.ElectricalPortHolderInOut(self, x = name)
            setattr(self, name, pobj)
            ports_electrical.append(pobj)
        self.ports_electrical = ports_electrical
        for idx in range(len(self.connect)):
            name = 'p{0}'.format(idx + self.N_ports)
            port = getattr(self, name)
            self.system.bond(self.connect[idx], port)
        return

    def system_setup_ports(self, ports_algorithm):
        for port1 in self.ports_electrical:
            for port2 in self.ports_electrical:
                for kfrom in ports_algorithm.port_update_get(port1.i):
                    ports_algorithm.port_coupling_needed(port2.o, kfrom)
                for kto in ports_algorithm.port_update_get(port2.o):
                    ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        _2 = self.math.number(2)
        total_ports = len(self.ports_electrical)
        for port1 in self.ports_electrical:
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                for port2 in self.ports_electrical:
                    if port1 is port2:
                        pgain = (_2 - total_ports) / total_ports
                    else:
                        pgain = (_2 / total_ports)
                    matrix_algorithm.port_coupling_insert(
                        port1.i,
                        kfrom,
                        port2.o,
                        kfrom,
                        pgain,
                    )


class Cable(Electrical2PortBase):
    @decl.dproperty
    def length_ns(self, val = 0):
        return val

    def phase_advance(self, F):
        return self.math.exp(-2 * self.system.i * self.system.pi * F * self.length_ns)

    def system_setup_ports(self, ports_algorithm):
        #TODO could reduce these with more information about used S-matrix elements
        for port1, port2 in [
            (self.A, self.B),
            (self.B, self.A),
        ]:
            for kfrom in ports_algorithm.port_update_get(port1.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for port1, port2 in [
            (self.A, self.B),
            (self.B, self.A),
        ]:
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                #if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                #    continue
                freq = self.system.classical_frequency_extract(kfrom)
                pgain = self.phase_advance(freq)
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    pgain,
                )
