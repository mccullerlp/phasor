# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import declarative
import numpy as np

from ... import optics
from ... import signals
from ... import readouts
from ... import mechanical
from ... import base


def pendulum_k(
    length_m,
    mass_kg,
    r_fiber_m,
    Ymod,
    theta,
    N_wires = 2,
):
    mgl = mass_kg * 9.81 * length_m
    k_pendL = mass_kg * 9.81 / length_m
    #FROM P930018 eq. 6
    T = mass_kg * 9.81
    Y = 200e9
    I = np.pi * r_fiber_m**4 / 2
    theta_pen = theta * N_wires * (T * Ymod * I)**.5 / (2 * mgl)
    return k_pendL, theta_pen


class QuadSusp(optics.OpticalCouplerBase):
    ln = .445
    l1 = .311
    l2 = .342
    l3 = .602
    mn = 21.949
    m1 = 22.338
    m2 = 39.63
    m3 = 39.6
    rn = 1.1e-3/2
    r1 = .711e-3/2
    r2 = .635e-3/2
    r3 = .0006/2
    Yn = 212e9
    Y1 = 212e9
    Y2 = 212e9
    Y3 = 72e9
    thetan = 4e-4
    theta1 = 4e-4
    theta2 = 4e-4
    theta3 = 1e-6

    @declarative.dproperty
    def Platform(self):
        return mechanical.TerminatorShorted()

    @declarative.dproperty
    def ActuatorF(self):
        return mechanical.ForceSourceBalanced()

    @declarative.dproperty
    def ActuatorD(self):
        return mechanical.DisplacementSourceBalanced()

    @declarative.dproperty
    def Mn(self):
        return mechanical.Mass(
            mass_kg = self.mn
        )

    @declarative.dproperty
    def M1(self):
        return mechanical.Mass(
            mass_kg = self.m1
        )

    @declarative.dproperty
    def M2(self):
        return mechanical.Mass(
            mass_kg = self.m2
        )

    @declarative.dproperty
    def M3(self):
        return mechanical.Mass(
            mass_kg = self.m3
        )

    @declarative.dproperty
    def Pendn(self):
        k, theta = pendulum_k(
            mass_kg   = self.Mn.mass_kg,
            length_m  = self.ln,
            r_fiber_m = self.rn,
            Ymod      = self.Yn,
            theta     = self.thetan,
        )
        return mechanical.SeriesSpring(
            elasticity_N_m     = k,
            loss_angle_by_freq = theta,
        )

    @declarative.dproperty
    def Pend1(self):
        k, theta = pendulum_k(
            mass_kg   = self.M1.mass_kg,
            length_m  = self.l1,
            r_fiber_m = self.r1,
            Ymod      = self.Y1,
            theta     = self.theta1,
        )
        return mechanical.SeriesSpring(
            elasticity_N_m     = k,
            loss_angle_by_freq = theta,
        )

    @declarative.dproperty
    def Pend2(self):
        k, theta = pendulum_k(
            mass_kg   = self.M2.mass_kg,
            length_m  = self.l2,
            r_fiber_m = self.r2,
            Ymod      = self.Y2,
            theta     = self.theta2,
        )
        return mechanical.SeriesSpring(
            elasticity_N_m     = k,
            loss_angle_by_freq = theta,
        )

    @declarative.dproperty
    def Pend3(self):
        k, theta = pendulum_k(
            mass_kg   = self.M3.mass_kg,
            length_m  = self.l3,
            r_fiber_m = self.r3,
            Ymod      = self.Y3,
            theta     = self.theta3,
        )
        return mechanical.SeriesSpring(
            elasticity_N_m     = k,
            loss_angle_by_freq = theta,
        )

    @declarative.dproperty
    def PendDn(self):
        return mechanical.SeriesDamper(
            resistance_Ns_m = .1,
            include_johnson_noise = False,
        )

    @declarative.dproperty
    def PendD1(self):
        return mechanical.SeriesDamper(
            resistance_Ns_m = .1,
            include_johnson_noise = False,
        )

    @declarative.dproperty
    def PendD2(self):
        return mechanical.SeriesDamper(
            resistance_Ns_m = .1,
            include_johnson_noise = False,
        )

    @declarative.dproperty
    def PendD3(self):
        return mechanical.SeriesDamper(
            resistance_Ns_m = .1,
            include_johnson_noise = False,
        )


    def __build__(self):
        try:
            super(QuadSusp, self).__build__()

            self.Platform.A.bond(self.ActuatorF.A)

            self.Pendn.A.bond(self.Platform.A)
            self.Pend1.A.bond(self.Pendn.B)
            self.Pend2.A.bond(self.Pend1.B)
            self.Pend3.A.bond(self.Pend2.B)

            self.Pendn.B.bond(self.Mn.A)
            self.Pend1.B.bond(self.M1.A)
            self.Pend2.B.bond(self.M2.A)
            self.Pend3.B.bond(self.M3.A)

            self.PendDn.A.bond(self.Pendn.A)
            self.PendD1.A.bond(self.Pend1.A)
            self.PendD2.A.bond(self.Pend2.A)
            self.PendD3.A.bond(self.Pend3.A)

            self.PendDn.B.bond(self.Pendn.B)
            self.PendD1.B.bond(self.Pend1.B)
            self.PendD2.B.bond(self.Pend2.B)
            self.PendD3.B.bond(self.Pend3.B)

            self.ActuatorF.B.bond(self.M3.A)
            self.ActuatorD.A.bond(self.ActuatorF.B)

            self.B_platform = self.Platform.A
            self.A_mirror = self.ActuatorD.B
        except Exception as E:
            print(repr(E))


class LIGODetector(base.SystemElementBase):
    def __init__(self, **kwargs):
        super(LIGODetector, self).__init__(**kwargs)

        base.OOA_ASSIGN(self).lossless = False

        base.OOA_ASSIGN(self).misalign_SR = False
        base.OOA_ASSIGN(self).missing_SR  = False
        base.OOA_ASSIGN(self).misalign_PR = False
        base.OOA_ASSIGN(self).missing_PR  = False
        base.OOA_ASSIGN(self).misalign_EX = False
        base.OOA_ASSIGN(self).misalign_EY = False

        base.OOA_ASSIGN(self).lPRC_m  = 57.656   # PRCL: lPRC_m = lPR + (lIX + lIY) / 2
        base.OOA_ASSIGN(self).lSRC_m  = 56.008   # SRCL: lSRC_m = lSR + (lIX + lIY) / 2
        base.OOA_ASSIGN(self).lasy_m  = 0.0504   # Schnupp Asy: lasy_m = lIX - lIY
        base.OOA_ASSIGN(self).lmean_m = 4.8298   # (lIX + lIY) / 2
        base.OOA_ASSIGN(self).larm_m  = 3994.5   # (lIX + lIY) / 2

        base.OOA_ASSIGN(self).lBS_IX_m  = self.lmean_m + self.lasy_m / 2  # distance [m] from BS to IX
        base.OOA_ASSIGN(self).lBS_IY_m  = self.lmean_m - self.lasy_m / 2  # distance [m] from BS to IY
        base.OOA_ASSIGN(self).lIX_EX_m  = self.larm_m                     # length [m] of the X arm
        base.OOA_ASSIGN(self).lIY_EY_m  = self.larm_m                     # length [m] of the Y armlplp
        base.OOA_ASSIGN(self).lBS_PR_m  = self.lPRC_m - self.lmean_m      # distance from PR to BS
        base.OOA_ASSIGN(self).lBS_SR_m  = self.lSRC_m - self.lmean_m      # distance from SR to BS
        base.OOA_ASSIGN(self).lPR_PR2_m = 16.6037                         # distance from PR to PR2
        base.OOA_ASSIGN(self).lPR2_BS_m = self.lBS_PR_m - self.lPR_PR2_m  # distance from PR2 to BS

        # optics.Mirror curvatures (all dimensions in meters)
        #Ri = 1934             # radius of curvature of input mirrors (IX and IY)
        #Re = 2245           # radius of curvature of end mirrors (EX and EY)
        #Rpr = -10.997          # radius of curvature of power recycling mirrors
        #Rpr2 = -4.555
        #Rsr = -5.6938      	# radius of curvature of signal recycling mirrors

        self.my.BS = optics.Mirror(
            T_hr = 0.5,
            L_hr = 37.5e-6 if not self.lossless else 0,
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )
        self.my.IX_sus = QuadSusp()
        self.my.IX = optics.Mirror(
            T_hr = 14e-3,
            L_hr = 0 if not self.lossless else 0,
            #facing_cardinal = 'E',
        )
        self.IX_sus.A_mirror.bond(self.IX.Z)
        self.my.EX_sus = QuadSusp()
        self.my.EX = optics.Mirror(
            T_hr = 5e-6,
            L_hr = 100e-6 if not self.lossless else 0,
            #facing_cardinal = 'W',
            AOI_deg = (1 if self.misalign_EX else 0),
        )
        self.EX_sus.A_mirror.bond(self.EX.Z)
        self.my.IY_sus = QuadSusp()
        self.my.IY = optics.Mirror(
            T_hr = 14e-3,
            L_hr = 0 if not self.lossless else 0,
            #facing_cardinal = 'N',
        )
        self.IY_sus.A_mirror.bond(self.IY.Z)
        self.my.EY_sus = QuadSusp()
        self.my.EY = optics.Mirror(
            T_hr = 5e-6,
            L_hr = 100e-6 if not self.lossless else 0,
            #facing_cardinal = 'S',
            AOI_deg = (1 if self.misalign_EY else 0),
        )
        self.EY_sus.A_mirror.bond(self.EY.Z)
        if not self.missing_PR:
            self.my.PR = optics.Mirror(
                T_hr = 30e-3,
                L_hr = 37.5e-6 if not self.lossless else 0,
                #facing_cardinal = 'E',
                AOI_deg = (5 if self.misalign_PR else 0),
            )
        else:
            self.my.PR = optics.Space(
                L_m = 0,
            )

        self.my.PR2 = optics.Mirror(
            T_hr = 1 - 250e-6,
            L_hr = 37.5e-6 if not self.lossless else 0,
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )
        if not self.missing_SR:
            self.my.SR = optics.Mirror(
                #T_hr = 350e-3,
                T_hr = 200e-3,
                L_hr = 37.5e-6 if not self.lossless else 0,
                #facing_cardinal = 'S',
                AOI_deg = (5 if self.misalign_SR else 0),
            )
        else:
            self.my.SR = optics.Space(
                L_m = 0,
            )

        self.my.S_BS_IX  = optics.Space(L_m = self.lBS_IX_m )
        self.my.S_BS_IY  = optics.Space(L_m = self.lBS_IY_m )
        self.my.S_IX_EX  = optics.Space(L_m = self.lIX_EX_m )
        self.my.S_IY_EY  = optics.Space(L_m = self.lIY_EY_m )
        self.my.S_BS_SR  = optics.Space(L_m = self.lBS_SR_m )
        self.my.S_PR_PR2 = optics.Space(L_m = self.lPR_PR2_m)
        self.my.S_PR2_BS = optics.Space(L_m = self.lPR2_BS_m)

        self.my.REFLPD = optics.MagicPD(
            #facing_cardinal = 'E',
        )
        self.my.POPTruePD = optics.MagicPD(
            #facing_cardinal = 'W',
        )
        self.my.POPPD = optics.PD()
        self.my.XarmPD = optics.MagicPD(
            #facing_cardinal = 'W',
        )
        self.my.XtransPD = optics.PD()
        self.my.YarmPD = optics.MagicPD(
            #facing_cardinal = 'S',
        )
        self.my.YtransPD = optics.PD()
        self.my.asymPD = optics.PD()

        self.system.bond_sequence(
            self.REFLPD.Fr,
            self.PR.Fr,
            self.POPTruePD.Bk,
            self.S_PR_PR2.Fr,
            self.PR2.BkA,
            self.S_PR2_BS.Fr,
            self.BS.FrA,
            self.S_BS_IX.Fr,
            self.IX.Fr,
            self.XarmPD.Bk,
            self.S_IX_EX.Fr,
            self.EX.Bk,
            self.XtransPD.Fr,
        )
        self.system.bond_sequence(
            self.SR.Fr,
            self.S_BS_SR.Fr,
            self.BS.BkB,
            self.S_BS_IY.Fr,
            self.IY.Fr,
            self.YarmPD.Fr,
            self.S_IY_EY.Fr,
            self.EY.Bk,
            self.YtransPD.Fr,
        )

        self.my.PR2_vac = optics.VacuumTerminator()
        self.system.bond_sequence(
            self.PR2_vac.Fr,
            self.PR2.BkB,
            self.POPPD.Fr,
        )

        self.my.XtransDC = readouts.DCReadout(
            port = self.XtransPD.Wpd.o,
        )
        self.my.XarmDC = readouts.DCReadout(
            port = self.XarmPD.Wpd.o,
        )
        self.my.YtransDC = readouts.DCReadout(
            port = self.YtransPD.Wpd.o,
        )
        self.my.YarmDC = readouts.DCReadout(
            port = self.YarmPD.Wpd.o,
        )
        self.my.REFLDC = readouts.DCReadout(
            port = self.REFLPD.Wpd.o,
        )
        self.my.POPDC = readouts.DCReadout(
            port = self.POPPD.Wpd.o,
        )
        self.my.POPTrueDC = readouts.DCReadout(
            port = self.POPTruePD.Wpd.o,
        )

        self.my.actuate_DARM_m = signals.DistributionAmplifier(
            port_gains = dict(
                EX = -1 / 2,
                EY = +1 / 2,
            )
        )
        self.system.bond(self.actuate_DARM_m.EX, self.EX_sus.ActuatorD.d)
        self.system.bond(self.actuate_DARM_m.EY, self.EY_sus.ActuatorD.d)

        self.my.actuate_DARM_N = signals.DistributionAmplifier(
            port_gains = dict(
                EX = -1 / 2,
                EY = +1 / 2,
            )
        )
        self.system.bond(self.actuate_DARM_N.EX, self.EX_sus.ActuatorF.F)
        self.system.bond(self.actuate_DARM_N.EY, self.EY_sus.ActuatorF.F)

        self.my.actuate_CARM_m = signals.DistributionAmplifier(
            port_gains = dict(
                EX = 1,
                EY = 1,
            )
        )
        self.system.bond(self.actuate_CARM_m.EX, self.EX_sus.ActuatorD.d)
        self.system.bond(self.actuate_CARM_m.EY, self.EY_sus.ActuatorD.d)

        self.my.actuate_CARM_N = signals.DistributionAmplifier(
            port_gains = dict(
                EX = 1,
                EY = 1,
            )
        )
        self.system.bond(self.actuate_CARM_N.EX, self.EX_sus.ActuatorF.F)
        self.system.bond(self.actuate_CARM_N.EY, self.EY_sus.ActuatorF.F)

        self.my.testpoint_DARM_pos_m = signals.SummingAmplifier(
            port_gains = dict(
                EX = -1,
                EY = +1,
            )
        )
        self.system.bond(self.EX.Z.d, self.testpoint_DARM_pos_m.EX)
        self.system.bond(self.EY.Z.d, self.testpoint_DARM_pos_m.EY)

        self.my.testpoint_CARM_pos_m = signals.SummingAmplifier(
            port_gains = dict(
                EX = +1 / 2,
                EY = +1 / 2,
            )
        )
        self.system.bond(self.EX.Z.d, self.testpoint_CARM_pos_m.EX)
        self.system.bond(self.EY.Z.d, self.testpoint_CARM_pos_m.EY)

        #since it is facing east
        self.INPUT_ATTACH_POINT = self.REFLPD.Bk
        #since it is facing south
        self.OUTPUT_ATTACH_POINT = self.SR.Bk
        return


class LIGOInputBasic(base.SystemElementBase):
    def __init__(self, **kwargs):
        super(LIGOInputBasic, self).__init__(**kwargs)
        self.my.F9 = base.Frequency(
            F_Hz  = 9099471,
            order = 0,
        )
        self.my.F45 = base.Frequency(
            F_Hz  = 45497355,
            order = 0,
        )
        self.my.generateF9 = signals.SignalGenerator(
            F = self.F9,
            harmonic_gains = {3 : 1},
        )
        self.my.generateF45 = signals.SignalGenerator(
            F = self.F45,
            harmonic_gains = {3 : 1},
        )
        self.my.EOM_drive = signals.SummingAmplifier(
            port_gains = dict(
                index_9  = .1,
                index_45 = .1,
            )
        )

        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 200,
            name = "PSL",
        )

        self.my.EOM = optics.PM()

        self.system.bond_sequence(
            self.PSL.Fr,
            self.EOM.Fr,
        )

        self.INPUT_ATTACH_POINT = self.EOM.Bk


class LIGOOutputBasic(base.SystemElementBase):
    def __init__(self, LIGO_obj, **kwargs):
        super(LIGOOutputBasic, self).__init__(**kwargs)
        self.my.ASPD = optics.PD()

        self.my.ASPD_DC = readouts.DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.my.ASPD_AC = readouts.ACReadout(
            portN = self.ASPD.Wpd.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )

        self.OUTPUT_ATTACH_POINT = self.ASPD.Fr


class LIGOOutputHomodyne(base.SystemElementBase):
    def __init__(
            self,
            input_obj,
            LIGO_obj,
            **kwargs
    ):
        super(LIGOOutputHomodyne, self).__init__(**kwargs)

        self.my.ASPD = optics.MagicPD(
            #facing_cardinal = 'N',
        )
        self.my.AS_vac = optics.VacuumTerminator()
        self.my.ASPDHD_lossless = optics.HiddenVariableHomodynePD(
            source_port     = input_obj.PSL.Fr.o,
            phase_deg       = 90,
            include_quanta  = True,
            #facing_cardinal = 'N',
        )

        base.OOA_ASSIGN(self).AS_efficiency_percent = 85
        self.my.AS_loss = optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.AS_efficiency_percent * 1e-2,
            #facing_cardinal = 'N',
            AOI_deg = 0,
        )

        self.my.ASPDHD = optics.HiddenVariableHomodynePD(
            source_port     = input_obj.PSL.Fr.o,
            phase_deg       = 90,
            include_quanta  = True,
            #facing_cardinal = 'N',
        )

        self.my.ASPDHD_DC_I = readouts.DCReadout(
            port = self.ASPDHD.rtWpdI.o,
        )
        self.my.ASPDHD_AC_I = readouts.ACReadout(
            portN = self.ASPDHD.rtWpdI.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )
        self.my.ASPDHD_DC_Q = readouts.DCReadout(
            port = self.ASPDHD.rtWpdQ.o,
        )
        self.my.ASPDHD_AC_Q = readouts.ACReadout(
            portN = self.ASPDHD.rtWpdQ.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )

        self.my.ASPDHD_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD.rtWpdI.o,
            portNQ = self.ASPDHD.rtWpdQ.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )
        self.my.ASPDHDll_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtWpdI.o,
            portNQ = self.ASPDHD_lossless.rtWpdQ.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )
        self.my.qASPDHD_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD.rtQuantumI.o,
            portNQ = self.ASPDHD.rtQuantumQ.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )
        self.my.qASPDHDll_AC = readouts.HomodyneACReadout(
            portNI = self.ASPDHD_lossless.rtQuantumI.o,
            portNQ = self.ASPDHD_lossless.rtQuantumQ.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )

        self.my.ASPD_DC = readouts.DCReadout(
            port = self.ASPD.Wpd.o,
        )
        self.my.ASPD_AC = readouts.ACReadout(
            portN = self.ASPD.Wpd.o,
            portD = LIGO_obj.actuate_DARM_m.I.i,
        )

        #TODO add loss
        self.system.bond_sequence(
            self.ASPD.Bk,
            self.ASPDHD_lossless.Fr,
            self.AS_loss.Fr,
            self.ASPDHD.Fr,
            self.AS_vac.Fr,
        )
        self.OUTPUT_ATTACH_POINT = self.ASPD.Fr


class LIGOBasicOperation(base.SystemElementBase):
    def __init__(self, **kwargs):
        super(LIGOBasicOperation, self).__init__(**kwargs)
        self.my.LIGO = LIGODetector()
        self.my.input  = LIGOInputBasic()
        #self.output = LIGOOutputBasic(LIGO_obj = self.LIGO)
        self.my.output = LIGOOutputHomodyne(
            LIGO_obj  = self.LIGO,
            input_obj = self.input,
        )

        self.system.bond_sequence(
            self.input.INPUT_ATTACH_POINT,
            self.LIGO.INPUT_ATTACH_POINT,
        )

        self.system.bond_sequence(
            self.LIGO.OUTPUT_ATTACH_POINT,
            self.output.OUTPUT_ATTACH_POINT,
        )


