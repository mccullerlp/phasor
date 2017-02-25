# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
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
        return vacuum.OpticalVacuumFluctuation(port = self.Fr)

    @decl.dproperty
    def include_readouts(self, val = False):
        val = self.ooa_params.setdefault('include_readouts', val)
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
    def Fr(self):
        return ports.OpticalPortHolderInOut(sname = 'Fr')

    @decl.dproperty
    def Wpd(self):
        return ports.SignalPortHolderOut(self, x    = 'Wpd')

    @decl.dproperty
    def BA(self):
        if self.magic:
            self.BA = None
        else:
            self.BA  = ports.SignalPortHolderIn(self,  x = 'BA')

    @decl.dproperty
    def Bk(self):
        if self.magic:
            return ports.OpticalPortHolderInOut(sname = 'Bk')

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.Fr.i : []
        }

        nonlinear_utilities.ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            [self.Fr],
            [],
            pmap,
            self.BA,
            self.Wpd,
        )
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.Fr.i):
            std_cplg  = 1
            std_cplgC = std_cplg

            nonlinear_utilities.modulations_fill_2optical_2classical(
                self.system,
                matrix_algorithm,
                self.Fr, kfrom,
                None,
                self.BA,
                self.Wpd,
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
    def Fr(self):
        return ports.OpticalPortHolderInOut(sname = 'Fr', pchain = 'Bk')

    @decl.dproperty
    def Wpd(self):
        return ports.SignalPortHolderOut(self, x = 'Wpd')

    @decl.dproperty
    def Bk(self):
        return ports.OpticalPortHolderInOut(sname = 'Bk', pchain = 'Fr')

    @decl.dproperty
    def include_readouts(self, val = False):
        val = self.ooa_params.setdefault('include_readouts', val)
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
            self.Fr.i : [self.Bk.o],
            self.Fr.o : [self.Bk.i],
            self.Bk.i : [self.Fr.o],
            self.Bk.o : [self.Fr.i],
        }

        nonlinear_utilities.ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            [self.Fr],
            [self.Fr],
            pmap,
            None,
            self.Wpd,
        )

        for kfrom in ports_algorithm.port_update_get(self.Bk.i):
            ports_algorithm.port_coupling_needed(pmap[self.Bk.i][0], kfrom)
        for kto in ports_algorithm.port_update_get(self.Bk.o):
            ports_algorithm.port_coupling_needed(pmap[self.Bk.o][0], kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.Fr.i):
            std_cplg  = 1
            std_cplgC = std_cplg

            nonlinear_utilities.modulations_fill_2optical_2classical(
                self.system,
                matrix_algorithm,
                self.Fr, kfrom,
                self.Bk,
                None,
                self.Wpd,
                std_cplg,
                std_cplgC,
                0,
                0,
                1,
                1,
            )
        for kfrom in matrix_algorithm.port_set_get(self.Bk.i):
            matrix_algorithm.port_coupling_insert(self.Bk.i, kfrom, self.Fr.o, kfrom, 1)
        #Dont need a second for-loop here since the direct coupling is included with modulations_fill_2optical_2classical
        return


