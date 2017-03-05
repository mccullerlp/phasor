# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
#from BGSF.utilities.print import print

import declarative as decl

from . import bases
from . import ports
from . import nonlinear_utilities

#TODO
#class AOM(OpticalCouplerBase):


class Optical2PortModulator(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):
    @decl.dproperty
    def Fr(self):
        return ports.OpticalPort(sname = 'Fr', pchain = 'Bk')

    @decl.dproperty
    def Bk(self):
        return ports.OpticalPort(sname = 'Bk', pchain = 'Fr')

    @decl.dproperty
    def Drv(self):
        return ports.SignalInPort(sname = 'Drv')

    @decl.dproperty
    def BA(self):
        return ports.SignalOutPort(sname = 'BA')

    @decl.mproperty
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
            self.Drv,
            self.BA,
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
                    self.Drv,
                    self.BA,
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
                    self.Drv,
                    self.BA,
                    std_cplg,
                    std_cplgC,
                    1 / 2,
                    1 / 2,
                    self.symbols.i / self.symbols.c_m_s,
                    -self.symbols.i / self.symbols.c_m_s,
                )
        return


#class EOM(Optical2PortModulator):
#    polarization = ports.PolS
#
#    def system_setup_ports(self, system):
#        pmap = {
#            self.FrA.i : [self.FrB.o],
#            self.FrB.i : [self.FrA.o],
#            self.FrA.o : [self.FrB.i],
#            self.FrB.o : [self.FrA.i],
#        }
#
#        #direct couplings
#        for port in self.ports_optical:
#            for kfrom in system.port_update_get(port.i):
#                for pto in pmap[port.i]:
#                    system.port_coupling_needed(pto, kfrom)
#            for kto in system.port_update_get(port.o):
#                for pfrom in pmap[port.o]:
#                    system.port_coupling_needed(pfrom, kfrom)
#
#        nonlinear_utilities.ports_fill_2optical_2classical(
#            system,
#            self.ports_optical,
#            self.ports_optical,
#            pmap,
#            self.Drv,
#            self.BA,
#            select_in = TODO,
#        )
#        return
#
#    def system_setup_coupling(self, system):
#        cmap = {
#            self.Fr : (self.FrB, 1),
#            self.Bk : (self.BkB, 1),
#        }
#
#        for port in self.ports_optical:
#            for kfrom in system.port_set_get(port.i):
#                ptoOpt, std_cplg = cmap[port.i]
#                std_cplgC = std_cplg
#
#                if kfrom.contains(self.polarization):
#                    nonlinear_utilities.modulations_fill_2optical_2classical(
#                        system,
#                        port, kfrom,
#                        ptoOpt,
#                        self.posZ.i,
#                        self.forceZ.o,
#                        std_cplg,
#                        std_cplgC,
#                        self.symbols.i,
#                        -self.symbols.i,
#                        1 / self.symbols.c_m_s,
#                        1 / self.symbols.c_m_s,
#                    )
#                else:
#                    if kfrom.contains(ports.LOWER):
#                        system.port_coupling_insert(port.i, kfrom, ptoOpt.o, kfrom, std_cplg)
#                    else:
#                        system.port_coupling_insert(port.i, kfrom, ptoOpt.o, kfrom, std_cplgC)
#        return
#
