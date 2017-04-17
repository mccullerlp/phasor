# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
#from BGSF.utilities.print import print
import declarative

from . import bases
from . import ports
from . import nonlinear_utilities

class Optical2PortModulator(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):
    @declarative.dproperty
    def Fr(self):
        return ports.OpticalPort(sname = 'Fr', pchain = 'Bk')

    @declarative.dproperty
    def Bk(self):
        return ports.OpticalPort(sname = 'Bk', pchain = 'Fr')

    @declarative.dproperty
    def Drv(self):
        return ports.SignalInPort(sname = 'Drv')

    @declarative.dproperty
    def BA(self):
        return ports.SignalOutPort(sname = 'BA')

    @declarative.mproperty
    def ports_optical(self):
        return set([
            self.Fr,
            self.Bk,
        ])

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.Fr.i : [self.Bk.o],
            self.Bk.i : [self.Fr.o],
            self.Fr.o : [self.Bk.i],
            self.Bk.o : [self.Fr.i],
        }

        #direct couplings
        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                for pto in pmap[port.i]:
                    ports_algorithm.port_coupling_needed(pto, kfrom)
            for kto in ports_algorithm.port_update_get(port.o):
                for pfrom in pmap[port.o]:
                    ports_algorithm.port_coupling_needed(pfrom, kto)

        nonlinear_utilities.ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            self.ports_optical,
            self.ports_optical,
            pmap,
            self.Drv.i,
            self.BA.o,
        )
        return


class PM(Optical2PortModulator):
    def system_setup_coupling(self, matrix_algorithm):
        cmap = {
            self.Fr : (self.Bk, 1),
            self.Bk : (self.Fr, 1),
        }

        ports_in_optical = [
            self.Fr,
            self.Bk,
        ]

        for pfrom in ports_in_optical:
            for kfrom in matrix_algorithm.port_set_get(pfrom.i):
                ptoOpt, std_cplg = cmap[pfrom]
                std_cplgC = std_cplg

                nonlinear_utilities.modulations_fill_2optical_2classical(
                    self.system,
                    matrix_algorithm,
                    pfrom, kfrom,
                    ptoOpt,
                    self.Drv.i,
                    self.BA.o,
                    std_cplg,
                    std_cplgC,
                    self.symbols.i / 2,
                    -self.symbols.i / 2,
                    1 / self.symbols.c_m_s,
                    1 / self.symbols.c_m_s,
                )
        return


class AM(Optical2PortModulator):
    def system_setup_coupling(self, matrix_algorithm):
        cmap = {
            self.Fr : (self.Bk, 1),
            self.Bk : (self.Fr, 1),
        }

        ports_in_optical = [
            self.Fr,
            self.Bk,
        ]

        for pfrom in ports_in_optical:
            for kfrom in matrix_algorithm.port_set_get(pfrom.i):
                ptoOpt, std_cplg = cmap[pfrom]
                std_cplgC = std_cplg

                nonlinear_utilities.modulations_fill_2optical_2classical(
                    self.system,
                    matrix_algorithm,
                    pfrom, kfrom,
                    ptoOpt,
                    self.Drv.i,
                    self.BA.o,
                    std_cplg,
                    std_cplgC,
                    1 / 2,
                    1 / 2,
                    self.symbols.i / self.symbols.c_m_s,
                    -self.symbols.i / self.symbols.c_m_s,
                )
        return

#TODO
class AOM(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):

    @declarative.dproperty
    def shift_direction(self, val = 'up'):
        assert(val in ['up', 'dn'])
        return val

    @declarative.dproperty
    def drive_PWR_nominal(self, val = 1):
        return val

    @declarative.dproperty
    def efficiency_nominal(self, val = 1):
        return val

    @declarative.dproperty
    def isolation(self, val = 1):
        return val

    @declarative.dproperty
    def Fr(self):
        return ports.OpticalPort(sname = 'Fr', pchain = 'Bk')

    @declarative.dproperty
    def Bk(self):
        return ports.OpticalPort(sname = 'Bk', pchain = 'Fr')

    @declarative.dproperty
    def Drv(self):
        return ports.SignalInPort(sname = 'Drv')

    @declarative.dproperty
    def BA(self):
        return ports.SignalOutPort(sname = 'BA')

    @declarative.mproperty
    def ports_optical(self):
        return set([
            self.Fr,
            self.Bk,
        ])

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.Fr.i : [self.Bk.o],
            self.Bk.i : [self.Fr.o],
            self.Fr.o : [self.Bk.i],
            self.Bk.o : [self.Fr.i],
        }

        #direct couplings
        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                for pto in pmap[port.i]:
                    ports_algorithm.port_coupling_needed(pto, kfrom)
            for kto in ports_algorithm.port_update_get(port.o):
                for pfrom in pmap[port.o]:
                    ports_algorithm.port_coupling_needed(pfrom, kto)

        nonlinear_utilities.ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            self.ports_optical,
            self.ports_optical,
            pmap,
            self.Drv.i,
            self.BA.o,
        )
        return

    def system_setup_coupling(self, matrix_algorithm):
        epsilon = sin**2(pi / 2 * P_in / P_nom)
        cmap = {
            self.Fr : (self.Bk, 1),
            self.Bk : (self.Fr, 1),
        }

        ports_in_optical = [
            self.Fr,
            self.Bk,
        ]

        for pfrom in ports_in_optical:
            for kfrom in matrix_algorithm.port_set_get(pfrom.i):
                ptoOpt, std_cplg = cmap[pfrom]
                std_cplgC = std_cplg

                nonlinear_utilities.modulations_fill_2optical_2classical(
                    self.system,
                    matrix_algorithm,
                    pfrom, kfrom,
                    ptoOpt,
                    self.Drv.i,
                    self.BA.o,
                    std_cplg,
                    std_cplgC,
                    1 / 2,
                    1 / 2,
                    self.symbols.i / self.symbols.c_m_s,
                    -self.symbols.i / self.symbols.c_m_s,
                )
        return

