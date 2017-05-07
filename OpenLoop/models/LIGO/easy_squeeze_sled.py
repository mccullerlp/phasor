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

#from BGSF.utilities.np import logspaced

class EasySqueezeSetup(base.SystemElementBase):
    def __init__(self, **kwargs):
        super(EasySqueezeSetup, self).__init__(**kwargs)
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )

        self.my.MZsensor = IFO_modulators.MZModulator()

        self.my.teeny_space = optics.Space(L_m = 0)

        self.my.sqz = optics.EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )

        base.OOA_ASSIGN(self).AS_efficiency_percent = 85
        self.my.AS_loss = optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.AS_efficiency_percent * 1e-2,
            ##facing_cardinal = 'W',
            AOI_deg = 0,
        )

        self.my.ASPDHD_lossless = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )

        self.my.ASPDHD = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )
        self.my.ASPD = optics.MagicPD(
            #facing_cardinal = 'W',
        )

        #self.system.optical_link_sequence_StoN(
        self.system.bond_sequence(
            self.sqz.Fr,
            self.MZsensor.FrA,
        )
        #self.system.optical_link_sequence_WtoE(
        self.system.bond_sequence(
            self.PSL.Fr,
            self.MZsensor.FrB,
        )
        self.system.bond_sequence(
            self.MZsensor.BkB,
            self.teeny_space.Fr,
            self.ASPDHD_lossless.Fr,
            self.AS_loss.FrA,
            self.ASPDHD.Fr,
            self.ASPD.Fr,
        )

        self.my.ASPD_DC = readouts.DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.my.ASPDHD_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.ASPDHD.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.ASPDHDll_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_lossless.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )


class EasySqueezeSetupSplit(base.SystemElementBase):
    def __init__(self, **kwargs):
        super(EasySqueezeSetupSplit, self).__init__(**kwargs)
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )

        self.my.MZsensor = MZModulator()

        self.my.teeny_space = optics.Space(L_m = 0)
        self.my.teeny_space2 = optics.Space(L_m = 0)

        self.my.sqz = optics.EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )
        self.my.sqz2 = optics.EZSqz(
            Fkey_QC_center = self.PSL.fkey,
            #sqzDB = 10,
            #antisqzDB = 13,
            nonlinear_field_gain = 2,
            phi_sqz_deg = 45,
        )


        base.OOA_ASSIGN(self).AS_efficiency_percent = 85
        self.my.AS_loss = optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.AS_efficiency_percent * 1e-2,
            #facing_cardinal = 'W',
            AOI_deg = 0,
        )

        base.OOA_ASSIGN(self).sqz_efficiency_percent = self.AS_efficiency_percent
        self.my.sqz_split_loss = optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.sqz_efficiency_percent * 1e-2,
            #facing_cardinal = 'W',
            AOI_deg = 0,
        )

        self.my.PD_sqz_split = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )

        self.my.ASPDHD_lossless = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )

        self.my.ASPDHD = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 90,
            #facing_cardinal = 'W',
        )
        self.my.ASPD = optics.MagicPD(
            #facing_cardinal = 'W',
        )

        self.my.sqz_split_vac = optics.VacuumTerminator()
        self.my.sqz_vac = optics.VacuumTerminator()
        self.my.sqz_split = optics.Mirror(
            T_hr = .5,
            L_hr = 0,
            #facing_cardinal = 'NW',
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

        self.my.ASPD_DC = readouts.DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.my.ASPDHD_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.ASPDHD.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.ASPDHDll_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_lossless.rtWpdQ.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.ASPDHDspl_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.PD_sqz_split.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )
        self.my.ASPDHDsplll_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.PD_sqz_split.rtWpdI.o,
            portD = self.MZsensor.Drv_m.i,
        )


class EasySqueezeSetupFP(base.SystemElementBase):
    def __init__(self, **kwargs):
        super(EasySqueezeSetupFP, self).__init__(**kwargs)
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
        )
        self.my.teeny_space = optics.Space(L_m = 0)
        self.my.teeny_space2 = optics.Space(L_m = 0)

        self.my.sqzM1 = optics.Mirror(
            T_hr = .01,
            L_hr = 0,
            AOI_deg = 60,
        )
        self.my.sqzM2 = optics.Mirror(
            T_hr = 0,
            L_hr = 0,
            AOI_deg = 60,
        )
        self.my.sqzS = optics.Space(L_m = 1)
        self.my.sqzM3 = optics.Mirror(
            T_hr = 0,
            L_hr = 0,
            AOI_deg = 60,
        )
        self.my.sqz = optics.EZSqz(
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

        self.my.EOM = optics.PM()
        self.my.AM  = optics.AM()
        self.my.MZsense = optics.Mirror(
            T_hr = 0,
            #facing_cardinal = 'NE',
            AOI_deg = 45,
        )

        base.OOA_ASSIGN(self).AS_efficiency_percent = 85
        self.my.AS_loss = optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.AS_efficiency_percent * 1e-2,
            #facing_cardinal = 'W',
            AOI_deg = 0,
        )

        self.my.ASPDHD_lossless = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            #source_port     = self.PSL.Fr.o,
            phase_deg       = 00,
            #facing_cardinal = 'W',
        )

        self.my.ASPDHD = optics.HiddenVariableHomodynePD(
            #source_port     = self.sqz.Bk.o,
            source_port     = self.PSL.Fr.o,
            phase_deg       = 00,
            #facing_cardinal = 'W',
        )
        self.my.ASPD = optics.MagicPD(
            #facing_cardinal = 'W',
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

        self.my.ASPD_DC = readouts.DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.my.ASPDHD_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.ASPDHD.rtWpdQ.o,
            portD = self.AM.Drv.i,
        )
        self.my.ASPDHDll_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_lossless.rtWpdQ.o,
            portD = self.AM.Drv.i,
        )

        self.PR_ATTACH_POINT = self.EOM.Bk
