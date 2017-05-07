# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#import numpy as np
#import declarative

from ... import optics
#from .. import signals
from ... import readouts
from ... import base
from . import IFO_modulators
from . import direct_homodyne

#from OpenLoop.utilities.np import logspaced


class BHDTestSled(base.SystemElementBase):
    def __build__(self):
        #super(BHDTestSled, self).__build__()
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )
        self.my.LO = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )

        self.my.MZsensor = IFO_modulators.MZModulator()

        self.my.sqz = optics.EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )

        self.my.BHD = direct_homodyne.BalancedHomodyneDetector(
            phase_deg = 90,
        )

        #self.system.optical_link_sequence_StoN(
        self.system.bond_sequence(
            self.sqz.Fr,
            self.MZsensor.FrA,
        )
        #self.system.optical_link_sequence_WtoE(
        self.system.bond_sequence(
            self.PSL.Fr,
            #self.MZsensor.FrB,
            self.BHD.port_signal,
        )
        self.system.bond(
            self.LO.Fr,
            self.BHD.port_LO,
        )

        self.my.BHD_AC = readouts.ACReadout(
            portN = self.BHD.Wpd_diff.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.BHDHD_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.Wpd_diff.o,
            portNQ = self.BHD.Wpd_cmn.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.BHDHDC_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.PD_IQ.rtWpdI.o,
            portNQ = self.BHD.PD_IQ.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.BHDHDD_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.PD_IQ_P.rtWpdI.o,
            portNQ = self.BHD.PD_IQ_N.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )


class SBHDTestSled(base.SystemElementBase):
    def __build__(self):
        #super(SBHDTestSled, self).__build__()
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )
        self.my.LO = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )

        self.my.MZsensor = IFO_modulators.MZModulator()

        self.my.sqz = optics.EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )

        self.my.BHD = direct_homodyne.BalancedHomodyneDetector(
            phase_deg = 90,
            P_link_intermediate = (self.MZsensor.FrB, self.MZsensor.BkA),
        )

        #self.system.optical_link_sequence_StoN(
        self.system.bond_sequence(
            self.sqz.Fr,
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

        self.my.BHD_AC = readouts.ACReadout(
            portN = self.BHD.Wpd_diff.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.BHDHD_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.Wpd_diff.o,
            portNQ = self.BHD.Wpd_cmn.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.BHDHDC_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.PD_IQ.rtWpdI.o,
            portNQ = self.BHD.PD_IQ.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.BHDHDD_AC = readouts.HomodyneACReadout(
            portNI = self.BHD.PD_IQ_P.rtWpdI.o,
            portNQ = self.BHD.PD_IQ_N.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )
