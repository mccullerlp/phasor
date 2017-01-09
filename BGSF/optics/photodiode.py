# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

import declarative as decl

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

from . import ports

from .nonlinear_utilities import (
    #symmetric_update,
    ports_fill_2optical_2classical,
    modulations_fill_2optical_2classical,
)

from ..readouts import (
    DCReadout,
    #ACReadout,
    NoiseReadout,
)

from .vacuum import (
    OpticalVacuumFluctuation,
)


class PD(ports.OpticalNonOriented1PortMixin, OpticalCouplerBase, SystemElementBase):

    @decl.mproperty
    def magic(self, val = False):
        return val

    @decl.dproperty
    def _fluct(self):
        return OpticalVacuumFluctuation(port = self.Fr)

    @decl.dproperty
    def include_readouts(self, val = False):
        val = self.ooa_params.setdefault('include_readouts', val)
        return val

    @decl.dproperty
    def DC(self):
        if self.include_readouts:
            return DCReadout(port = self.Wpd.o)

    @decl.dproperty
    def noise(self):
        if self.include_readouts:
            return NoiseReadout(portN = self.Wpd.o)

    @decl.dproperty
    def Fr(self):
        return ports.OpticalPortHolderInOut(self, x = 'Fr')

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
            return ports.OpticalPortHolderInOut(self, x = 'Bk')

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.Fr.i : []
        }

        ports_fill_2optical_2classical(
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

            modulations_fill_2optical_2classical(
                self.system,
                matrix_algorithm,
                self.Fr, kfrom,
                None,
                self.BA,
                self.Wpd,
                std_cplg,
                std_cplgC,
                +self.system.i,
                -self.system.i,
                1,
                1,
            )
        return


class MagicPD(ports.OpticalOriented2PortMixin, OpticalCouplerBase, SystemElementBase):
    def __init__(
            self,
            include_readouts = False,
            **kwargs
    ):
        super(MagicPD, self).__init__(**kwargs)
        self.Fr   = ports.OpticalPortHolderInOut(self, x = 'Fr')
        self.Bk   = ports.OpticalPortHolderInOut(self, x = 'Bk')
        self.Wpd  = ports.SignalPortHolderOut(self, x = 'Wpd')

        OOA_ASSIGN(self).include_readouts = include_readouts
        if self.include_readouts:
            self.DC    = DCReadout(port = self.Wpd.o)
            self.noise = NoiseReadout(portN = self.Wpd.o)
        return

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.Fr.i : [self.Bk.o],
            self.Fr.o : [self.Bk.i],
            self.Bk.i : [self.Fr.o],
            self.Bk.o : [self.Fr.i],
        }

        ports_fill_2optical_2classical(
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

            modulations_fill_2optical_2classical(
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


