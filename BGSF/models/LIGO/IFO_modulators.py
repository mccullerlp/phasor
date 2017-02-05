# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function

#import numpy as np
#import declarative

from ..import optics
from ..import signals
from ..import base

#from BGSF.utilities.np import logspaced

class MichelsonModulator(base.SystemElementSled):
    def __init__(self, **kwargs):
        super(MichelsonModulator, self).__init__(**kwargs)

        self.mX = optics.Mirror(
            T_hr = 0,
            L_hr = 0,
            #facing_cardinal = 'W',
        )
        self.mY = optics.Mirror(
            T_hr = 0,
            L_hr = 0,
            #facing_cardinal = 'S',
        )
        self.mBS = optics.Mirror(
            T_hr = .5,
            L_hr = 0,
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )

        self.sX = optics.Space(
            L_m = 0,
            L_detune_m = 0,
        )
        self.sY = optics.Space(
            L_m = 0,
            L_detune_m = 0,
        )

        self.system.optical_link_sequence_WtoE(
            self.mBS,
            self.sX,
            self.mX,
        )
        self.system.optical_link_sequence_StoN(
            self.mBS,
            self.sY,
            self.mY,
        )

        self.Fr = self.mBS.FrA
        self.Bk = self.mBS.BkB

    def orient_optical_portsEW(self):
        return (self.Fr, self.Bk)

    def orient_optical_portsNS(self):
        return (self.Fr, self.Bk)


class MZModulator(base.SystemElementSled):
    def __init__(self, **kwargs):
        super(MZModulator, self).__init__(**kwargs)

        self.mX = optics.Mirror(
            T_hr = 0,
            L_hr = 0,
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )
        #this orientation makes the modulator "dark" on the through pass
        self.mY = optics.Mirror(
            T_hr = 0,
            L_hr = 0,
            AOI_deg = 45,
            #facing_cardinal = 'SE',
        )
        self.mBS1 = optics.Mirror(
            T_hr = .5,
            L_hr = 0,
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )
        self.mBS2 = optics.Mirror(
            T_hr = .5,
            L_hr = 0,
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )

        self.sX1 = optics.Space(
            L_m = 0,
            L_detune_m = 0,
        )
        self.sX2 = optics.Space(
            L_m = 0,
            L_detune_m = 0,
        )
        self.sY1 = optics.Space(
            L_m = 0,
            L_detune_m = 0,
        )
        self.sY2 = optics.Space(
            L_m = 0,
            L_detune_m = 0,
        )

        self.system.optical_link_sequence_WtoE(
            self.mBS1,
            self.sX1,
            self.mX,
        )
        self.system.optical_link_sequence_StoN(
            self.mX,
            self.sX2,
            self.mBS2,
        )
        self.system.optical_link_sequence_StoN(
            self.mBS1,
            self.sY1,
            self.mY,
        )
        self.system.optical_link_sequence_WtoE(
            self.mY,
            self.sY2,
            self.mBS2,
        )

        self.FrA = self.mBS1.FrA
        self.BkA = self.mBS2.BkA

        self.FrB = self.mBS1.BkB
        self.BkB = self.mBS2.FrB

        self.actuate_DARM_m = signals.DistributionAmplifier(
            port_gains = dict(
                mX = -1 / 2,
                mY = +1 / 2,
            )
        )
        self.system.bond(self.actuate_DARM_m.mX, self.mX.posZ)
        self.system.bond(self.actuate_DARM_m.mY, self.mY.posZ)

        self.Drv_m = self.actuate_DARM_m.I

        self.INPUT_ATTACH_POINT    = self.FrA
        self.OUTPUT_ATTACH_POINT   = self.BkB
        self.SQZ_ATTACH_POINT      = self.FrB
        self.DIAG_PWR_ATTACH_POINT = self.BkA
        return

    def orient_optical_portsEW(self):
        return (self.FrA, self.BkA)

    def orient_optical_portsNS(self):
        return (self.FrB, self.BkB)

