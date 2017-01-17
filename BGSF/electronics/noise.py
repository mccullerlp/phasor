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

sided_conversions = {
    "one-sided" :    2,
    "one sided" :    2,
    "one" :          2,
    "single-sided" : 2,
    "single sided" : 2,
    "single" :       2,
    "two-sided" :    1,
    "two sided" :    1,
    "two" :          1,
    "double-sided" : 1,
    "double sided" : 1,
    "double" :       1,
}

class VoltageFluctuation(elements.ElectricalNoiseBase, elements.ElectricalElementBase):
    @decl.dproperty
    def port(self, val):
        self.system.own_port_virtual(self, val.i)
        self.system.own_port_virtual(self, val.o)
        return val

    @decl.dproperty
    def p_virt(self):
        return ports.ElectricalPortHolderOut(self, 'virtual')

    @decl.dproperty
    def sided(self, val):
        assert(val in sided_conversions)
        return val

    @decl.mproperty
    def conversion(self):
        return sided_conversions[self.sided]

    def Vsq_Hz_by_freq(self, F):
        return 0

    def system_setup_ports(self, ports_algorithm):
        print("SETUP: ", self)
        for kfrom in ports_algorithm.port_set_get(self.port.i):
            print("SETUP1: ", self, kfrom)
            ports_algorithm.port_coupling_needed(self.p_virt.o, kfrom)
        for kfrom in ports_algorithm.port_set_get(self.port.o):
            print("SETUP2: ", self, kfrom)
            ports_algorithm.port_coupling_needed(self.p_virt.o, kfrom)
        return

    def system_setup_ports_final(self, ports_algorithm):
        return

    def system_setup_coupling(self, matrix_algorithm):
        print("CPLG: ", self)
        for kfrom in matrix_algorithm.port_set_get(self.port.i):
            print("CPLG1: ", kfrom)
            matrix_algorithm.port_coupling_insert(
                self.p_virt.o,
                kfrom,
                self.port.i,
                kfrom,
                1,
            )
        porto_use = self.system.ports_post_get(self.port.o)
        for kfrom in matrix_algorithm.port_set_get(self.port.o):
            print("CPLG2: ", kfrom)
            matrix_algorithm.port_coupling_insert(
                self.p_virt.o,
                kfrom,
                porto_use,
                kfrom,
                -1,
            )

    def system_setup_noise(self, matrix_algorithm):
        #porti_use = self.port.i
        #porto_use = self.system.ports_post_get(self.port.o)
        print("SETUP NOISE")
        for k1 in matrix_algorithm.port_set_get(self.p_virt.o):
            freq = k1[ports.ClassicalFreqKey]
            k2 = k1.without_keys(ports.ClassicalFreqKey) | DictKey({ports.ClassicalFreqKey : -freq})

            print("NADD", k1)
            matrix_algorithm.noise_pair_insert(
                self.p_virt.o, k1, self.p_virt.o, k2, self
            )
            #matrix_algorithm.noise_pair_insert(
            #    porto_use, k1, porto_use, k2, self
            #)
            #matrix_algorithm.noise_pair_insert(
            #    porti_use, k1, porto_use, k2, self
            #)
            #matrix_algorithm.noise_pair_insert(
            #    porto_use, k1, porti_use, k2, self
            #)
            #matrix_algorithm.noise_pair_insert(
            #    porti_use, k1, porti_use, k2, self
            #)
        pass

    def noise_2pt_expectation(self, p1, k1, p2, k2):
        print ("USE NOISE: ", self)
        freq = k1[ports.ClassicalFreqKey].frequency()
        Vsq_Hz = self.Vsq_Hz_by_freq(freq) / self.conversion
        if p1 == p2:
            return Vsq_Hz / 4
        else:
            return -Vsq_Hz / 4


class CurrentFluctuation(elements.ElectricalNoiseBase):
    @decl.dproperty
    def port(self, val):
        return val

    @decl.dproperty
    def sided(self, val):
        assert(val in sided_conversions)
        return val

    @decl.mproperty
    def conversion(self):
        return sided_conversions[self.sided]

    def Isq_Hz_by_freq(self, F):
        return 0

    def system_setup_noise(self, matrix_algorithm):
        #print ("SETUP NOISE: ", self)
        porti_use = self.port.i
        porto_use = self.system.ports_post_get(self.port.o)
        for k1 in matrix_algorithm.port_set_get(self.port.o):
            freq = k1[ports.ClassicalFreqKey]
            k2 = k1.without_keys(ports.ClassicalFreqKey) | DictKey({ports.ClassicalFreqKey : -freq})

            matrix_algorithm.noise_pair_insert(
                porto_use, k1, porto_use, k2, self
            )
            matrix_algorithm.noise_pair_insert(
                self.port.i, k1, porto_use, k2, self
            )
            matrix_algorithm.noise_pair_insert(
                porto_use, k1, self.port.i, k2, self
            )
            matrix_algorithm.noise_pair_insert(
                self.port.i, k1, self.port.i, k2, self
            )
        pass

    def noise_2pt_expectation(self, p1, k1, p2, k2):
        freq = k1[ports.ClassicalFreqKey].frequency()
        Isq_Hz = self.Isq_Hz_by_freq(freq) / self.conversion
        if p1 == p2:
            return (self.Z_termination)**2 * Isq_Hz / 4
        else:
            return (self.Z_termination)**2 * Isq_Hz / 4
