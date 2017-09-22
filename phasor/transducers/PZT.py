# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from builtins import object
#import numpy as np

import declarative as declarative

from ..mechanical import ports as m_ports
from ..electrical import ports as e_ports
from ..mechanical import elements as m_elements
from ..electrical import elements as e_elements


class PZTMountedGrounded(
        m_elements.MechanicalElementBase,
        e_elements.ElectricalElementBase
):
    @declarative.dproperty
    def pe_A(self):
        return e_ports.ElectricalPort(pchain = 'pm_Z')

    @declarative.dproperty
    def pm_Z(self):
        return m_ports.MechanicalPort(pchain = 'pe_A')

    @declarative.dproperty
    def capacitance_F(self, val):
        return val

    @declarative.dproperty
    def k_N_m(self, val):
        return val

    @declarative.dproperty
    def d_eff_m_V(self, val = None):
        if val is None:
            val = self.full_swing_um*1e-6 / self.max_voltage_V
        return val

    @declarative.dproperty
    def full_swing_um(self, val = None):
        return val

    @declarative.dproperty
    def max_voltage_V(self, val = None):
        return val

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
        C   = self.capacitance_F
        k   = self.k_N_m
        d   = self.d_eff_m_V
        Z_e = self.Ze_termination
        Z_m = self.Zm_termination

        #computed in sympy
        def See_by_freq(F_Hz):
            s = self.symbols.i2pi * F_Hz
            return ((C*Z_e*Z_m*k*s + C*Z_e*s - Z_e*d**2*k*s - Z_m*k - 1)/(-C*Z_e*Z_m*k*s - C*Z_e*s + Z_e*d**2*k*s - Z_m*k - 1))

        def Smm_by_freq(F_Hz):
            s = self.symbols.i2pi * F_Hz
            return (-(Z_e*d**2*k*s + (Z_m*k - 1)*(C*Z_e*s + 1))/(C*Z_e*s - Z_e*d**2*k*s + Z_m*k*(C*Z_e*s + 1) + 1))

        def Sem_by_freq(F_Hz):
            s = self.symbols.i2pi * F_Hz
            return (2*Z_m*d*k/(C*Z_e*s - Z_e*d**2*k*s + Z_m*k*(C*Z_e*s + 1) + 1))

        def Sme_by_freq(F_Hz):
            s = self.symbols.i2pi * F_Hz
            return (2*Z_e*d*k*s/(-C*Z_e*Z_m*k*s - C*Z_e*s + Z_e*d**2*k*s - Z_m*k - 1))

        for port1, port2, func in [
            (self.pe_A, self.pe_A, See_by_freq),
            (self.pe_A, self.pm_Z, Sem_by_freq),
            (self.pm_Z, self.pe_A, Sme_by_freq),
            (self.pm_Z, self.pm_Z, Smm_by_freq),
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
