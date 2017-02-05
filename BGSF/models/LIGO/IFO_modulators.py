# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import print_function

import numpy as np

from declarative.bunch import (
    declarative.Bunch,
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

#from BGSF.utilities.np import logspaced

class MichelsonModulator(SystemElementSled):
    def __init__(self, **kwargs):
        super(MichelsonModulator, self).__init__(**kwargs)

        self.mX = Mirror(
            T_hr = 0,
            L_hr = 0,
            facing_cardinal = 'W',
        )
        self.mY = Mirror(
            T_hr = 0,
            L_hr = 0,
            facing_cardinal = 'S',
        )
        self.mBS = Mirror(
            T_hr = .5,
            L_hr = 0,
            AOI_deg = 45,
            facing_cardinal = 'NW',
        )

        self.sX = Space(
            L_m = 0,
            L_detune_m = 0,
        )
        self.sY = Space(
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


class MZModulator(SystemElementSled):
    def __init__(self, **kwargs):
        super(MZModulator, self).__init__(**kwargs)

        self.mX = Mirror(
            T_hr = 0,
            L_hr = 0,
            AOI_deg = 45,
            facing_cardinal = 'NW',
        )
        #this orientation makes the modulator "dark" on the through pass
        self.mY = Mirror(
            T_hr = 0,
            L_hr = 0,
            AOI_deg = 45,
            facing_cardinal = 'SE',
        )
        self.mBS1 = Mirror(
            T_hr = .5,
            L_hr = 0,
            AOI_deg = 45,
            facing_cardinal = 'NW',
        )
        self.mBS2 = Mirror(
            T_hr = .5,
            L_hr = 0,
            AOI_deg = 45,
            facing_cardinal = 'NW',
        )

        self.sX1 = Space(
            L_m = 0,
            L_detune_m = 0,
        )
        self.sX2 = Space(
            L_m = 0,
            L_detune_m = 0,
        )
        self.sY1 = Space(
            L_m = 0,
            L_detune_m = 0,
        )
        self.sY2 = Space(
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

        self.actuate_DARM_m = DistributionAmplifier(
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

