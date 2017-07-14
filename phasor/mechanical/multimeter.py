# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import declarative as decl

from .. import readouts
from . import elements
from . import ports

class DisplacementReadout(readouts.DCReadout, elements.MechanicalElementBase):
    """
    Measures the force to ground if not used differentially
    """

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
    def d(self):
        return ports.SignalOutPort(sname = 'd')

    @decl.dproperty
    def port(self):
        return self.d.o

    def system_setup_ports(self, ports_algorithm):
        #TODO hackish, need better system support for binding
        #this linear port into the readout ports
        ports = [self.terminal.i, self.terminal.o]
        if self.terminal_N is not None:
            ports.extend([self.terminal_N.i, self.terminal_N.o])
        for port1 in ports:
            for kfrom in ports_algorithm.port_update_get(port1):
                ports_algorithm.port_coupling_needed(self.d.o, kfrom)
            for kto in ports_algorithm.port_update_get(self.d.o):
                ports_algorithm.port_coupling_needed(port1, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        pcplgs = {
            self.system.ports_pre_get(self.terminal.i) :  1,
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
                    self.d.o,
                    kfrom,
                    pcplg,
                )


class ForceReadout(readouts.DCReadout, elements.MechanicalElementBase):

    @decl.dproperty
    def direction(self, val = 'out'):
        assert(val in ['in', 'out'])
        return val

    @decl.dproperty
    def terminal(self, port):
        return port

    @decl.dproperty
    def F(self):
        return ports.SignalOutPort(sname = 'F')

    @decl.dproperty
    def port(self):
        return self.F.o

    def system_setup_ports(self, ports_algorithm):
        #TODO hackish, need better system support for binding
        #this linear port into the readout ports
        ports = [self.terminal.i, self.terminal.o]
        for port1 in ports:
            #for kfrom in ports_algorithm.port_update_get(port1):
            #    ports_algorithm.port_coupling_needed(self.d.o, kfrom)
            for kto in ports_algorithm.port_update_get(self.F.o):
                ports_algorithm.port_coupling_needed(port1, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO, not sure about the 1/2 everywhere
        pcplgs = {
            self.terminal.i :  1 / self.zM_termination,
            self.terminal.o : -1 / self.zM_termination,
        }
        direction_cplg = {'in' : 1, 'out' : -1}[self.direction]
        for port, pcplg in pcplgs.items():
            for kfrom in matrix_algorithm.port_set_get(port):
                matrix_algorithm.port_coupling_insert(
                    port,
                    kfrom,
                    self.F.o,
                    kfrom,
                    direction_cplg * pcplg,
                )


