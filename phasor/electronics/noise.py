# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import declarative as decl

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
        return ports.ElectricalPort(sname = 'virtual')

    @decl.dproperty
    def sided(self, val):
        assert(val in sided_conversions)
        return val

    @decl.mproperty
    def conversion(self):
        return sided_conversions[self.sided]

    @staticmethod
    def Vsq_Hz_by_freq(F):
        return 0

    def system_setup_ports(self, ports_algorithm):
        for kto in ports_algorithm.port_update_get(self.port.i):
            ports_algorithm.port_coupling_needed(self.p_virt.o, kto)
        for kto in ports_algorithm.port_update_get(self.port.o):
            ports_algorithm.port_coupling_needed(self.p_virt.o, kto)
        for kfrom in ports_algorithm.port_update_get(self.p_virt.o):
            ports_algorithm.port_coupling_needed(self.port.o, kfrom)
            ports_algorithm.port_coupling_needed(self.port.i, kfrom)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO: double check that porto needs to be used
        porto_use = self.port.o #  self.system.ports_post_get(self.port.o)
        for kfrom in matrix_algorithm.port_set_get(self.p_virt.o):
            matrix_algorithm.port_coupling_insert(
                self.p_virt.o,
                kfrom,
                self.port.i,
                kfrom,
                1/2,
            )
            matrix_algorithm.port_coupling_insert(
                self.p_virt.o,
                kfrom,
                porto_use,
                kfrom,
                -1/2,
            )

    def system_setup_noise(self, matrix_algorithm):
        for k1 in matrix_algorithm.port_set_get(self.p_virt.o):
            freq = k1[ports.ClassicalFreqKey]
            k2 = k1.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey : -freq})
            matrix_algorithm.noise_pair_insert(
                self.p_virt.o, k1, self.p_virt.o, k2, self
            )
        return

    def noise_2pt_expectation(self, pe_1, k1, pe_2, k2):
        freq = k1[ports.ClassicalFreqKey].frequency()
        Vsq_Hz = self.Vsq_Hz_by_freq(freq) / self.conversion
        return Vsq_Hz


class CurrentFluctuation(elements.ElectricalNoiseBase, elements.ElectricalElementBase):

    @decl.dproperty
    def port(self, val = None):
        if val is not None:
            self.system.own_port_virtual(self, val.o)
            self.system.own_port_virtual(self, val.i)
        return val

    @decl.dproperty
    def portA(self, val = None):
        if val is None:
            val = self.port.i
        self.system.own_port_virtual(self, val)
        return val

    @decl.dproperty
    def portB(self, val = None):
        if val is None:
            val = self.port.o
        self.system.own_port_virtual(self, val)
        return val

    @decl.dproperty
    def p_virt(self):
        return ports.ElectricalPort(sname = 'virtual')

    @decl.dproperty
    def sided(self, val):
        assert(val in sided_conversions)
        return val

    @decl.mproperty
    def conversion(self):
        return sided_conversions[self.sided]

    @staticmethod
    def Isq_Hz_by_freq(F):
        return 0

    def system_setup_ports(self, ports_algorithm):
        for kto in ports_algorithm.port_update_get(self.portA):
            ports_algorithm.port_coupling_needed(self.p_virt.o, kto)
        for kto in ports_algorithm.port_update_get(self.portB):
            ports_algorithm.port_coupling_needed(self.p_virt.o, kto)
        for kfrom in ports_algorithm.port_update_get(self.p_virt.o):
            ports_algorithm.port_coupling_needed(self.portB, kfrom)
            ports_algorithm.port_coupling_needed(self.portA, kfrom)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO: double check that porto needs to be used
        #porto_use = self.system.ports_post_get(self.portB)
        porto_use = self.portB  # self.system.ports_post_get(self.portB)
        for kfrom in matrix_algorithm.port_set_get(self.p_virt.o):
            matrix_algorithm.port_coupling_insert(
                self.p_virt.o,
                kfrom,
                self.portA,
                kfrom,
                1/2,
            )
            matrix_algorithm.port_coupling_insert(
                self.p_virt.o,
                kfrom,
                porto_use,
                kfrom,
                1/2,
            )

    def system_setup_noise(self, matrix_algorithm):
        for k1 in matrix_algorithm.port_set_get(self.p_virt.o):
            freq = k1[ports.ClassicalFreqKey]
            k2 = k1.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey : -freq})
            matrix_algorithm.noise_pair_insert(
                self.p_virt.o, k1, self.p_virt.o, k2, self
            )
        return

    def noise_2pt_expectation(self, pe_1, k1, pe_2, k2):
        freq = k1[ports.ClassicalFreqKey].frequency()
        Isq_Hz = self.Isq_Hz_by_freq(freq) / self.conversion
        return (self.Z_termination)**2 * Isq_Hz


class VoltageFluctuation2(elements.ElectricalNoiseBase):
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

    @staticmethod
    def Vsq_Hz_by_freq(F):
        return 0

    def system_setup_noise(self, matrix_algorithm):
        porti_use = self.port.i
        porto_use = self.system.ports_post_get(self.port.o)
        for k1 in matrix_algorithm.port_set_get(self.port.o):
            freq = k1[ports.ClassicalFreqKey]
            k2 = k1.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey : -freq})

            matrix_algorithm.noise_pair_insert(
                porto_use, k1, porto_use, k2, self
            )
            matrix_algorithm.noise_pair_insert(
                porti_use, k1, porto_use, k2, self
            )
            matrix_algorithm.noise_pair_insert(
                porto_use, k1, porti_use, k2, self
            )
            matrix_algorithm.noise_pair_insert(
                porti_use, k1, porti_use, k2, self
            )
        pass

    def noise_2pt_expectation(self, pe_1, k1, pe_2, k2):
        freq = k1[ports.ClassicalFreqKey].frequency()
        Vsq_Hz = self.Vsq_Hz_by_freq(freq) / self.conversion
        if pe_1 == pe_2:
            return Vsq_Hz / 4
        else:
            return -Vsq_Hz / 4


class CurrentFluctuation2(elements.ElectricalNoiseBase):
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

    @staticmethod
    def Isq_Hz_by_freq(F):
        return 0

    def system_setup_noise(self, matrix_algorithm):
        #print ("SETUP NOISE: ", self)
        #porti_use = self.port.i
        porto_use = self.system.ports_post_get(self.port.o)
        for k1 in matrix_algorithm.port_set_get(self.port.o):
            freq = k1[ports.ClassicalFreqKey]
            k2 = k1.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey : -freq})

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

    def noise_2pt_expectation(self, pe_1, k1, pe_2, k2):
        freq = k1[ports.ClassicalFreqKey].frequency()
        Isq_Hz = self.Isq_Hz_by_freq(freq) / self.conversion
        if pe_1 == pe_2:
            return (self.Z_termination)**2 * Isq_Hz / 4
        else:
            return (self.Z_termination)**2 * Isq_Hz / 4
