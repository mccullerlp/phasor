# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from OpenLoop.utilities.print import print

import declarative

from . import bases
from . import ports

class VacuumTerminator(
    bases.OpticalCouplerBase,
):

    @declarative.dproperty
    def Fr(self):
        return ports.OpticalPort(sname = 'Fr')

    @declarative.dproperty
    def _fluct(self):
        return OpticalVacuumFluctuation(port = self.Fr)

    def system_setup_ports(self, ports_algorithm):
        #TODO should separate "wanted" ports from "driven ports"
        #Must move inputs to outputs for AC sidebands
        for kto in ports_algorithm.port_update_get(self.Fr.o):
            ports_algorithm.port_coupling_needed(self.Fr.i, kto)
        for kfrom in ports_algorithm.port_update_get(self.Fr.i):
            ports_algorithm.port_coupling_needed(self.Fr.o, kfrom)
        return


class OpticalVacuumFluctuation(
    bases.OpticalNoiseBase,
):
    @declarative.dproperty
    def port(self, val):
        return val

    def system_setup_noise(self, matrix_algorithm):
        for k1 in matrix_algorithm.port_set_get(self.port.o):
            #print(self, k1)
            if k1.subkey_has(ports.LOWER):
                k2 = k1.without_keys(ports.QuantumKey) | ports.RAISE
            else:
                k2 = k1.without_keys(ports.QuantumKey) | ports.LOWER

            matrix_algorithm.noise_pair_insert(
                self.port.o, k1, self.port.o, k2, self
            )
        pass

    def noise_2pt_expectation(self, p1, k1, p2, k2):
        #dont need to further check as the setup noise call already selected pairs
        iwavelen_m, freq_Hz = self.system.optical_frequency_extract(k1)
        #this is in the TWO SIDED PSPEC
        return self.symbols.h_Js * self.symbols.c_m_s * iwavelen_m / 2