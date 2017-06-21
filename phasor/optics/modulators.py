# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
#from phasor.utilities.print import print
import declarative

from . import bases
from . import ports
from . import nonlinear_utilities

class Optical2PortModulator(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):
    @declarative.dproperty
    def po_Fr(self):
        return ports.OpticalPort(pchain = 'po_Bk')

    @declarative.dproperty
    def po_Bk(self):
        return ports.OpticalPort(pchain = 'po_Fr')

    @declarative.dproperty
    def Drv(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def BA(self):
        return ports.SignalOutPort()

    @declarative.mproperty
    def ports_optical(self):
        return set([
            self.po_Fr,
            self.po_Bk,
        ])

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.po_Fr.i : [self.po_Bk.o],
            self.po_Bk.i : [self.po_Fr.o],
            self.po_Fr.o : [self.po_Bk.i],
            self.po_Bk.o : [self.po_Fr.i],
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
    @declarative.mproperty
    def DrvPM(self):
        return self.Drv

    @declarative.mproperty
    def DrvFM(self):
        return self.FM2PM.ps_In

    @declarative.dproperty
    def FM2PM(self):
        from .. import signals
        return signals.Integrator()

    @declarative.dproperty
    def FM2PM_setup(self):
        self.FM2PM.ps_Out.bond(self.DrvPM)
        return

    def system_setup_coupling(self, matrix_algorithm):
        cmap = {
            self.po_Fr : (self.po_Bk, 1),
            self.po_Bk : (self.po_Fr, 1),
        }

        ports_in_optical = [
            self.po_Fr,
            self.po_Bk,
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
    @declarative.mproperty
    def DrvAM(self):
        return self.Drv

    def system_setup_coupling(self, matrix_algorithm):
        cmap = {
            self.po_Fr : (self.po_Bk, 1),
            self.po_Bk : (self.po_Fr, 1),
        }

        ports_in_optical = [
            self.po_Fr,
            self.po_Bk,
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


class AMPM(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):
    @declarative.dproperty
    def po_Fr(self):
        return ports.OpticalPort(pchain = 'po_Bk')

    @declarative.dproperty
    def po_Bk(self):
        return ports.OpticalPort(pchain = 'po_Fr')

    @declarative.dproperty
    def DrvAM(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def DrvPM(self):
        return ports.SignalInPort()

    @declarative.mproperty
    def DrvFM(self):
        return self.FM2PM.ps_In

    @declarative.dproperty
    def FM2PM(self):
        from .. import signals
        return signals.Integrator()

    @declarative.dproperty
    def FM2PM_setup(self):
        self.FM2PM.ps_Out.bond(self.DrvPM)
        return

    @declarative.mproperty
    def ports_optical(self):
        return set([
            self.po_Fr,
            self.po_Bk,
        ])

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.po_Fr.i : [self.po_Bk.o],
            self.po_Bk.i : [self.po_Fr.o],
            self.po_Fr.o : [self.po_Bk.i],
            self.po_Bk.o : [self.po_Fr.i],
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
            self.DrvAM.i,
            None,
        )

        nonlinear_utilities.ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            self.ports_optical,
            self.ports_optical,
            pmap,
            self.DrvPM.i,
            None,
        )
        return

    def system_setup_coupling(self, matrix_algorithm):
        cmap = {
            self.po_Fr : (self.po_Bk, 1),
            self.po_Bk : (self.po_Fr, 1),
        }

        ports_in_optical = [
            self.po_Fr,
            self.po_Bk,
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
                    self.DrvPM.i,
                    None,
                    std_cplg,
                    std_cplgC,
                    self.symbols.i / 2,
                    -self.symbols.i / 2,
                    1 / self.symbols.c_m_s,
                    1 / self.symbols.c_m_s,
                )
                nonlinear_utilities.modulations_fill_2optical_2classical(
                    self.system,
                    matrix_algorithm,
                    pfrom, kfrom,
                    ptoOpt,
                    self.DrvAM.i,
                    None,
                    std_cplg,
                    std_cplgC,
                    1 / 2,
                    1 / 2,
                    self.symbols.i / self.symbols.c_m_s,
                    -self.symbols.i / self.symbols.c_m_s,
                    include_through_coupling = False,
                )
        return
