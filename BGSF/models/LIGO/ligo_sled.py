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
    PM
)

from ..optics.hidden_variable_homodyne import (
    HiddenVariableHomodynePD,
)

from ..optics.vacuum import (
    VacuumTerminator,
)

#from YALL.utilities.np import logspaced

class QuadMirrorBasic(SystemElementSled):
    def __init__(
            self,
            T_hr,
            L_hr,
            facing_cardinal,
            AOI_deg = 0,
            **kwargs
    ):
        super(QuadMirrorBasic, self).__init__(**kwargs)
        OOA_ASSIGN(self).resonance_F_Hz = .45
        OOA_ASSIGN(self).resonance_FWHM_Hz = .05
        #OOA_ASSIGN(self).resonance_FWHM_Hz = .45
        OOA_ASSIGN(self).mass_kg = 40

        self.mirror = Mirror(
            T_hr            = T_hr,
            L_hr            = L_hr,
            facing_cardinal = facing_cardinal,
            AOI_deg         = AOI_deg,
        )
        self.quad_xfer = TransferFunctionSISOMechSingleResonance(
            mass_kg   = self.mass_kg,
            center_Hz = self.resonance_F_Hz,
            FWHM_Hz   = self.resonance_FWHM_Hz,
            no_DC     = True,
        )

        self.pos_amp = SummingAmplifier(
            port_gains = dict(
                mech = 1,
                actuator = 1,
            )
        )

        self.force_amp = SummingAmplifier(
            port_gains = dict(
                optical  = 1,
                actuator = 1,
            )
        )

        self.actuate_force_N = self.force_amp.actuator
        self.actuate_pos_m   = self.pos_amp.actuator
        self.testpoint_pos_m = self.pos_amp.O

        self.system.link(self.force_amp.O, self.quad_xfer.In)
        self.system.link(self.quad_xfer.Out, self.pos_amp.mech)
        self.system.link(self.pos_amp.O, self.mirror.posZ)
        self.system.link(self.mirror.forceZ, self.force_amp.optical)

        self.mirror_ACCLG = ACReadoutCLG(
            portN = self.mirror.posZ.i,
            portD = self.mirror.forceZ.o,
        )
        self.mirror_AC = ACReadout(
            portN = self.mirror.posZ.i,
            portD = self.mirror.forceZ.o,
        )
        self.mirror_DC = DCReadout(
            port = self.mirror.posZ.i,
        )


class LIGODetector(SystemElementSled):
    def __init__(self, **kwargs):
        super(LIGODetector, self).__init__(**kwargs)

        OOA_ASSIGN(self).lossless = False

        OOA_ASSIGN(self).misalign_SR = False
        OOA_ASSIGN(self).missing_SR  = False
        OOA_ASSIGN(self).misalign_PR = False
        OOA_ASSIGN(self).missing_PR  = False
        OOA_ASSIGN(self).misalign_EX = False
        OOA_ASSIGN(self).misalign_EY = False

        OOA_ASSIGN(self).lPRC_m  = 57.656   # PRCL: lPRC_m = lPR + (lIX + lIY) / 2
        OOA_ASSIGN(self).lSRC_m  = 56.008   # SRCL: lSRC_m = lSR + (lIX + lIY) / 2
        OOA_ASSIGN(self).lasy_m  = 0.0504   # Schnupp Asy: lasy_m = lIX - lIY
        OOA_ASSIGN(self).lmean_m = 4.8298   # (lIX + lIY) / 2
        OOA_ASSIGN(self).larm_m  = 3994.5   # (lIX + lIY) / 2

        OOA_ASSIGN(self).lBS_IX_m  = self.lmean_m + self.lasy_m / 2  # distance [m] from BS to IX
        OOA_ASSIGN(self).lBS_IY_m  = self.lmean_m - self.lasy_m / 2  # distance [m] from BS to IY
        OOA_ASSIGN(self).lIX_EX_m  = self.larm_m                     # length [m] of the X arm
        OOA_ASSIGN(self).lIY_EY_m  = self.larm_m                     # length [m] of the Y armlplp
        OOA_ASSIGN(self).lBS_PR_m  = self.lPRC_m - self.lmean_m      # distance from PR to BS
        OOA_ASSIGN(self).lBS_SR_m  = self.lSRC_m - self.lmean_m      # distance from SR to BS
        OOA_ASSIGN(self).lPR_PR2_m = 16.6037                         # distance from PR to PR2
        OOA_ASSIGN(self).lPR2_BS_m = self.lBS_PR_m - self.lPR_PR2_m  # distance from PR2 to BS

        # Mirror curvatures (all dimensions in meters)
        #Ri = 1934             # radius of curvature of input mirrors (IX and IY)
        #Re = 2245           # radius of curvature of end mirrors (EX and EY)
        #Rpr = -10.997          # radius of curvature of power recycling mirrors
        #Rpr2 = -4.555
        #Rsr = -5.6938      	# radius of curvature of signal recycling mirrors

        self.BS = QuadMirrorBasic(
            T_hr = 0.5,
            L_hr = 37.5e-6 if not self.lossless else 0,
            AOI_deg = 45,
            facing_cardinal = 'NW',
        )
        self.IX = QuadMirrorBasic(
            T_hr = 14e-3,
            L_hr = 0 if not self.lossless else 0,
            facing_cardinal = 'E',
        )
        self.EX = QuadMirrorBasic(
            T_hr = 5e-6,
            L_hr = 100e-6 if not self.lossless else 0,
            facing_cardinal = 'W',
            AOI_deg = (1 if self.misalign_EX else 0),
        )
        self.IY = QuadMirrorBasic(
            T_hr = 14e-3,
            L_hr = 0 if not self.lossless else 0,
            facing_cardinal = 'N',
        )
        self.EY = QuadMirrorBasic(
            T_hr = 5e-6,
            L_hr = 100e-6 if not self.lossless else 0,
            facing_cardinal = 'S',
            AOI_deg = (1 if self.misalign_EY else 0),
        )
        if not self.missing_PR:
            self.PR = Mirror(
                T_hr = 30e-3,
                L_hr = 37.5e-6 if not self.lossless else 0,
                facing_cardinal = 'E',
                #facing_cardinal = 'W',
                AOI_deg = (5 if self.misalign_PR else 0),
            )
        else:
            self.PR = Space(
                L_m = 0,
            )

        self.PR2 = Mirror(
            T_hr = 1 - 250e-6,
            L_hr = 37.5e-6 if not self.lossless else 0,
            AOI_deg = 45,
            facing_cardinal = 'NW',
        )
        if not self.missing_SR:
            self.SR = Mirror(
                T_hr = 350e-3,
                L_hr = 37.5e-6 if not self.lossless else 0,
                facing_cardinal = 'S',
                AOI_deg = (5 if self.misalign_SR else 0),
            )
        else:
            self.SR = Space(
                L_m = 0,
            )

        self.BS_IX  = Space(L_m = self.lBS_IX_m )
        self.BS_IY  = Space(L_m = self.lBS_IY_m )
        self.IX_EX  = Space(L_m = self.lIX_EX_m )
        self.IY_EY  = Space(L_m = self.lIY_EY_m )
        self.BS_SR  = Space(L_m = self.lBS_SR_m )
        self.PR_PR2 = Space(L_m = self.lPR_PR2_m)
        self.PR2_BS = Space(L_m = self.lPR2_BS_m)

        self.REFLPD = MagicPD(
            facing_cardinal = 'E',
        )
        self.POPTruePD = MagicPD(
            facing_cardinal = 'W',
        )
        self.POPPD = PD()
        self.XarmPD = MagicPD(
            facing_cardinal = 'W',
        )
        self.XtransPD = PD()
        self.YarmPD = MagicPD(
            facing_cardinal = 'S',
        )
        self.YtransPD = PD()
        self.asymPD = PD()

        self.system.optical_link_sequence_WtoE(
            self.REFLPD,
            self.PR,
            self.POPTruePD,
            self.PR_PR2,
            self.PR2,
            self.PR2_BS,
            self.BS.mirror,
            self.BS_IX,
            self.IX.mirror,
            self.XarmPD,
            self.IX_EX,
            self.EX.mirror,
            self.XtransPD,
        )
        self.system.optical_link_sequence_StoN(
            self.SR,
            self.BS_SR,
            self.BS.mirror,
            self.BS_IY,
            self.IY.mirror,
            self.YarmPD,
            self.IY_EY,
            self.EY.mirror,
            self.YtransPD,
        )

        self.PR2_vac = VacuumTerminator()
        self.system.optical_link_sequence_StoN(
            self.PR2_vac,
            self.PR2,
            self.POPPD,
        )

        self.XtransDC = DCReadout(
            port = self.XtransPD.Wpd.o,
        )
        self.XarmDC = DCReadout(
            port = self.XarmPD.Wpd.o,
        )
        self.YtransDC = DCReadout(
            port = self.YtransPD.Wpd.o,
        )
        self.YarmDC = DCReadout(
            port = self.YarmPD.Wpd.o,
        )
        self.REFLDC = DCReadout(
            port = self.REFLPD.Wpd.o,
        )
        self.POPDC = DCReadout(
            port = self.POPPD.Wpd.o,
        )
        self.POPTrueDC = DCReadout(
            port = self.POPTruePD.Wpd.o,
        )

        self.actuate_DARM_m = DistributionAmplifier(
            port_gains = dict(
                EX = -1 / 2,
                EY = +1 / 2,
            )
        )
        self.system.link(self.actuate_DARM_m.EX, self.EX.actuate_pos_m)
        self.system.link(self.actuate_DARM_m.EY, self.EY.actuate_pos_m)

        self.actuate_DARM_N = DistributionAmplifier(
            port_gains = dict(
                EX = -1 / 2,
                EY = +1 / 2,
            )
        )
        self.system.link(self.actuate_DARM_N.EX, self.EX.actuate_force_N)
        self.system.link(self.actuate_DARM_N.EY, self.EY.actuate_force_N)

        self.actuate_CARM_m = DistributionAmplifier(
            port_gains = dict(
                EX = 1,
                EY = 1,
            )
        )
        self.system.link(self.actuate_CARM_m.EX, self.EX.actuate_pos_m)
        self.system.link(self.actuate_CARM_m.EY, self.EY.actuate_pos_m)

        self.actuate_CARM_N = DistributionAmplifier(
            port_gains = dict(
                EX = 1,
                EY = 1,
            )
        )
        self.system.link(self.actuate_CARM_N.EX, self.EX.actuate_force_N)
        self.system.link(self.actuate_CARM_N.EY, self.EY.actuate_force_N)

        self.testpoint_DARM_pos_m = SummingAmplifier(
            port_gains = dict(
                EX = -1,
                EY = +1,
            )
        )
        self.system.link(self.EX.testpoint_pos_m, self.testpoint_DARM_pos_m.EX)
        self.system.link(self.EY.testpoint_pos_m, self.testpoint_DARM_pos_m.EY)

        self.testpoint_CARM_pos_m = SummingAmplifier(
            port_gains = dict(
                EX = +1 / 2,
                EY = +1 / 2,
            )
        )
        self.system.link(self.EX.testpoint_pos_m, self.testpoint_CARM_pos_m.EX)
        self.system.link(self.EY.testpoint_pos_m, self.testpoint_CARM_pos_m.EY)

        #since it is facing east
        self.INPUT_ATTACH_POINT = self.REFLPD.Bk
        #since it is facing south
        self.OUTPUT_ATTACH_POINT = self.SR.Fr
        return


class LIGOInputBasic(SystemElementSled):
    def __init__(self, **kwargs):
        super(LIGOInputBasic, self).__init__(**kwargs)
        self.F9 = Frequency(
            F_Hz  = 9099471,
            order = 0,
        )
        self.F45 = Frequency(
            F_Hz  = 45497355,
            order = 0,
        )
        self.generateF9 = SignalGenerator(
            F = self.F9,
            harmonic_gains = {3 : 1},
        )
        self.generateF45 = SignalGenerator(
            F = self.F45,
            harmonic_gains = {3 : 1},
        )
        self.EOM_drive = SummingAmplifier(
            port_gains = dict(
                index_9  = .1,
                index_45 = .1,
            )
        )

        self.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 200,
            name = "PSL",
        )

        self.EOM = PM()

        self.system.optical_link_sequence_WtoE(
            self.PSL,
            self.EOM,
        )

        self.INPUT_ATTACH_POINT = self.EOM


class LIGOOutputBasic(SystemElementSled):
    def __init__(self, LIGO_obj, **kwargs):
        super(LIGOOutputBasic, self).__init__(**kwargs)
        self.ASPD = PD()

        self.ASPD_DC = DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.ASPD_AC = ACReadout(
            portN = self.ASPD.Wpd.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )

        self.OUTPUT_ATTACH_POINT = self.ASPD


class LIGOOutputHomodyne(SystemElementSled):
    def __init__(
            self,
            input_obj,
            LIGO_obj,
            **kwargs
    ):
        super(LIGOOutputHomodyne, self).__init__(**kwargs)

        self.ASPD = MagicPD(
            facing_cardinal = 'N',
        )
        self.AS_vac = VacuumTerminator()
        self.ASPDHD_lossless = HiddenVariableHomodynePD(
            source_port     = input_obj.PSL.Fr.o,
            phase_deg       = 90,
            facing_cardinal = 'N',
        )

        OOA_ASSIGN(self).AS_efficiency_percent = 85
        self.AS_loss = Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.AS_efficiency_percent * 1e-2,
            facing_cardinal = 'N',
            AOI_deg = 0,
        )

        self.ASPDHD = HiddenVariableHomodynePD(
            source_port     = input_obj.PSL.Fr.o,
            phase_deg       = 90,
            facing_cardinal = 'N',
        )

        self.ASPDHD_DC_I = DCReadout(
            port = self.ASPDHD.rtWpdI.o,
        )
        self.ASPDHD_AC_I = ACReadout(
            portN = self.ASPDHD.rtWpdI.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )
        self.ASPDHD_DC_Q = DCReadout(
            port = self.ASPDHD.rtWpdQ.o,
        )
        self.ASPDHD_AC_Q = ACReadout(
            portN = self.ASPDHD.rtWpdQ.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )

        self.ASPDHD_AC = HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.ASPDHD.rtWpdQ.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )
        self.ASPDHDll_AC = HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_lossless.rtWpdQ.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )


        self.ASPD_DC = DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.ASPD_AC = ACReadout(
            portN = self.ASPD.Wpd.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )

        #TODO add loss
        self.system.optical_link_sequence_NtoS(
            self.ASPD,
            self.ASPDHD_lossless,
            self.AS_loss,
            self.ASPDHD,
            self.AS_vac,
        )
        self.OUTPUT_ATTACH_POINT = self.ASPD


class LIGOBasicOperation(SystemElementSled):
    def __init__(self, **kwargs):
        super(LIGOBasicOperation, self).__init__(**kwargs)
        self.LIGO = LIGODetector()
        self.input  = LIGOInputBasic()
        #self.output = LIGOOutputBasic(LIGO_obj = self.LIGO)
        self.output = LIGOOutputHomodyne(
            LIGO_obj  = self.LIGO,
            input_obj = self.input,
        )

        self.system.optical_link_sequence_WtoE(
            self.input.INPUT_ATTACH_POINT,
            self.LIGO.INPUT_ATTACH_POINT,
        )

        self.system.optical_link_sequence_NtoS(
            self.LIGO.OUTPUT_ATTACH_POINT,
            self.output.OUTPUT_ATTACH_POINT,
        )


