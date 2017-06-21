"""
"""
from __future__ import division

import declarative as decl

from .. import readouts
from . import elements
from . import ports

class VoltageReadout(readouts.DCReadout, elements.ElectricalElementBase):

    @decl.dproperty
    def terminal(self, port):
        self.system.own_port_virtual(self, port.i)
        self.system.own_port_virtual(self, port.o)
        return port

    @decl.dproperty
    def terminal_N(self, port = None):
        if port is not None:
            self.system.own_port_virtual(self, port.i)
            self.system.own_port_virtual(self, port.o)
        return port

    @decl.dproperty
    def V(self):
        return ports.SignalOutPort(sname = 'V')

    @decl.dproperty
    def port(self):
        return self.V.o

    def system_setup_ports(self, ports_algorithm):
        #TODO hackish, need better system support for binding
        #this linear port into the readout ports
        ports = [self.terminal.i, self.terminal.o]
        if self.terminal_N is not None:
            ports.extend([self.terminal_N.i, self.terminal_N.o])
        for port1 in ports:
            for kfrom in ports_algorithm.port_update_get(port1):
                ports_algorithm.port_coupling_needed(self.V.o, kfrom)
            for kto in ports_algorithm.port_update_get(self.V.o):
                ports_algorithm.port_coupling_needed(port1, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        pcplgs = {
            self.system.ports_pre_get(self.terminal.i) : 1,
            self.system.ports_post_get(self.terminal.o) : 1,
        }
        if self.terminal_N is not None:
            pcplgs[self.terminal_N.i] = -1
            pcplgs[self.terminal_N.o] = -1
        for port, pcplg in pcplgs.items():
            for kfrom in matrix_algorithm.port_set_get(port):
                matrix_algorithm.port_coupling_insert(
                    port,
                    kfrom,
                    self.V.o,
                    kfrom,
                    pcplg,
                )


class CurrentReadout(readouts.DCReadout, elements.ElectricalElementBase):

    @decl.dproperty
    def direction(self, val):
        assert(val in ['in', 'out'])
        return val

    @decl.dproperty
    def terminal(self, port):
        return port

    @decl.dproperty
    def ps_In(self):
        return ports.SignalOutPort(sname = 'ps_In')

    @decl.dproperty
    def port(self):
        return self.ps_In.o

    def system_setup_ports(self, ports_algorithm):
        #TODO hackish, need better system support for binding
        #this linear port into the readout ports
        ports = [self.terminal.i, self.terminal.o]
        for port1 in ports:
            #for kfrom in ports_algorithm.port_update_get(port1):
            #    ports_algorithm.port_coupling_needed(self.ps_In.o, kfrom)
            for kto in ports_algorithm.port_update_get(self.ps_In.o):
                ports_algorithm.port_coupling_needed(port1, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO, not sure about the 1/2 everywhere
        _2 = self.symbols.number(2)
        pcplgs = {
            self.terminal.i :  1 / self.Z_termination,
            self.terminal.o : -1 / self.Z_termination,
        }
        direction_cplg = {'in' : 1, 'out' : -1}[self.direction]
        for port, pcplg in pcplgs.items():
            for kfrom in matrix_algorithm.port_set_get(port):
                matrix_algorithm.port_coupling_insert(
                    port,
                    kfrom,
                    self.ps_In.o,
                    kfrom,
                    direction_cplg * pcplg,
                )


