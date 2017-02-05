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

from .IFO_modulators import (
    MZModulator,
)

#from BGSF.utilities.np import logspaced

class EasySqueezeSetup(SystemElementSled):
    def __init__(self, **kwargs):
        super(EasySqueezeSetup, self).__init__(**kwargs)
        self.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            name = "PSL",
        )

        self.MZsensor = MZModulator()

        self.teeny_space = Space(L_m = 0)

        self.sqz = EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )

        OOA_ASSIGN(self).AS_efficiency_percent = 85
        self.AS_loss = Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.AS_efficiency_percent * 1e-2,
            facing_cardinal = 'W',
            AOI_deg = 0,
        )

        self.ASPDHD_lossless = HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            facing_cardinal = 'W',
        )

        self.ASPDHD = HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            facing_cardinal = 'W',
        )
        self.ASPD = MagicPD(
            facing_cardinal = 'W',
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

        self.ASPD_DC = DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.ASPDHD_AC = HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.ASPDHD.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.ASPDHDll_AC = HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_lossless.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )


class EasySqueezeSetupSplit(SystemElementSled):
    def __init__(self, **kwargs):
        super(EasySqueezeSetupSplit, self).__init__(**kwargs)
        self.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            name = "PSL",
        )

        self.MZsensor = MZModulator()

        self.teeny_space = Space(L_m = 0)
        self.teeny_space2 = Space(L_m = 0)

        self.sqz = EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )
        self.sqz2 = EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )


        OOA_ASSIGN(self).AS_efficiency_percent = 85
        self.AS_loss = Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.AS_efficiency_percent * 1e-2,
            facing_cardinal = 'W',
            AOI_deg = 0,
        )

        OOA_ASSIGN(self).sqz_efficiency_percent = self.AS_efficiency_percent
        self.sqz_split_loss = Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.sqz_efficiency_percent * 1e-2,
            facing_cardinal = 'W',
            AOI_deg = 0,
        )

        self.PD_sqz_split = HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            facing_cardinal = 'W',
        )

        self.ASPDHD_lossless = HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            facing_cardinal = 'W',
        )

        self.ASPDHD = HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            facing_cardinal = 'W',
        )
        self.ASPD = MagicPD(
            facing_cardinal = 'W',
        )

        self.sqz_split_vac = VacuumTerminator()
        self.sqz_vac = VacuumTerminator()
        self.sqz_split = Mirror(
            T_hr = .5,
            L_hr = 0,
            facing_cardinal = 'NW',
            AOI_deg = 45,
        )

        self.system.optical_link_sequence_StoN(
            self.sqz_vac,
            self.sqz,
            self.sqz_split,
            self.MZsensor,
        )
        self.system.optical_link_sequence_WtoE(
            self.sqz_split_vac,
            self.sqz2,
            self.sqz_split,
            self.teeny_space2,
            self.sqz_split_loss,
            self.PD_sqz_split,
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

        self.ASPD_DC = DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.ASPDHD_AC = HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.ASPDHD.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.ASPDHDll_AC = HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_lossless.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.ASPDHDspl_AC = HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.PD_sqz_split.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.ASPDHDsplll_AC = HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.PD_sqz_split.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )


class EasySqueezeSetupFP(SystemElementSled):
    def __init__(self, **kwargs):
        super(EasySqueezeSetupFP, self).__init__(**kwargs)
        self.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            name = "PSL",
        )
        self.teeny_space = Space(L_m = 0)
        self.teeny_space2 = Space(L_m = 0)

        self.sqzM1 = Mirror(
            T_hr = .01,
            L_hr = 0,
            AOI_deg = 60,
        )
        self.sqzM2 = Mirror(
            T_hr = 0,
            L_hr = 0,
            AOI_deg = 60,
        )
        self.sqzS = Space(L_m = 1)
        self.sqzM3 = Mirror(
            T_hr = 0,
            L_hr = 0,
            AOI_deg = 60,
        )
        self.sqz = EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_power_gain = 2,
            phi_sqz_deg = 90,
        )
        self.system.bond(self.sqzM1.FrB, self.sqzM2.FrA)
        self.system.bond(self.sqzM2.FrB, self.sqzS.Fr)
        self.system.bond(self.sqzS.Bk, self.sqzM3.FrA)
        self.system.bond(self.sqzM3.FrB, self.sqz.Fr)
        self.system.bond(self.sqz.Bk, self.sqzM1.FrA)

        self.EOM = PM()
        self.AM  = AM()
        self.MZsense = Mirror(
            T_hr = 0,
            facing_cardinal = 'NE',
            AOI_deg = 45,
        )

        OOA_ASSIGN(self).AS_efficiency_percent = 85
        self.AS_loss = Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.AS_efficiency_percent * 1e-2,
            facing_cardinal = 'W',
            AOI_deg = 0,
        )

        self.ASPDHD_lossless = HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            #source_port     = self.PSL.Fr.o,
            phase_deg       = 00,
            facing_cardinal = 'W',
        )

        self.ASPDHD = HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 00,
            facing_cardinal = 'W',
        )
        self.ASPD = MagicPD(
            facing_cardinal = 'W',
        )

        self.system.optical_link_sequence_NtoS(
            self.PSL,
            self.teeny_space,
            self.sqzM1.BkB,
        )

        self.system.optical_link_sequence_NtoS(
            self.sqzM1.BkA,
            self.EOM,
            self.AM,
            self.MZsense,
        )
        self.system.optical_link_sequence_WtoE(
            self.MZsense,
            self.teeny_space2,
            self.ASPDHD_lossless,
            self.AS_loss,
            self.ASPDHD,
            self.ASPD,
        )

        self.ASPD_DC = DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.ASPDHD_AC = HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.ASPDHD.rtWpdQ.o,
            portD = self.AM.Drv.i,
        )
        self.ASPDHDll_AC = HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_lossless.rtWpdQ.o,
            portD = self.AM.Drv.i,
        )

        self.PR_ATTACH_POINT = self.EOM
