# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from phasor.utilities.print import print
import numpy as np

import declarative

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
)

from . import ports
from . import standard_attrs

from .nonlinear_utilities import (
    ports_fill_2optical_2classical,
    modulations_fill_2optical_2classical,
)

from .vacuum import (
    VacuumTerminator
)


from .. import mechanical


class Mirror(
    ports.OpticalDegenerate4PortMixin,
    OpticalCouplerBase,
    SystemElementBase
):
    unitary_loss = False

    phase = standard_attrs.generate_rotate(name = 'phase')
    _phase_default = ('phase_rad', 0)

    backscatter_phase = standard_attrs.generate_rotate(name = 'backscatter_phase')
    _backscatter_phase_default = ('backscatter_phase_rad', 0)

    @declarative.dproperty
    def flip_sign(self, val = False):
        return val

    @declarative.dproperty
    def R_backscatter(self, val = 0):
        val = self.ctree.setdefault('R_backscatter', val)
        return val

    @declarative.dproperty
    def T_hr(self, val = 0):
        val = self.ctree.setdefault('T_hr', val)
        return val

    @declarative.dproperty
    def L_hr(self, val = 0):
        val = self.ctree.setdefault('L_hr', val)
        return val

    @declarative.dproperty
    def L_t(self, val = 0):
        val = self.ctree.setdefault('L_t', val)
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

    @declarative.dproperty
    def Z(self):
        mechport = mechanical.MechanicalPortDriven(
            t_terminator = mechanical.TerminatorShorted,
        )
        return mechport

    @declarative.dproperty
    def _Z_setup(self):
        #separated from Z just so that the port object is generated through the dproperty mechanism
        self.system.own_port_virtual(self, self.Z.F.i)
        self.system.own_port_virtual(self, self.Z.d.o)

    @declarative.dproperty
    def po_Fr(self):
        if not self.is_4_port:
            return ports.OpticalPort(sname = 'po_Fr', pchain = 'po_Bk')
        else:
            return None

    @declarative.dproperty
    def po_Bk(self):
        if not self.is_4_port:
            return ports.OpticalPort(sname = 'po_Bk', pchain = 'po_Fr')
        else:
            return None

    @declarative.dproperty
    def _LFr(self):
        if self._has_loss and not self.is_4_port:
            return ports.OpticalPort(sname = 'LFr')

    @declarative.dproperty
    def _LBk(self):
        if self._has_loss and not self.is_4_port:
            return ports.OpticalPort(sname = 'LBk')

    @declarative.dproperty
    def _LFrA_vac(self):
        return VacuumTerminator()

    @declarative.dproperty
    def _LBkA_vac(self):
        return VacuumTerminator()

    @declarative.dproperty
    def _LFrB_vac(self):
        if self.is_4_port:
            return VacuumTerminator()

    @declarative.dproperty
    def _LBkB_vac(self):
        if self.is_4_port:
            return VacuumTerminator()

    @declarative.dproperty
    def po_FrA(self):
        if self.is_4_port:
            return ports.OpticalPort(sname = 'po_FrA', pchain = 'po_BkA')
        else:
            return self.po_Fr

    @declarative.dproperty
    def po_FrB(self):
        if self.is_4_port:
            return ports.OpticalPort(sname = 'po_FrB', pchain = 'po_BkB')
        else:
            return self.po_Fr

    @declarative.dproperty
    def po_BkA(self):
        if self.is_4_port:
            return ports.OpticalPort(sname = 'po_BkA', pchain = 'po_FrA')
        else:
            return self.po_Bk

    @declarative.dproperty
    def po_BkB(self):
        if self.is_4_port:
            return ports.OpticalPort(sname = 'po_BkB', pchain = 'po_FrB')
        else:
            return self.po_Bk

    @declarative.dproperty
    def _LFrA(self):
        if self._has_loss and self.is_4_port:
            return ports.OpticalPort(sname = 'LFrA' )
        else:
            return self._LFr

    @declarative.dproperty
    def _LFrB(self):
        if self._has_loss and self.is_4_port:
            return ports.OpticalPort(sname = 'LFrB' )
        else:
            return self._LFr

    @declarative.dproperty
    def _LBkA(self):
        if self._has_loss and self.is_4_port:
            return ports.OpticalPort(sname = 'LBkA' )
        else:
            return self._LBk

    @declarative.dproperty
    def _LBkB(self):
        if self._has_loss and self.is_4_port:
            return ports.OpticalPort(sname = 'LBkB' )
        else:
            return self._LBk

    @declarative.dproperty
    def _link(self):
        if self._has_loss:
            self.system.bond(self._LFrA, self._LFrA_vac.po_Fr)
            self.system.bond(self._LBkA, self._LBkA_vac.po_Fr)
            if self.is_4_port:
                self.system.bond(self._LFrB, self._LFrB_vac.po_Fr)
                self.system.bond(self._LBkB, self._LBkB_vac.po_Fr)

    @declarative.mproperty
    def ports_select(self):
        return [
            self.po_Fr,
            self.po_Bk,
            self.po_FrA,
            self.po_BkA,
            self.po_FrB,
            self.po_BkB,
        ]

    @declarative.mproperty
    def ports_optical(self):
        return set([
            self.po_FrA,
            self.po_BkA,
            self.po_FrB,
            self.po_BkB,
        ])

    @declarative.mproperty
    def ports_optical_loss(self):
        return set([
            self._LFrA,
            self._LBkA,
            self._LFrB,
            self._LBkB,
        ])

    @declarative.mproperty
    def _has_loss(self):
        return np.any(self.L_hr != 0) or np.any(self.L_t != 0)

    def system_setup_ports(self, ports_algorithm):
        tmap = {
            self.po_FrA: self.po_BkA,
            self.po_BkA: self.po_FrA,
            self.po_FrB: self.po_BkB,
            self.po_BkB: self.po_FrB,
        }

        rmap = {
            self.po_FrA: self.po_FrB,
            self.po_BkA: self.po_BkB,
            self.po_FrB: self.po_FrA,
            self.po_BkB: self.po_BkA,
        }

        rBSmap = {
            self.po_FrA: self.po_FrA,
            self.po_BkA: self.po_BkA,
            self.po_FrB: self.po_FrB,
            self.po_BkB: self.po_BkB,
        }

        lmap = {
            self.po_FrA: self._LFrA,
            self.po_BkA: self._LBkA,
            self.po_FrB: self._LFrB,
            self.po_BkB: self._LBkB,
            self._LFrA: self.po_FrA,
            self._LBkA: self.po_BkA,
            self._LFrB: self.po_FrB,
            self._LBkB: self.po_BkB,
        }
        rmapL = dict((k.i, [v.o]) for k, v in list(rmap.items()))
        rmapL.update((k.o, [v.i]) for k, v in list(rmap.items()))

        #TODO these will have to be made symbolic compatible
        R = 1 - self.T_hr - self.L_hr - self.R_backscatter
        R_nonzero = np.any(R != 0)

        T = self.T_hr - self.L_t
        T_nonzero = np.any(T != 0)

        #direct couplings
        #TODO some of these may be excessive, need more test cases
        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(port.o, kfrom)
                if T_nonzero:
                    ports_algorithm.port_coupling_needed(tmap[port].o, kfrom)
                if self._has_loss:
                    ports_algorithm.port_coupling_needed(lmap[port].o, kfrom)
                if R_nonzero:
                    ports_algorithm.port_coupling_needed(rmap[port].o, kfrom)
                if self.R_backscatter != 0:
                    ports_algorithm.port_coupling_needed(rBSmap[port].o, kfrom)
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(port.i, kto)
                if T_nonzero:
                    ports_algorithm.port_coupling_needed(tmap[port].i, kto)
                if self._has_loss:
                    ports_algorithm.port_coupling_needed(lmap[port].i, kto)
                if R_nonzero:
                    ports_algorithm.port_coupling_needed(rmap[port].i, kto)
                if self.R_backscatter != 0:
                    ports_algorithm.port_coupling_needed(rBSmap[port].i, kto)

        if self._has_loss:
            for port in self.ports_optical_loss:
                for kfrom in ports_algorithm.port_update_get(port.i):
                    ports_algorithm.port_coupling_needed(port.o, kfrom)
                    ports_algorithm.port_coupling_needed(lmap[port].o, kfrom)
                for kto in ports_algorithm.port_update_get(port.o):
                    ports_algorithm.port_coupling_needed(port.o, kto)
                    ports_algorithm.port_coupling_needed(lmap[port].i, kto)

        ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            self.ports_optical,
            self.ports_optical,
            rmapL,
            self.Z.d.o,
            self.Z.F.i,
        )
        return

    def system_setup_coupling(self, matrix_algorithm):

        T = self.T_hr - self.L_t
        L = self.L_hr + self.L_t
        R = 1 - self.T_hr - self.L_hr - self.R_backscatter

        t   = +self.symbols.math.sqrt(T)
        l   = +self.symbols.math.sqrt(L)
        lT  = +self.symbols.math.sqrt(1 - L)
        r   = self.symbols.math.sqrt(R)
        rBS = self.symbols.math.sqrt(self.R_backscatter)

        #TODO these will have to be made symbolic compatible
        R_nonzero = np.any(R != 0)
        T_nonzero = np.any(T != 0)
        rBS_nonzero = np.any(self.R_backscatter != 0)

        if self.flip_sign:
            r   = -r
            rBS = -rBS

        mod_sign_map = {
            self.po_FrA: 1,
            self.po_BkA: -1,
            self.po_FrB: 1,
            self.po_BkB: -1,
        }

        tmap = {
            self.po_FrA: (self.po_BkA   , t),
            self.po_BkA: (self.po_FrA   , t),
            self.po_FrB: (self.po_BkB   , t),
            self.po_BkB: (self.po_FrB   , t),
        }
        rmap = {
            self.po_FrA: (self.po_FrB   , r),
            self.po_BkA: (self.po_BkB   , -r),
            self.po_FrB: (self.po_FrA   , r),
            self.po_BkB: (self.po_BkA   , -r),
        }
        rBSmap = {
            self.po_FrA: (self.po_FrA   , rBS),
            self.po_FrB: (self.po_FrB   , -rBS),
            self.po_BkA: (self.po_BkA   , -rBS),
            self.po_BkB: (self.po_BkB   , rBS),
        }
        lmap = {
            self._LFrA: (self.po_FrA   , l),
            self._LBkA: (self.po_BkA   , l),
            self._LFrB: (self.po_FrB   , l),
            self._LBkB: (self.po_BkB   , l),
        }
        if self.unitary_loss:
            raise NotImplementedError("Needs to add phases to property account for fully unitary loss.")
            lmap.update({
                self.po_FrA  : (self._LFrA , l),
                self.po_BkA  : (self._LBkA , l),
                self.po_FrB  : (self._LFrB , l),
                self.po_BkB  : (self._LBkB , l),
                self._LFrA: (self._LFrA , lT),
                self._LBkA: (self._LBkA , lT),
                self._LFrB: (self._LFrB , lT),
                self._LBkB: (self._LBkB , lT),
            })

        if self.AOI_deg != 0:
            if self.AOI_deg == 45:
                coupling = 1 / 2**.5
            else:
                coupling = self.symbols.math.cos(self.AOI_deg * self.symbols.pi / 180)
            couplingC = coupling
        else:
            coupling = 1
            couplingC = coupling

        for port in self.ports_optical:
            mod_sign = mod_sign_map[port]
            for kfrom in matrix_algorithm.port_set_get(port.i):
                if T_nonzero:
                    pto, cplg = tmap[port]
                    matrix_algorithm.port_coupling_insert(
                        port.i,
                        kfrom,
                        pto.o,
                        kfrom,
                        cplg,
                    )

                if self._has_loss:
                    val = lmap.get(port, None)
                    if val is not None:
                        pto, cplg = val
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            pto.o,
                            kfrom,
                            cplg,
                        )

                iwavelen_m, freq = self.system.optical_frequency_extract(kfrom)
                index_coupling  = -2 * coupling * self.symbols.pi * 2 * iwavelen_m
                index_couplingC = -2 * couplingC * self.symbols.pi * 2 * iwavelen_m
                force_coupling  = -2 * coupling
                force_couplingC = -2 * couplingC
                ptoOpt, R_cplgF  = rmap[port]

                R_cplg   = R_cplgF
                R_cplgC  = R_cplg

                if np.any(self.phase_rad.val != 0):
                    R_cplg   = R_cplg * self.symbols.math.exp(self.symbols.i * self.phase_rad.val)
                    R_cplgC  = R_cplgC * self.symbols.math.exp(-self.symbols.i * self.phase_rad.val)

                #everything scales with Stdcplg, so don't run if there are no reflections
                if R_nonzero:
                    modulations_fill_2optical_2classical(
                        system             = self.system,
                        matrix_algorithm   = matrix_algorithm,
                        pfrom              = port,
                        kfrom              = kfrom,
                        ptoOpt             = ptoOpt,
                        in_port_classical  = self.Z.d.o,
                        out_port_classical = self.Z.F.i,
                        Stdcplg            = R_cplg,
                        StdcplgC           = R_cplgC,
                        CLcplg             = mod_sign * +self.symbols.i * index_coupling,
                        CLcplgC            = mod_sign * -self.symbols.i * index_couplingC,
                        BAcplg             = mod_sign * force_coupling / self.symbols.c_m_s,
                        BAcplgC            = mod_sign * force_couplingC / self.symbols.c_m_s,
                    )

                if rBS_nonzero:
                    ptoOpt, R_cplgF  = rBSmap[port]
                    R_cplg   = R_cplgF
                    R_cplgC  = R_cplg

                    if np.any(self.backscatter_phase_rad.val != 0):
                        R_cplg   = R_cplg * self.symbols.math.exp(self.symbols.i * self.phase_rad.val)
                        R_cplgC  = R_cplgC * self.symbols.math.exp(-self.symbols.i * self.phase_rad.val)

                    modulations_fill_2optical_2classical(
                        system             = self.system,
                        matrix_algorithm   = matrix_algorithm,
                        pfrom              = port,
                        kfrom              = kfrom,
                        ptoOpt             = ptoOpt,
                        in_port_classical  = self.Z.d.o,
                        out_port_classical = self.Z.F.i,
                        Stdcplg            = R_cplg,
                        StdcplgC           = R_cplgC,
                        CLcplg             = mod_sign * +self.symbols.i * index_coupling,
                        CLcplgC            = mod_sign * -self.symbols.i * index_couplingC,
                        BAcplg             = mod_sign * force_coupling / self.symbols.c_m_s,
                        BAcplgC            = mod_sign * force_couplingC / self.symbols.c_m_s,
                    )

        #to keep the matrix with loss ports unitary
        #really we need some phases
        #but if loss ports only keep incoherent noise, this will work
        if self._has_loss:
            for port in self.ports_optical_loss:
                pto, cplg = lmap.get(port)
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    matrix_algorithm.port_coupling_insert(
                        port.i,
                        kfrom,
                        pto.o,
                        kfrom,
                        cplg,
                    )
        return


