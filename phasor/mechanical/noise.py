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

class DisplacementFluctuation(elements.MechanicalNoiseBase, elements.MechanicalElementBase):

    @decl.dproperty
    def port(self, val):
        self.system.own_port_virtual(self, val.i)
        self.system.own_port_virtual(self, val.o)
        return val

    @decl.dproperty
    def p_virt(self):
        return ports.MechanicalPort(sname = 'virtual')

    @decl.dproperty
    def sided(self, val):
        assert(val in sided_conversions)
        return val

    @decl.mproperty
    def conversion(self):
        return sided_conversions[self.sided]

    @staticmethod
    def dsq_Hz_by_freq(F):
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

    def noise_2pt_expectation(self, pm_1, k1, pm_2, k2):
        freq = k1[ports.ClassicalFreqKey].frequency()
        dsq_Hz = self.dsq_Hz_by_freq(freq) / self.conversion
        return dsq_Hz


class ForceFluctuation(elements.MechanicalNoiseBase, elements.MechanicalElementBase):

    @decl.dproperty
    def portA(self, val):
        self.system.own_port_virtual(self, val.o)
        return val

    @decl.dproperty
    def portB(self, val):
        self.system.own_port_virtual(self, val.o)
        return val

    @decl.dproperty
    def p_virt(self):
        return ports.MechanicalPort(sname = 'virtual')

    @decl.dproperty
    def sided(self, val):
        assert(val in sided_conversions)
        return val

    @decl.mproperty
    def conversion(self):
        return sided_conversions[self.sided]

    @staticmethod
    def Fsq_Hz_by_freq(F):
        return 0

    def system_setup_ports(self, ports_algorithm):
        for kto in ports_algorithm.port_update_get(self.portA.o):
            ports_algorithm.port_coupling_needed(self.p_virt.o, kto)
        for kto in ports_algorithm.port_update_get(self.portB.o):
            ports_algorithm.port_coupling_needed(self.p_virt.o, kto)
        for kfrom in ports_algorithm.port_update_get(self.p_virt.o):
            ports_algorithm.port_coupling_needed(self.portB.o, kfrom)
            ports_algorithm.port_coupling_needed(self.portA.o, kfrom)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.p_virt.o):
            matrix_algorithm.port_coupling_insert(
                self.p_virt.o,
                kfrom,
                self.portA.o,
                kfrom,
                1/2,
            )
            matrix_algorithm.port_coupling_insert(
                self.p_virt.o,
                kfrom,
                self.portB.o,
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

    def noise_2pt_expectation(self, pm_1, k1, pm_2, k2):
        freq = k1[ports.ClassicalFreqKey].frequency()
        Fsq_Hz = self.Fsq_Hz_by_freq(freq) / self.conversion
        return (self.zM_termination)**2 * Fsq_Hz


