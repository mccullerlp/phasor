# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import declarative as decl

from . import bases
from . import ports
from . import polarization as pol


class FaradayIsolator(
        ports.OpticalOriented2PortMixin,
        bases.OpticalCouplerBase,
        bases.SystemElementBase
):

    @decl.dproperty
    def pol_from(self, val = 'S'):
        val = self.ctree.setdefault('pol_from', val)
        return val

    @decl.dproperty
    def pol_to(self, val = 'S'):
        val = self.ctree.setdefault('pol_from', val)
        return val

    def __build__(self):
        self.pol_BS_in  = pol.PolarizingBeamsplitter(
            pass_polarization = self.pol_from,
        )

        self.faraday = pol.FaradayRotator()

        if self.pol_from == self.pol_to:
            rotate_sign = -1
        else:
            rotate_sign = 1

        self.lambda2 = pol.HalfWavePlate(
            rotate_deg = rotate_sign * 45 / 2,
        )

        self.pol_BS_out = pol.PolarizingBeamsplitter(
            pass_polarization = self.pol_to,
        )

        self.system.bond(self.pol_BS_in.po_BkA, self.faraday.po_Fr)
        self.system.bond(self.faraday.po_Bk,    self.lambda2.po_Fr)
        self.system.bond(self.lambda2.po_Bk,    self.pol_BS_out.po_FrA)

        self.po_Fr          = self.pol_BS_in.po_FrA
        self.Fr_pol      = self.pol_from

        self.po_Bk          = self.pol_BS_out.po_BkA
        self.Bk_pol      = self.pol_to

        self.Fr_Prej     = self.pol_BS_in.po_FrB
        self.Fr_Prej_pol = pol.polarization_opposite(self.pol_from)

        self.Bk_Prej     = self.pol_BS_out.po_BkB
        self.Bk_Prej_pol = pol.polarization_opposite(self.pol_to)

        self.Fr_ins      = self.pol_BS_out.po_FrB
        self.Fr_ins_pol  = pol.polarization_opposite(self.pol_to)








