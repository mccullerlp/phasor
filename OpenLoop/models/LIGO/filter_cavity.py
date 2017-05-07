# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import print_function

import numpy as np

import declarative
from .. import optics
from .. import signals
from .. import readouts
from .. import base

from . import IFO_modulators

#from OpenLoop.utilities.np import logspaced


class EasySqueezeSetup(base.SystemElementBase):
    def __init__(self, **kwargs):
        super(EasySqueezeSetup, self).__init__(**kwargs)
        self.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            name = "PSL",
        )

        self.MZsensor = IFO_modulators.MZModulator()

        self.teeny_space = optics.Space(L_m = 0)

        self.sqz = optics.EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )

        base.OOA_ASSIGN(self).AS_efficiency_percent = 85
        self.AS_loss = optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.AS_efficiency_percent * 1e-2,
            #facing_cardinal = 'W',
            AOI_deg = 0,
        )

        self.ASPDHD_lossless = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )

        self.ASPDHD = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )
        self.ASPD = optics.MagicPD(
            #facing_cardinal = 'W',
        )

        self.system.optical_link_sequence_StoN(
            self.sqz,
            self.MZsensor,
        )
        self.system.optical_link_sequence_WtoE(
            self.PSL,
            self.MZsensor,
            self.teeny_space,
            self.ASPDHD_lossless,
            self.AS_loss,
            self.ASPDHD,
            self.ASPD,
        )

        self.ASPD_DC = readouts.DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.ASPDHD_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.ASPDHD.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.ASPDHDll_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_lossless.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )

