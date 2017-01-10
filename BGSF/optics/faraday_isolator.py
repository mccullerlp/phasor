# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)

from . import bases
from . import ports
from . import polarization as pol


class FaradayIsolator(
        ports.OpticalOriented2PortMixin,
        bases.OpticalCouplerBase,
        bases.SystemElementBase
):
    def __init__(
            self,
            pol_from = 'S',
            pol_to   = 'S',
            **kwargs
    ):
        super(FaradayIsolator, self).__init__(**kwargs)
        bases.OOA_ASSIGN(self).pol_from = pol_from
        bases.OOA_ASSIGN(self).pol_to   = pol_to

        self.pol_BS_in  = pol.PolarizingBeamsplitter(
            pass_polarization = pol_from,
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
            pass_polarization = pol_to,
        )

        self.system.link(self.pol_BS_in.BkA, self.faraday.Fr)
        self.system.link(self.faraday.Bk,    self.lambda2.Fr)
        self.system.link(self.lambda2.Bk,    self.pol_BS_out.FrA)

        self.Fr          = self.pol_BS_in.FrA
        self.Fr_pol      = self.pol_from

        self.Bk          = self.pol_BS_out.BkA
        self.Bk_pol      = self.pol_to

        self.Fr_Prej     = self.pol_BS_in.FrB
        self.Fr_Prej_pol = pol.polarization_opposite(self.pol_from)

        self.Bk_Prej     = self.pol_BS_out.BkB
        self.Bk_Prej_pol = pol.polarization_opposite(self.pol_to)

        self.Fr_ins      = self.pol_BS_out.FrB
        self.Fr_ins_pol  = pol.polarization_opposite(self.pol_to)








