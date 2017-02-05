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
    optics.Mirror,
    optics.PD,
    optics.MagicPD,
    optics.Space,
    optics.Laser,
)

from ..system.optical import (
    OpticalSystem,
)

from ..signals import (
    signals.SignalGenerator,
    Mixer,
    signals.DistributionAmplifier,
    signals.SummingAmplifier,
    #signals.TransferFunctionSISO,
    signals.TransferFunctionSISOMechSingleResonance,
)

from ..readouts import (
    readouts.DCReadout,
    readouts.ACReadout,
    readouts.ACReadoutCLG,
)

from ..readouts.homodyne_AC import (
    readouts.HomodyneACReadout,
)

from ..base import (
    base.SystemElementSled,
    base.OOA_ASSIGN,
    base.Frequency,
)

from ..optics.modulators import (
    PM, AM
)

from ..optics.EZSqz import (
    EZSqz,
)

from ..optics.hidden_variable_homodyne import (
    optics.HiddenVariableHomodynePD,
)

from ..optics.vacuum import (
    optics.VacuumTerminator,
)

from .IFO_modulators import (
    MZModulator,
)

#from BGSF.utilities.np import logspaced


class CondSqueezeSetup(base.SystemElementSled):
    def __init__(self, **kwargs):
        super(CondSqueezeSetup, self).__init__(**kwargs)
        #self.PSL = optics.Laser(
        #    F = self.system.F_carrier_1064,
        #    power_W = 1,
        #    name = "PSL",
        #)

        self.F_shift = base.Frequency(
            F_Hz = 1e6,
            name = 'SQZsep',
        )
        self.PSL_up = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            name = "PSL+",
            classical_fdict = {
                self.F_shift : 1,
            },
        )
        self.PSL_dn = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            name = "PSL-",
            classical_fdict = {
                self.F_shift : -1,
            },
        )

        self.MZsensor = MZModulator()

        self.teeny_space = optics.Space(L_m = 0)

        self.sqz = EZSqz(
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

        self.ASPDHD_up_lossless = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL_up.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )
        self.ASPDHD_dn_lossless = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL_dn.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )
        self.ASPDHD_up = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL_up.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )
        self.ASPDHD_dn = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL_dn.Fr.o,
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
            self.PSL_dn,
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
            portNI = self.ASPDHD_dn.rtWpdI.o,
            portNQ = self.ASPDHD_dn.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.ASPDHDll_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD_dn_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_dn_lossless.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
