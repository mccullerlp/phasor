"""
"""
from __future__ import division, print_function
import numpy as np
from ... import optics
from ... import base
from ... import signals
from ... import readouts
from ...utilities.mpl.autoniceplot import mplfigB
#from ... import system


class AOMTestStand(optics.OpticalCouplerBase):
    def __build__(self):
        super(AOMTestStand, self).__build__()
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        self.my.F_LO = base.Frequency(
            F_Hz  = 200e6,
            order = 1,
        )

        self.my.PD_R1 = optics.MagicPD()
        self.my.PD_R2 = optics.MagicPD()

        self.my.LO = signals.SignalGenerator(
            F         = self.F_LO,
            amplitude = 1,
        )

        self.my.aom = optics.AOM(
            N_ode = 100,
            solution_order = 4,
        )
        self.aom.Drv.bond(self.LO.Out)

        self.PSL.Fr.bond_sequence(
            self.aom.FrA,
        )
        self.aom.BkA.bond(self.PD_R1.Fr)
        self.aom.BkB.bond(self.PD_R2.Fr)

        self.my.DC_R1 = readouts.DCReadout(
            port = self.PD_R1.Wpd.o,
        )
        self.my.DC_R2 = readouts.DCReadout(
            port = self.PD_R2.Wpd.o,
        )
