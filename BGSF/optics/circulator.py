# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
)

from .ports import (
    OpticalPortHolderInOut,
)


class OpticalCirculator(OpticalCouplerBase, SystemElementBase):
    def __init__(
        self,
        N_ports = 3,
        **kwargs
    ):
        super(OpticalCirculator, self).__init__(**kwargs)
        self.N_ports = N_ports
        self.port_list = []

        for idx in range(0, N_ports):
            pname = "P{0}".format(idx)
            port = OpticalPortHolderInOut(self, x = pname)
            setattr(self, pname, port)
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


