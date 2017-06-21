# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
#from phasor.utilities.print import print
import numpy as np
import declarative as decl

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
)

from . import ports
from . import nonlinear_utilities


class PPKTP(ports.OpticalSymmetric2PortMixin, OpticalCouplerBase, SystemElementBase):
    dn_dT_r_25deg = 1.4774e-5
    dn_dT_g_25deg = 2.4188e-5
    n_r = 1.830
    n_g = 1.889
    alpha_KTP = 6.7e-6

    def __init__(
        self,
        facing_cardinal = None,
        L = 0,
        Lc_m = 1e-2,
        wedge_angle_rad = 0,
        **kwargs
    ):
        super(PPKTP, self).__init__(**kwargs)

        self.Lc_m = 1e-2,
        poling_spacing = wavelen_r_m / (2 * (self.n_g - self.n_r))

        #optic mechanical ports
        self.Theat = ports.MechanicalPortHolderIn(self, x = 'T')
        self.Qheat = ports.MechanicalPortHolderOut(self, x = 'Q')

        self.is_4_port = False
        self.po_Fr   = ports.OpticalPort(sname = 'po_Fr' )
        self.po_Bk   = ports.OpticalPort(sname = 'po_Bk' )
        self._LFr = ports.OpticalPort(sname = 'LFr')
        self._LBk = ports.OpticalPort(sname = 'LBk')
        return

    def phase_mismatch(self):
        #page 114 of Etic's thesis
        #L_c * \Delta k
        #this is nominally zero
        phi = 2 * np.pi * self.L_c * (2 / wavelen_m * (self.n_g - self.n_r) - 1 / self.poling_spacing)
        return phi

    def d_phase_dT(self):
        return 2 * 2 * np.pi / wavelen_m * self.Lc_m * (self.alpha_KTP * (self.n_g - self.n_r) * self.dn_dT_g_25deg + self.dn_dT_r_25deg)

    def d_phase_dY(self):
        return 2 * 2 * np.pi / wavelen_m * self.Lc_m * (self.alpha_KTP * (self.n_g - self.n_r) * self.dn_dT_g_25deg + self.dn_dT_r_25deg)

    @decl.mproperty
    def ports_optical(self):
        return [
            self.po_Fr,
            self.po_Bk,
        ]

    @mproperty
    def ports_optical_loss(self):
        return [
            self._LFr,
            self._LBk,
        ]

    def system_setup_ports(self, system):
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

        #direct couplings
        for port in self.ports_optical:
            for kfrom in system.port_update_get(port.i):
                system.port_coupling_needed(tmap[port].o, kfrom)
                system.port_coupling_needed(lmap[port].o, kfrom)
                system.port_coupling_needed(rmap[port].o, kfrom)
            for kto in system.port_update_get(port.o):
                system.port_coupling_needed(tmap[port].i, kto)
                system.port_coupling_needed(lmap[port].i, kto)
                system.port_coupling_needed(rmap[port].i, kto)

        nonlinear_utilities.ports_fill_2optical_2classical(
            system,
            self.ports_optical,
            self.ports_optical,
            rmapL,
            self.posZ,
            self.forceZ,
        )
        return

    def system_setup_coupling(self, system):
        t     = +system.math.sqrt(self.T_hr)
        r     = +system.math.sqrt(self.R_hr)
        r_neg = -system.math.sqrt(self.R_hr)
        l     = +system.math.sqrt(self.L_hr)

        tmap = {
            self.po_FrA: (self.po_BkA   , t),
            self.po_BkA: (self.po_FrA   , t),
            self.po_FrB: (self.po_BkB   , t),
            self.po_BkB: (self.po_FrB   , t),
        }

        rmap = {
            self.po_FrA: (self.po_FrB   , r),
            self.po_BkA: (self.po_BkB   , r_neg),
            self.po_FrB: (self.po_FrA   , r),
            self.po_BkB: (self.po_BkA   , r_neg),
        }

        lmap = {
            self._LFrA: (self.po_FrA   , l),
            self._LBkA: (self.po_BkA   , l),
            self.po_FrA  : (self._LFrA , l),
            self.po_BkA  : (self._LBkA , l),
            self._LFrB: (self.po_FrB   , l),
            self._LBkB: (self.po_BkB   , l),
            self.po_FrB  : (self._LFrB , l),
            self.po_BkB  : (self._LBkB , l),
        }

        if self.AOI_deg != 0:
            if self.AOI_deg == 45:
                coupling = 1/2**.5
            else:
                coupling = system.math.cos(self.AOI_deg * system.pi / 180)
            couplingC = coupling
        else:
            coupling = 1
            couplingC = coupling

        for port in self.ports_optical:
            for kfrom in system.port_set_get(port.i):
                pto, cplg = tmap[port]
                system.port_coupling_insert(
                    port.i,
                    kfrom,
                    pto.o,
                    kfrom,
                    cplg,
                )

                pto, cplg = lmap[port]
                system.port_coupling_insert(
                    port.i,
                    kfrom,
                    pto.o,
                    kfrom,
                    cplg,
                )
                system.port_coupling_insert(
                    pto.i,
                    kfrom,
                    port.o,
                    kfrom,
                    cplg,
                )

                iwavelen_m, freq = system.optical_frequency_extract(kfrom)
                index_coupling  = -2 * coupling * system.pi * 2 * iwavelen_m
                index_couplingC = -2 * couplingC * system.pi * 2 * iwavelen_m
                force_coupling  = -2 * coupling
                force_couplingC = -2 * couplingC
                ptoOpt, R_cplgF  = rmap[port]

                R_cplg   = R_cplgF
                R_cplgC  = R_cplg

                nonlinear_utilities.modulations_fill_2optical_2classical(
                    system,
                    port, kfrom,
                    ptoOpt,
                    self.posZ,
                    self.forceZ,
                    R_cplg,
                    R_cplgC,
                    +system.i * index_coupling,
                    -system.i * index_couplingC,
                    force_coupling / system.c_m_s,
                    force_couplingC / system.c_m_s,
                )
        #now do updates to the loss cross
        return

