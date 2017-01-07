# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

from .bases import (
    OpticalCouplerBase,
    OpticalNoiseBase,
    SystemElementBase,
)

from .ports import (
    OpticalPortHolderOut,
    QuantumKey,
    RAISE, LOWER,
    OpticalNonOriented1PortMixin,
)


#TODO - SystemElementBase,
# need system sled
class VacuumTerminator(OpticalNonOriented1PortMixin, OpticalCouplerBase, SystemElementBase):
    def __init__(
        self,
        **kwargs
    ):
        super(VacuumTerminator, self).__init__(**kwargs)
        self.Fr = OpticalPortHolderOut(self, x = 'Fr')
        #TODO, not sure I like these semantics
        self._fluct = OpticalVacuumFluctuation(port = self.Fr)
        return

    def linked_elements(self):
        return (
            self._fluct,
        )

    def system_setup_ports(self, system):
        return

class OpticalVacuumFluctuation(OpticalNoiseBase, SystemElementBase):
    def __init__(self, port, **kwargs):
        super(OpticalVacuumFluctuation, self).__init__(**kwargs)
        self.port = port

    def system_setup_noise(self, matrix_algorithm):
        #print ("SETUP NOISE: ", self)
        for k1 in matrix_algorithm.port_set_get(self.port.o):
            if k1.subkey_has(LOWER):
                k2 = k1.without_keys(QuantumKey) | RAISE
            else:
                k2 = k1.without_keys(QuantumKey) | LOWER

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
        return self.system.h_Js * self.system.c_m_s * iwavelen_m

