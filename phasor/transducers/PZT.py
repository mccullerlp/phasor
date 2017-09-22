# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from builtins import object
import numpy as np

import declarative as decl

from . import smatrix
from . import elements
from . import noise

from ..mechanical import ports as m_ports
from ..electrical import ports as e_ports

from ..base.bases import (
    CouplerBase,
)


class MountedGroundedPZT(CouplerBase):
    @decl.dproperty
    def pe_A(self):
        return e_ports.ElectricalPort(pchain = 'pm_Z')

    @decl.dproperty
    def pm_Z(self):
        return m_ports.MechanicalPort(pchain = 'pe_A')

    def system_setup_ports(self, ports_algorithm):
        #TODO could reduce these with more information about used S-matrix elements
        ports = [
            self.pm_A,
            self.pm_B,
        ]
        for port1 in ports:
            for port2 in ports:
                for kfrom in ports_algorithm.port_update_get(port1.i):
                    ports_algorithm.port_coupling_needed(port2.o, kfrom)
                for kto in ports_algorithm.port_update_get(port2.o):
                    ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        def S11_by_freq(F_Hz):
            return

        def S12_by_freq(F_Hz):
            return

        def S21_by_freq(F_Hz):
            return

        def S22_by_freq(F_Hz):
            return

        for port1, port2, func in [
            (self.pe_A, self.pe_A, S11_by_freq),
            (self.pe_A, self.pm_Z, S12_by_freq),
            (self.pm_Z, self.pe_A, S21_by_freq),
            (self.pm_Z, self.pm_Z, S22_by_freq),
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
