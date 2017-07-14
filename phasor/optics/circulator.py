# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from phasor.utilities.print import print

import declarative as decl

from . import bases
from . import ports


class OpticalCirculator(bases.OpticalCouplerBase, bases.SystemElementBase):

    @decl.dproperty
    def N_ports(self, val = 3):
        return val

    def __build__(
        self,
    ):
        self.port_list = []

        for idx in range(0, self.N_ports):
            pname = "P{0}".format(idx)
            if idx + 1 < self.N_ports:
                pnext = "P{0}".format(idx + 1)
            else:
                pnext = "P{0}".format(0)
            port = ports.OpticalPort(
                pchain = pnext
            )
            port = self.insert(port, pname)
            self.port_list.append(port)
        return

    def system_setup_ports(self, ports_algorithm):
        for idx, port in enumerate(self.port_list):
            idx_next = (idx + 1) % self.N_ports
            port_next = self.port_list[idx_next]
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(port_next.o, kfrom)
            for kto in ports_algorithm.port_update_get(port_next.o):
                ports_algorithm.port_coupling_needed(port.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for idx, port in enumerate(self.port_list):
            idx_next = (idx + 1) % self.N_ports
            port_next = self.port_list[idx_next]
            for kfrom in matrix_algorithm.port_set_get(port.i):
                matrix_algorithm.port_coupling_insert(port.i, kfrom, port_next.o, kfrom, 1)
        return


