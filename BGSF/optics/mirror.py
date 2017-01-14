# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
#from BGSF.utilities.print import print

import declarative as decl

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
)

from . import ports

from .nonlinear_utilities import (
    ports_fill_2optical_2classical,
    modulations_fill_2optical_2classical,
)

from .vacuum import (
    VacuumTerminator
)


class Mirror(
    ports.OpticalDegenerate4PortMixin,
    OpticalCouplerBase,
    SystemElementBase
):

    @decl.dproperty
    def T_hr(self, val = 0):
        val = self.ooa_params.setdefault('T_hr', val)
        return val

    @decl.dproperty
    def L_hr(self, val = 0):
        val = self.ooa_params.setdefault('L_hr', val)
        return val

    @decl.dproperty
    def L_t(self, val = 0):
        val = self.ooa_params.setdefault('L_t', val)
        return val

    #self.angleZ  = MechanicalPortHolder(self, x = 'aZ')
    #self.torqueZ = MechanicalPortHolder(self, x = 'tZ')
    #self.posX    = MechanicalPortHolder(self, x = 'pX')
    #self.forceX  = MechanicalPortHolder(self, x = 'fX')
    #self.angleX  = MechanicalPortHolder(self, x = 'aX')
    #self.torqueX = MechanicalPortHolder(self, x = 'tX')
    #self.posY    = MechanicalPortHolder(self, x = 'pY')
    #self.forceY  = MechanicalPortHolder(self, x = 'fY')
    #self.angleY  = MechanicalPortHolder(self, x = 'aY')
    #self.torqueY = MechanicalPortHolder(self, x = 'tY')

    @decl.dproperty
    def posZ(self):
        return ports.MechanicalPortHolderIn(self, x = 'pZ')

    @decl.dproperty
    def forceZ(self):
        return ports.MechanicalPortHolderOut(self, x = 'fZ')

    @decl.dproperty
    def Fr(self):
        if not self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'Fr', pchain = 'Bk')
        else:
            return None

    @decl.dproperty
    def Bk(self):
        if not self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'Bk', pchain = 'Fr')
        else:
            return None

    @decl.dproperty
    def _LFr(self):
        if not self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'LFr')

    @decl.dproperty
    def _LBk(self):
        if not self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'LBk')

    @decl.dproperty
    def _LFrA_vac(self):
        return VacuumTerminator()

    @decl.dproperty
    def _LBkA_vac(self):
        return VacuumTerminator()

    @decl.dproperty
    def _LFrB_vac(self):
        if self.is_4_port:
            return VacuumTerminator()

    @decl.dproperty
    def _LBkB_vac(self):
        if self.is_4_port:
            return VacuumTerminator()

    @decl.dproperty
    def FrA(self):
        if self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'FrA', pchain = 'BkA')
        else:
            return self.Fr

    @decl.dproperty
    def FrB(self):
        if self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'FrB', pchain = 'BkB')
        else:
            return self.Fr

    @decl.dproperty
    def BkA(self):
        if self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'BkA', pchain = 'FrA')
        else:
            return self.Bk

    @decl.dproperty
    def BkB(self):
        if self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'BkB', pchain = 'FrB')
        else:
            return self.Bk

    @decl.dproperty
    def _LFrA(self):
        if self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'LFrA' )
        else:
            return self._LFr

    @decl.dproperty
    def _LFrB(self):
        if self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'LFrB' )
        else:
            return self._LFr

    @decl.dproperty
    def _LBkA(self):
        if self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'LBkA' )
        else:
            return self._LBk

    @decl.dproperty
    def _LBkB(self):
        if self.is_4_port:
            return ports.OpticalPortHolderInOut(self, x = 'LBkB' )
        else:
            return self._LBk

    @decl.dproperty
    def _link(self):
        self.system.bond(self._LFrA, self._LFrA_vac.Fr)
        self.system.bond(self._LBkA, self._LBkA_vac.Fr)
        if self.is_4_port:
            self.system.bond(self._LFrB, self._LFrB_vac.Fr)
            self.system.bond(self._LBkB, self._LBkB_vac.Fr)

    @decl.mproperty
    def ports_optical(self):
        return set([
            self.FrA,
            self.BkA,
            self.FrB,
            self.BkB,
        ])

    @decl.mproperty
    def ports_optical_loss(self):
        return set([
            self._LFrA,
            self._LBkA,
            self._LFrB,
            self._LBkB,
        ])

    def system_setup_ports(self, ports_algorithm):
        tmap = {
            self.FrA: self.BkA,
            self.BkA: self.FrA,
            self.FrB: self.BkB,
            self.BkB: self.FrB,
        }

        rmap = {
            self.FrA: self.FrB,
            self.BkA: self.BkB,
            self.FrB: self.FrA,
            self.BkB: self.BkA,
        }

        lmap = {
            self.FrA: self._LFrA,
            self.BkA: self._LBkA,
            self.FrB: self._LFrB,
            self.BkB: self._LBkB,
            self._LFrA: self.FrA,
            self._LBkA: self.BkA,
            self._LFrB: self.FrB,
            self._LBkB: self.BkB,
        }
        rmapL = dict((k.i, [v.o]) for k, v in list(rmap.items()))
        rmapL.update((k.o, [v.i]) for k, v in list(rmap.items()))

        #direct couplings
        #TODO some of these may be excessive, need more test cases
        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(port.o, kfrom)
                ports_algorithm.port_coupling_needed(port.i, kfrom)
                ports_algorithm.port_coupling_needed(tmap[port].o, kfrom)
                ports_algorithm.port_coupling_needed(lmap[port].o, kfrom)
                ports_algorithm.port_coupling_needed(rmap[port].o, kfrom)
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(port.o, kto)
                ports_algorithm.port_coupling_needed(port.i, kto)
                ports_algorithm.port_coupling_needed(tmap[port].i, kto)
                ports_algorithm.port_coupling_needed(lmap[port].i, kto)
                ports_algorithm.port_coupling_needed(rmap[port].i, kto)

        for port in self.ports_optical_loss:
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(port.i, kfrom)
                ports_algorithm.port_coupling_needed(port.o, kfrom)
                ports_algorithm.port_coupling_needed(lmap[port].o, kfrom)
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(port.o, kto)
                ports_algorithm.port_coupling_needed(port.i, kto)
                ports_algorithm.port_coupling_needed(lmap[port].i, kto)

        ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            self.ports_optical,
            self.ports_optical,
            rmapL,
            self.posZ,
            self.forceZ,
        )
        return

    def system_setup_coupling(self, matrix_algorithm):

        T = self.T_hr - self.L_t
        L = self.L_hr + self.L_t
        R = 1 - T - L

        t     = +self.system.math.sqrt(T)
        r     = +self.system.math.sqrt(R)
        r_neg = -self.system.math.sqrt(R)
        l     = +self.system.math.sqrt(L)
        lT    = +self.system.math.sqrt(1 - L)

        mod_sign_map = {
            self.FrA: 1,
            self.BkA: -1,
            self.FrB: 1,
            self.BkB: -1,
        }

        tmap = {
            self.FrA: (self.BkA   , t),
            self.BkA: (self.FrA   , t),
            self.FrB: (self.BkB   , t),
            self.BkB: (self.FrB   , t),
        }

        rmap = {
            self.FrA: (self.FrB   , r),
            self.BkA: (self.BkB   , r_neg),
            self.FrB: (self.FrA   , r),
            self.BkB: (self.BkA   , r_neg),
        }

        lmap = {
            self._LFrA: (self.FrA   , l),
            self._LBkA: (self.BkA   , l),
            self.FrA  : (self._LFrA , l),
            self.BkA  : (self._LBkA , l),
            self._LFrB: (self.FrB   , l),
            self._LBkB: (self.BkB   , l),
            self.FrB  : (self._LFrB , l),
            self.BkB  : (self._LBkB , l),
        }

        if self.AOI_deg != 0:
            if self.AOI_deg == 45:
                coupling = 1 / 2**.5
            else:
                coupling = self.system.math.cos(self.AOI_deg * self.system.pi / 180)
            couplingC = coupling
        else:
            coupling = 1
            couplingC = coupling

        for port in self.ports_optical:
            mod_sign = mod_sign_map[port]
            for kfrom in matrix_algorithm.port_set_get(port.i):
                pto, cplg = tmap[port]
                matrix_algorithm.port_coupling_insert(
                    port.i,
                    kfrom,
                    pto.o,
                    kfrom,
                    cplg,
                )

                pto, cplg = lmap[port]
                matrix_algorithm.port_coupling_insert(
                    port.i,
                    kfrom,
                    pto.o,
                    kfrom,
                    cplg,
                )
                matrix_algorithm.port_coupling_insert(
                    pto.i,
                    kfrom,
                    port.o,
                    kfrom,
                    cplg,
                )

                iwavelen_m, freq = self.system.optical_frequency_extract(kfrom)
                index_coupling  = -2 * coupling * self.system.pi * 2 * iwavelen_m
                index_couplingC = -2 * couplingC * self.system.pi * 2 * iwavelen_m
                force_coupling  = -2 * coupling
                force_couplingC = -2 * couplingC
                ptoOpt, R_cplgF  = rmap[port]

                R_cplg   = R_cplgF
                R_cplgC  = R_cplg

                modulations_fill_2optical_2classical(
                    self.system,
                    matrix_algorithm,
                    port, kfrom,
                    ptoOpt,
                    self.posZ,
                    self.forceZ,
                    R_cplg,
                    R_cplgC,
                    mod_sign * +self.system.i * index_coupling,
                    mod_sign * -self.system.i * index_couplingC,
                    mod_sign * force_coupling / self.system.c_m_s,
                    mod_sign * force_couplingC / self.system.c_m_s,
                )

        #to keep the matrix with loss ports unitary
        for port in self.ports_optical_loss:
            for kfrom in matrix_algorithm.port_set_get(port.i):
                matrix_algorithm.port_coupling_insert(
                    port.i,
                    kfrom,
                    port.o,
                    kfrom,
                    lT,
                )
        return


