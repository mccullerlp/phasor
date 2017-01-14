# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import print_function

import numpy as np

from declarative.bunch import (
    Bunch,
)

from ..optics import (
    Mirror,
    PD,
    MagicPD,
    Space,
    Laser,
)

from ..system.optical import (
    OpticalSystem,
)

from ..signals import (
    SignalGenerator,
    Mixer,
    DistributionAmplifier,
    SummingAmplifier,
    #TransferFunctionSISO,
    TransferFunctionSISOMechSingleResonance,
)

from ..readouts import (
    DCReadout,
    ACReadout,
    ACReadoutCLG,
)

from ..readouts.homodyne_AC import (
    HomodyneACReadout,
)

from ..base import (
    SystemElementSled,
    OOA_ASSIGN,
    Frequency,
)

from ..optics.modulators import (
    PM, AM
)

from ..optics.EZSqz import (
    EZSqz,
)

from ..optics.hidden_variable_homodyne import (
    HiddenVariableHomodynePD,
)

from ..optics.vacuum import (
    VacuumTerminator,
)

from .IFO_modulators import (
    MZModulator,
)

from .direct_homodyne import (
    BalancedHomodyneDetector
)

#from BGSF.utilities.np import logspaced

class BHDTestSled(SystemElementSled):
    def __init__(self, **kwargs):
        super(BHDTestSled, self).__init__(**kwargs)
        self.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )
        self.LO = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )

        self.MZsensor = MZModulator()

        self.sqz = EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )

        self.BHD = BalancedHomodyneDetector(
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

        self.BHD_AC = ACReadout(
            portN = self.BHD.Wpd_diff.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHD_AC = HomodyneACReadout(
            portNI = self.BHD.Wpd_diff.o,
            portNQ = self.BHD.Wpd_cmn.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHDC_AC = HomodyneACReadout(
            portNI = self.BHD.PD_IQ.rtWpdI.o,
            portNQ = self.BHD.PD_IQ.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHDD_AC = HomodyneACReadout(
            portNI = self.BHD.PD_IQ_P.rtWpdI.o,
            portNQ = self.BHD.PD_IQ_N.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )


class SBHDTestSled(SystemElementSled):
    def __init__(self, **kwargs):
        super(SBHDTestSled, self).__init__(**kwargs)
        self.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )
        self.LO = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )

        self.MZsensor = MZModulator()

        self.sqz = EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )

        self.BHD = BalancedHomodyneDetector(
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

        self.BHD_AC = ACReadout(
            portN = self.BHD.Wpd_diff.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHD_AC = HomodyneACReadout(
            portNI = self.BHD.Wpd_diff.o,
            portNQ = self.BHD.Wpd_cmn.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHDC_AC = HomodyneACReadout(
            portNI = self.BHD.PD_IQ.rtWpdI.o,
            portNQ = self.BHD.PD_IQ.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.BHDHDD_AC = HomodyneACReadout(
            portNI = self.BHD.PD_IQ_P.rtWpdI.o,
            portNQ = self.BHD.PD_IQ_N.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )
