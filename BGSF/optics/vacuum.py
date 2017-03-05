# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

import declarative as decl

from . import bases
from . import ports

#TODO - bases.SystemElementBase,
# need system sled
class VacuumTerminator(bases.OpticalCouplerBase, bases.SystemElementBase):

    @decl.dproperty
    def Fr(self):
        return ports.OpticalPort(sname = 'Fr')

    @decl.dproperty
    def _fluct(self):
        return OpticalVacuumFluctuation(port = self.Fr)

    def linked_elements(self):
        return (self._fluct,)

    def system_setup_ports(self, system):
        return


class OpticalVacuumFluctuation(bases.OpticalNoiseBase, bases.SystemElementBase):
    @decl.dproperty
    def port(self, val):
        return val

    def system_setup_noise(self, matrix_algorithm):
        #print ("SETUP NOISE: ", self)
        for k1 in matrix_algorithm.port_set_get(self.port.o):
            if k1.subkey_has(ports.LOWER):
                k2 = k1.without_keys(ports.QuantumKey) | ports.RAISE
            else:
                k2 = k1.without_keys(ports.QuantumKey) | ports.LOWER

            #matrix_algorithm.noise_pair_insert(
            #    self.port.o, k1, self.port.o, k1, self.optical_vacuum_noise_generate
            #)
            matrix_algorithm.noise_pair_insert(
                self.port.o, k1, self.port.o, k2, self
            )
        pass

    def noise_2pt_expectation(self, p1, k1, p2, k2):
        #dont need to further check as the setup noise call already selected pairs
        iwavelen_m, freq_Hz = self.system.optical_frequency_extract(k1)
        #this is in the TWO SIDED PSPEC
        #TODO double thing this value (/ 2 part)
        return self.symbols.h_Js * self.symbols.c_m_s * iwavelen_m / 2

