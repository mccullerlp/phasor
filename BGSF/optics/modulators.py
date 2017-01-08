# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

from declarative import (
    mproperty,
)

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
    #OOA_ASSIGN,
)

from .ports import (
    OpticalPortHolderInOut,
    SignalPortHolderIn,
    SignalPortHolderOut,
    QuantumKey, RAISE, LOWER,
    PolKEY, PolS, PolP,
    OpticalSymmetric2PortMixin,
)

from .nonlinear_utilities import (
    #symmetric_update,
    ports_fill_2optical_2classical,
    modulations_fill_2optical_2classical,
)



#TODO
#class AOM(OpticalCouplerBase):


class Optical2PortModulator(OpticalSymmetric2PortMixin, OpticalCouplerBase, SystemElementBase):
    def __init__(self, **kwargs):
        super(Optical2PortModulator, self).__init__(**kwargs)
        self.Fr   = OpticalPortHolderInOut(self, x = 'Fr')
        self.Bk   = OpticalPortHolderInOut(self, x = 'Bk')
        self.Drv  = SignalPortHolderIn(self, x = 'Drv')
        self.BA   = SignalPortHolderOut(self, x = 'BA')
        return

    @mproperty
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

        ports_fill_2optical_2classical(
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

                modulations_fill_2optical_2classical(
                    self.system,
                    matrix_algorithm,
                    pfrom, kfrom,
                    ptoOpt,
                    self.Drv,
                    self.BA,
                    std_cplg,
                    std_cplgC,
                    self.system.i / 2,
                    -self.system.i / 2,
                    1 / self.system.c_m_s,
                    1 / self.system.c_m_s,
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

                modulations_fill_2optical_2classical(
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
                    self.system.i / self.system.c_m_s,
                    -self.system.i / self.system.c_m_s,
                )
        return


#class EOM(Optical2PortModulator):
#    polarization = PolS
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
#        ports_fill_2optical_2classical(
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
#                    modulations_fill_2optical_2classical(
#                        system,
#                        port, kfrom,
#                        ptoOpt,
#                        self.posZ.i,
#                        self.forceZ.o,
#                        std_cplg,
#                        std_cplgC,
#                        self.system.i,
#                        -self.system.i,
#                        1 / self.system.c_m_s,
#                        1 / self.system.c_m_s,
#                    )
#                else:
#                    if kfrom.contains(LOWER):
#                        system.port_coupling_insert(port.i, kfrom, ptoOpt.o, kfrom, std_cplg)
#                    else:
#                        system.port_coupling_insert(port.i, kfrom, ptoOpt.o, kfrom, std_cplgC)
#        return
#
