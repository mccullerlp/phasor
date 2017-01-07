# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

from declarative import (
    mproperty,
)

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

from .ports import (
    OpticalPortHolderInOut,
    MechanicalPortHolderIn,
    MechanicalPortHolderOut,
    OpticalDegenerate4PortMixin,
)

from .nonlinear_utilities import (
    ports_fill_2optical_2classical,
    modulations_fill_2optical_2classical,
)

from .vacuum import (
    VacuumTerminator
)


class Mirror(
    OpticalDegenerate4PortMixin,
    OpticalCouplerBase,
    SystemElementBase
):
    def __init__(
        self,
        T_hr    = 0,
        L_hr    = 0,
        L_t     = 0,
        **kwargs
    ):
        super(Mirror, self).__init__(**kwargs)
        OOA_ASSIGN(self).T_hr    = T_hr
        OOA_ASSIGN(self).L_hr    = L_hr
        OOA_ASSIGN(self).L_t     = L_t

        #optic mechanical ports
        self.posZ     = MechanicalPortHolderIn(self, x = 'pZ')
        self.forceZ   = MechanicalPortHolderOut(self, x = 'fZ')
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

        #behave like a mirror if AOI_deg is 0 and only have a front and back port
        if not self.is_4_port:
            self.Fr   = OpticalPortHolderInOut(self, x = 'Fr' )
            self.Bk   = OpticalPortHolderInOut(self, x = 'Bk' )
            self._LFr = OpticalPortHolderInOut(self, x = 'LFr')
            self._LBk = OpticalPortHolderInOut(self, x = 'LBk')

            self._LFr_vac = VacuumTerminator()
            self._LBk_vac = VacuumTerminator()
            #TODO, not clear if linking from constructor here is OK
            self.system.link(self._LFr, self._LFr_vac.Fr)
            self.system.link(self._LBk, self._LBk_vac.Fr)
            #emulate BS ports, will raise an error if they are ever accidentally multiply assigned
            self.FrA = self.Fr
            self.FrB = self.Fr
            self.BkA = self.Bk
            self.BkB = self.Bk
            self._LFrA = self._LFr
            self._LFrB = self._LFr
            self._LBkA = self._LBk
            self._LBkB = self._LBk
        else:
            self.FrA   = OpticalPortHolderInOut(self, x = 'FrA' )
            self.FrB   = OpticalPortHolderInOut(self, x = 'FrB' )
            self.BkA   = OpticalPortHolderInOut(self, x = 'BkA' )
            self.BkB   = OpticalPortHolderInOut(self, x = 'BkB' )
            self._LFrA = OpticalPortHolderInOut(self, x = 'LFrA')
            self._LFrB = OpticalPortHolderInOut(self, x = 'LFrB')
            self._LBkA = OpticalPortHolderInOut(self, x = 'LBkA')
            self._LBkB = OpticalPortHolderInOut(self, x = 'LBkB')

            self._LFrA_vac = VacuumTerminator()
            self._LFrB_vac = VacuumTerminator()
            self._LBkA_vac = VacuumTerminator()
            self._LBkB_vac = VacuumTerminator()
            #TODO, not clear if linking from constructor here is OK
            self.system.link(self._LFrA, self._LFrA_vac.Fr)
            self.system.link(self._LFrB, self._LFrB_vac.Fr)
            self.system.link(self._LBkA, self._LBkA_vac.Fr)
            self.system.link(self._LBkB, self._LBkB_vac.Fr)
        return

    @mproperty
    def ports_optical(self):
        return set([
            self.FrA,
            self.BkA,
            self.FrB,
            self.BkB,
        ])

    @mproperty
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
        rmapL = dict((k.i, [v.o]) for k, v in rmap.items())
        rmapL.update((k.o, [v.i]) for k, v in rmap.items())

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


