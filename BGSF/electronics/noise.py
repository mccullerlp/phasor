"""
"""
from __future__ import division

import declarative as decl

from ..math.key_matrix.dictionary_keys import (
    DictKey,
    FrequencyKey,
)

from . import ports
from . import elements


class VoltageFluctuation(elements.ElectricalNoiseBase):
    @decl.dproperty
    def port(self, val):
        return val

    def Vsq_Hz_by_freq(self, F):
        return 0

    def system_setup_noise(self, matrix_algorithm):
        #print ("SETUP NOISE: ", self)
        for k1 in matrix_algorithm.port_set_get(self.port.o):
            freq = k1[ports.ClassicalFreqKey]
            k2 = k1.without_keys(ports.ClassicalFreqKey) | DictKey({ports.ClassicalFreqKey : -freq})

            matrix_algorithm.noise_pair_insert(
                self.port.o, k1, self.port.o, k2, self
            )
            matrix_algorithm.noise_pair_insert(
                self.port.i, k1, self.port.o, k2, self
            )
            matrix_algorithm.noise_pair_insert(
                self.port.o, k1, self.port.i, k2, self
            )
            matrix_algorithm.noise_pair_insert(
                self.port.i, k1, self.port.i, k2, self
            )
        pass

    def noise_2pt_expectation(self, p1, k1, p2, k2):
        freq = k1[ports.ClassicalFreqKey]
        Vsq_Hz = self.Vsq_Hz_by_freq(freq)
        if p1 == p2:
            return Vsq_Hz / 4
        else:
            return -Vsq_Hz / 4


class CurrentFluctuation(elements.ElectricalNoiseBase):
    @decl.dproperty
    def port(self, val):
        return val

    def Isq_Hz_by_freq(self, F):
        return 0

    def system_setup_noise(self, matrix_algorithm):
        for k1 in matrix_algorithm.port_set_get(self.port.o):
            freq = k1[ports.ClassicalFreqKey]
            k2 = k1.without_keys(ports.ClassicalFreqKey) | DictKey({ports.ClassicalFreqKey : -freq})

            matrix_algorithm.noise_pair_insert(
                self.port.o, k1, self.port.o, k2, self
            )
            #matrix_algorithm.noise_pair_insert(
            #    self.port.i, k1, self.port.o, k2, self
            #)
            #matrix_algorithm.noise_pair_insert(
            #    self.port.o, k1, self.port.i, k2, self
            #)
            #matrix_algorithm.noise_pair_insert(
            #    self.port.i, k1, self.port.i, k2, self
            #)
        pass

    def noise_2pt_expectation(self, p1, k1, p2, k2):
        freq = k1[ports.ClassicalFreqKey]
        Isq_Hz = self.Isq_Hz_by_freq(freq)
        if p1 == p2:
            return (self.Z_termination)**2 * Isq_Hz / 4
        else:
            return (self.Z_termination)**2 * Isq_Hz / 4
