# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#import numpy as np
#import declarative

from .. import optics
#from .. import signals
from .. import readouts
from .. import base
from . import IFO_modulators
from . import direct_homodyne

#from BGSF.utilities.np import logspaced


class BHDTestSled(base.SystemElementSled):
    def __init__(self, **kwargs):
        super(BHDTestSled, self).__init__(**kwargs)
        self.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )
        self.LO = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )

        self.MZsensor = IFO_modulators.MZModulator()

        self.sqz = optics.EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )

        self.BHD = direct_homodyne.BalancedHomodyneDetector(
            phase_deg = 90,
        )

        self.system.optical_link_sequence_StoN(
            self.sqz,
            self.MZsensor,
        )
        self.system.optical_link_sequence_WtoE(
            self.PSL,
            self.MZsensor,
            self.BHD.port_signal,
        )
        self.system.bond(
            self.LO.Fr,
            self.BHD.port_LO,
        )

        self.BHD_AC = readouts.ACReadout(
            portN = self.BHD.Wpd_diff.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHD_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.Wpd_diff.o,
            portNQ = self.BHD.Wpd_cmn.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHDC_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.PD_IQ.rtWpdI.o,
            portNQ = self.BHD.PD_IQ.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHDD_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.PD_IQ_P.rtWpdI.o,
            portNQ = self.BHD.PD_IQ_N.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )


class SBHDTestSled(base.SystemElementSled):
    def __init__(self, **kwargs):
        super(SBHDTestSled, self).__init__(**kwargs)
        self.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )
        self.LO = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )

        self.MZsensor = IFO_modulators.MZModulator()

        self.sqz = optics.EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )

        self.BHD = direct_homodyne.BalancedHomodyneDetector(
            phase_deg = 90,
            P_link_intermediate = (self.MZsensor.FrB, self.MZsensor.BkA),
        )

        self.system.optical_link_sequence_StoN(
            self.sqz,
            self.BHD.port_signal,
        )
        self.system.bond(
            self.PSL.Fr,
            self.MZsensor.FrA,
        )
        self.system.bond(
            self.LO.Fr,
            self.BHD.port_LO,
        )

        self.BHD_AC = readouts.ACReadout(
            portN = self.BHD.Wpd_diff.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHD_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.Wpd_diff.o,
            portNQ = self.BHD.Wpd_cmn.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHDC_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.PD_IQ.rtWpdI.o,
            portNQ = self.BHD.PD_IQ.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHDD_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.PD_IQ_P.rtWpdI.o,
            portNQ = self.BHD.PD_IQ_N.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )
