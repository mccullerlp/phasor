# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import declarative as decl

from .. import readouts
from . import ports
from . import bases
from . import vacuum
from . import nonlinear_utilities


class PD(
        bases.OpticalCouplerBase,
        bases.SystemElementBase
):

    @decl.mproperty
    def magic(self, val = False):
        return val

    @decl.dproperty
    def _fluct(self):
        return vacuum.OpticalVacuumFluctuation(
            port = self.po_Fr,
        )

    @decl.dproperty
    def include_readouts(self, val = False):
        val = self.ctree.setdefault('include_readouts', val)
        return val

    @decl.dproperty
    def DC(self):
        if self.include_readouts:
            return readouts.DCReadout(port = self.Wpd.o)

    @decl.dproperty
    def noise(self):
        if self.include_readouts:
            return readouts.NoiseReadout(portN = self.Wpd.o)

    @decl.dproperty
    def po_Fr(self):
        return ports.OpticalPort()

    @decl.dproperty
    def Wpd(self):
        return ports.SignalOutPort()

    @decl.dproperty
    def BA(self):
        if self.magic:
            return None
        else:
            return ports.SignalInPort(sname = 'BA')

    @decl.dproperty
    def po_Bk(self):
        if self.magic:
            return ports.OpticalPort(sname = 'po_Bk')

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.po_Fr.i : []
        }

        nonlinear_utilities.ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            [self.po_Fr],
            [],
            pmap,
            self.BA.i,
            self.Wpd.o,
        )
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.po_Fr.i):
            std_cplg  = 1
            std_cplgC = std_cplg

            nonlinear_utilities.modulations_fill_2optical_2classical(
                self.system,
                matrix_algorithm,
                self.po_Fr, kfrom,
                None,
                self.BA.i,
                self.Wpd.o,
                std_cplg,
                std_cplgC,
                +self.symbols.i,
                -self.symbols.i,
                1,
                1,
            )
        return


class MagicPD(
        bases.OpticalCouplerBase,
        bases.SystemElementBase
):

    @decl.dproperty
    def po_Fr(self):
        return ports.OpticalPort(pchain = 'po_Bk')

    @decl.dproperty
    def Wpd(self):
        return ports.SignalOutPort()

    @decl.dproperty
    def po_Bk(self):
        return ports.OpticalPort(pchain = 'po_Fr')

    @decl.dproperty
    def include_readouts(self, val = False):
        val = self.ctree.setdefault('include_readouts', val)
        return val

    @decl.dproperty
    def DC(self):
        if self.include_readouts:
            return readouts.DCReadout(port = self.Wpd.o)

    @decl.dproperty
    def noise(self):
        if self.include_readouts:
            return readouts.NoiseReadout(portN = self.Wpd.o)

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.po_Fr.i : [self.po_Bk.o],
            self.po_Fr.o : [self.po_Bk.i],
            self.po_Bk.i : [self.po_Fr.o],
            self.po_Bk.o : [self.po_Fr.i],
        }

        nonlinear_utilities.ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            [self.po_Fr],
            [self.po_Bk],
            pmap,
            None,
            self.Wpd.o,
        )

        for kfrom in ports_algorithm.port_update_get(self.po_Bk.i):
            ports_algorithm.port_coupling_needed(pmap[self.po_Bk.i][0], kfrom)
        for kto in ports_algorithm.port_update_get(self.po_Bk.o):
            ports_algorithm.port_coupling_needed(pmap[self.po_Bk.o][0], kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.po_Fr.i):
            std_cplg  = 1
            std_cplgC = std_cplg

            nonlinear_utilities.modulations_fill_2optical_2classical(
                self.system,
                matrix_algorithm,
                self.po_Fr, kfrom,
                self.po_Bk,
                None,
                self.Wpd.o,
                std_cplg,
                std_cplgC,
                0,
                0,
                1,
                1,
            )
        for kfrom in matrix_algorithm.port_set_get(self.po_Bk.i):
            matrix_algorithm.port_coupling_insert(self.po_Bk.i, kfrom, self.po_Fr.o, kfrom, 1)
        #Dont need a second for-loop here since the direct coupling is included with modulations_fill_2optical_2classical
        return


