"""
"""
from __future__ import division, print_function
import numpy as np
import declarative

from ... import optics
from ... import base
from ... import signals
from ... import readouts
from ... import mechanical
#from ... import system

from .AOM import AOM1XBasic
from .OPO import OPOaLIGO
from .SHG import SHGaLIGO
from .VCO import VCO


#From E1500445
class FilterCavity16m(optics.OpticalCouplerBase):

    @declarative.dproperty
    def M1(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = 60e-6,
                    #T_hr = 10*60e-6,
                    L_hr = 5e-6,
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1500e-6,
                ),
                AOI_deg = 0,
            )
        return val

    @declarative.dproperty
    def S1(self, val = None):
        if val is None:
            val = optics.Space(L_m = 16)
        return val

    @declarative.dproperty
    def M2(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = 1e-6,
                    #T_hr = 60e-6 + 1e-6,
                    L_hr = 5e-6,
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1500e-6,
                ),
                AOI_deg = 0,
            )
        return val

    def __build__(self):
        try:
            super(FilterCavity16m, self).__build__()
            self.my.PD = optics.MagicPD()
            self.my.DC = readouts.DCReadout(
                port = self.PD.Wpd.o,
            )
            self.M1.Fr.bond_sequence(
                self.PD.Fr,
                self.S1.Fr,
                self.M2.Fr,
            )
            self.Fr = self.M1.Bk
            self.Bk = self.M2.Bk
            return
        except Exception as E:
            print(repr(E))

class NPRO(optics.OpticalCouplerBase):

    @declarative.dproperty
    def laser(self, val = None):
        if val is None:
            return optics.Laser(
                F = self.system.F_carrier_1064,
                power_W = 1,
                multiple = 1,
                phase_deg = 0,
            )
        else:
            return val

    @declarative.dproperty
    def noise_mod(self):
        return optics.AMPM()

    @declarative.dproperty
    def AM_SPEC(self):
        return signals.SRationalFilter(
            poles_c = (-1e6 + 1.8e6j,),
            gain = 1e-7,
        )

    @declarative.dproperty
    def FM_SPEC(self, val = None):
        if val is None:
            return signals.SRationalFilter(
                poles_r = (-1e-4, ),
                gain = 1e4,
                gain_F_Hz = 1,
            )
        return val

    @declarative.dproperty
    def FM2PM(self, val = None):
        if val is None:
            return signals.SRationalFilter(
                poles_r = (-1e-4,),
                gain = 1,
                gain_F_Hz = 1,
            )
        return val

    @declarative.dproperty
    def noise_FM(self):
        return signals.WhiteNoise(
            name_noise = 'NPRO FM',
            sided = 'single',
            port = self.FM_SPEC.In,
        )

    @declarative.dproperty
    def noise_AM(self):
        return signals.WhiteNoise(
            name_noise = 'NPRO AM',
            sided = 'single',
            port = self.AM_SPEC.In,
        )

    def __build__(self):
        try:
            super(NPRO, self).__build__()
            self.laser.Fr.bond(self.noise_mod.Fr)
            self.Fr = self.noise_mod.Bk

            self.noise_mod.DrvAM.bond(self.AM_SPEC.Out)
            self.FM2PM.In.bond(self.FM_SPEC.Out)
            self.noise_mod.DrvPM.bond(self.FM2PM.Out)
            return
        except Exception as E:
            print(repr(E))


class ELFTestStand(optics.OpticalCouplerBase):
    """
    Shows the Squeezing performance
    """

    @declarative.dproperty
    def FC(self):
        return FilterCavity16m()

    @declarative.dproperty
    def F_ELF(self):
        val = base.Frequency(
            #F_Hz  = (1 + 1.5e-6) * self.symbols.c_m_s / (2*16),
            F_Hz  = (1) * self.symbols.c_m_s / (2*16),
            order = 1,
        )
        return val

    @declarative.dproperty
    def PSL_IFO(self):
        return NPRO(
            laser = optics.Laser(
                F = self.system.F_carrier_1064,
                power_W = 1,
                multiple = 1,
                phase_deg = 0,
            ),
            #from G1501370
            FM_SPEC = signals.SRationalFilter(
                poles_r   = (-1e4, ),
                zeros_r   = (-1e2, ),
                gain      = 1e-4,
                gain_F_Hz = 1e4,
            ),
        )

    @declarative.dproperty
    def BS_backscatter(self):
        return optics.Mirror(
            T_hr = .1e-6,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def faraday_backscatter(self):
        val = optics.OpticalCirculator(
            N_ports = 3,
        )
        return val

    @declarative.dproperty
    def faraday_elfs(self):
        val = optics.OpticalCirculator(
            N_ports = 3,
        )
        return val

    @declarative.dproperty
    def hdyne_backscatter(self):
        return optics.HiddenVariableHomodynePD(
            source_port = self.BS_backscatter.FrB.o,
            include_quanta = True,
        )

    @declarative.dproperty
    def PSL_SQZ(self):
        return NPRO(
            laser = optics.Laser(
                F = self.system.F_carrier_1064,
                power_W = 5e-3,
                multiple = 1,
                phase_deg = 0,
                polarization = 'P',
            )
        )

    @declarative.dproperty
    def beat_rotator(self):
        return optics.PolarizationRotator(rotate_deg = 90)

    @declarative.dproperty
    def FC_pol_inj(self):
        return optics.PolarizingSelector()

    @declarative.dproperty
    def VCO_ELF(self):
        return VCO(
            f_dict = {self.F_ELF : 1},
        )

    @declarative.dproperty
    def AOM_GEN_ELF(self):
        val = optics.AOMBasic()
        return val

    @declarative.dproperty
    def BS_ELF(self):
        return optics.Mirror(
            T_hr = .5,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def BS_PSL_Beat(self):
        return optics.Mirror(
            T_hr = 20e-3,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def BS_PSL_Beat12(self):
        return optics.Mirror(
            T_hr = .5,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def BS_MZ1(self):
        return optics.Mirror(
            T_hr = .5,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def BS_MZ2(self):
        return optics.Mirror(
            T_hr = .5,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def M_MZ(self):
        return optics.Mirror(
            T_hr = 0,
            AOI_deg = 45,
            phase_deg = 45,
        )

    @declarative.dproperty
    def BS_MZ_PO(self):
        return optics.Mirror(
            T_hr = 0,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def BS_Beat(self):
        return optics.Mirror(
            T_hr = .5,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def BeatPD(self):
        return optics.MagicPD()

    @declarative.dproperty
    def BS_Beat2(self):
        return optics.Mirror(
            T_hr = .5,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def BeatPD2(self):
        return optics.MagicPD()

    @declarative.dproperty
    def MZPD(self):
        return optics.MagicPD()

    @declarative.dproperty
    def MZPD2(self):
        return optics.MagicPD()

    @declarative.dproperty
    def Mix_ELF(self):
        return signals.Mixer()

    @declarative.dproperty
    def Mix_ELF2(self):
        return signals.Mixer()

    @declarative.dproperty
    def ActuatorFC(self):
        return mechanical.ForceSourceBalanced()

    @declarative.dproperty
    def FC_Pend_M(self):
        return mechanical.Mass(
            mass_kg = 1, #.0885
        )

    @declarative.dproperty
    def FC_Pend_k(self):
        k_pendL = self.FC_Pend_M.mass_kg * 9.81 / .14
        return mechanical.SeriesSpring(
            elasticity_N_m = k_pendL
        )

    @declarative.dproperty
    def FC_Pend_d(self):
        return mechanical.SeriesDamper(
            resistance_Ns_m = 1e-2
        )

    @declarative.dproperty
    def Ground(self):
        return mechanical.DisplacementSource()

    @declarative.dproperty
    def FC_length_loop(self):
        return readouts.ACReadoutLG(
            portAct   = self.FC.M2.Z.d.o,
            portSense = self.FeedbackFC.In.i,
            portDrv   = self.ActuatorFC.F.i,
        )

    @declarative.dproperty
    def FCMZ_length_loop(self):
        return readouts.ACReadoutLG(
            portAct   = self.FC.M2.Z.d.o,
            portSense = self.FeedbackMZFC.In.i,
            portDrv   = self.ActuatorFC.F.i,
        )

    @declarative.dproperty
    def FeedbackFC(self):
        Px = (-60 + 120j)
        Zx = (-50 + 70j)

        Px2 = (-10 + 30j)
        Zx2 = (-30 + 30j)

        #the first two are force-too-disp
        return signals.SRationalFilter(
            poles_r = (-1e3, -1, -1,),
            zeros_r = (-100, -60, -100, -100,),
            poles_c = (8*Px,  -2000+2000j, -50+150j),
            zeros_c = (8*Zx,  -150+150j),
            gain    = 0 * -2 / 2e4 / 4.85075673233e-5 / 61.8415 / .5012,
            gain_F_Hz = 1e3,
            no_DC   = True,
            F_cutoff = 1e6,
        )

    @declarative.dproperty
    def FeedbackMZFC(self):
        Px = (-60 + 120j)
        Zx = (-50 + 70j)

        Px2 = (-10 + 30j)
        Zx2 = (-30 + 30j)

        #the first two are force-too-disp
        return signals.SRationalFilter(
            poles_r = (-1e3, -1, -1,),
            zeros_r = (-100, -60, -100, -100,),
            poles_c = (8*Px,  -2000+2000j, -50+150j),
            zeros_c = (8*Zx,  -150+150j),
            gain    = -2 / 2e4 / 4.85075673233e-5 / 61.8415 / .250602,
            gain_F_Hz = 1e3,
            no_DC   = True,
            F_cutoff = 1e6,
        )

    @declarative.dproperty
    def FeedbackELF2NPROFM(self):
        #the first two are force-too-disp
        return signals.SRationalFilter(
            #butterworth compensation good but too aggressive for the simulation
            poles_r = (-1, -1, -1,),  # -1, -1),
            #zeros_r = ()
            zeros_c = (-20000 + 20000j,),  # -1000 + 1000j,),
            gain    = 1 / .001250474,
            gain_F_Hz = 1e5,
            no_DC   = True,
            F_cutoff = 1e6,
        )

    @declarative.dproperty
    def FC_FM_loop(self):
        return readouts.ACReadoutLG(
            portAct   = self.FeedbackELF2NPROFM.Out.o,
            portSense = self.FeedbackELF2NPROFM.In.i,
            portDrv   = self.FeedbackELF2NPROFM.Out.o,
        )

    def __build__(self):
        super(ELFTestStand, self).__build__()

        self.FC_pol_inj.Fr.bond_sequence(
            self.FC.Fr,
        )

        self.AOM_GEN_ELF.Drv.bond(
            self.VCO_ELF.Out,
        )

        #self.my.BS_SQZ = optics.Mirror(
        #    T_hr = 1 - 5e-3,
        #    AOI_deg = 45,
        #)

        self.PSL_IFO.Fr.bond_sequence(
            #self.BS_SQZ.FrA,
            self.BS_backscatter.FrA,
            self.faraday_backscatter.P0,
        )

        #self.my.rot_SQZ = optics.PolarizationRotator(rotate_deg = 90)
        #self.BS_SQZ.FrB.bond_sequence(
        #    self.rot_SQZ.Fr,
        self.PSL_SQZ.Fr.bond_sequence(
            #self.faraday_elfs.P0,
            self.AOM_GEN_ELF.Fr,
        )
        self.AOM_GEN_ELF.Bk.bond_sequence(
            self.BS_ELF.FrA,
            self.BS_MZ1.FrA,
            self.faraday_elfs.P0,
        )

        self.BS_MZ1.FrB.bond_sequence(
            self.M_MZ.FrA,
        )
        self.M_MZ.FrB.bond_sequence(
            self.BS_MZ2.BkB,
        )
        self.BS_MZ2.BkA.bond_sequence(
            self.MZPD.Fr,
        )
        self.BS_MZ2.FrB.bond_sequence(
            self.MZPD2.Fr,
        )

        self.faraday_elfs.P1.bond_sequence(
            self.FC_pol_inj.Bk_P,
        )
        self.faraday_elfs.P2.bond_sequence(
            self.BS_MZ_PO.FrA,
            self.BS_MZ2.FrA,
        )

        self.BS_MZ_PO.FrB.bond_sequence(
            self.BS_Beat.FrA,
            self.BeatPD.Fr,
        )

        self.BS_ELF.FrB.bond_sequence(
            self.BS_Beat2.FrA,
            self.BeatPD2.Fr,
        )

        self.BS_backscatter.FrB.bond_sequence(
            self.BS_PSL_Beat.FrA,
            self.beat_rotator.Fr,
            self.BS_PSL_Beat12.FrA,
            self.BS_Beat.BkB,
        )
        self.BS_PSL_Beat12.FrB.bond_sequence(
            self.BS_Beat2.BkB,
        )

        self.faraday_backscatter.P1.bond_sequence(
            self.FC_pol_inj.Bk_S,
        )

        self.my.M_hdyne = optics.Mirror(
            T_hr = 0,
            phase_deg = 00,
            AOI_deg = 45,
        )
        self.faraday_backscatter.P2.bond_sequence(
            self.M_hdyne.FrA,
        )
        self.my.BS_backscatter_read = optics.Mirror(
            T_hr = .5,
            AOI_deg = 45,
        )
        self.my.pd_backscatter = optics.MagicPD()
        self.M_hdyne.FrB.bond_sequence(
            self.hdyne_backscatter.Fr,
            self.BS_backscatter_read.FrA,
            self.pd_backscatter.Fr,
        )
        self.BS_backscatter_read.BkB.bond_sequence(
            self.BS_PSL_Beat.FrB,
        )

        self.my.DC_BeatPD = readouts.DCReadout(
            port = self.BeatPD.Wpd.o,
        )

        self.Mix_ELF.LO.bond(
            self.VCO_ELF.Out,
        )
        self.Mix_ELF.I.bond(
            self.BeatPD.Wpd,
        )
        self.my.DC_ELF_I = readouts.DCReadout(
            port = self.Mix_ELF.R_I.o
        )
        self.my.DC_ELF_Q = readouts.DCReadout(
            port = self.Mix_ELF.R_Q.o
        )

        self.Mix_ELF2.LO.bond(
            self.VCO_ELF.Out,
        )
        self.Mix_ELF2.I.bond(
            self.BeatPD2.Wpd,
        )
        self.my.DC_ELF2_I = readouts.DCReadout(
            port = self.Mix_ELF2.R_I.o
        )
        self.my.DC_ELF2_Q = readouts.DCReadout(
            port = self.Mix_ELF2.R_Q.o
        )
        self.my.DC_MZ = readouts.DCReadout(
            port = self.MZPD.Wpd.o,
        )

        self.Mix_ELF.R_Q.bond_sequence(
            self.FeedbackFC.In,
            self.ActuatorFC.F,
        )

        self.MZPD.Wpd.bond_sequence(
            self.FeedbackMZFC.In,
            self.ActuatorFC.F,
        )

        self.Mix_ELF2.R_Q.bond_sequence(
            self.FeedbackELF2NPROFM.In,
            self.PSL_SQZ.noise_mod.DrvPM,
        )

        self.Ground.A.bond(self.FC_Pend_d.A)
        self.Ground.A.bond(self.FC_Pend_k.A)
        self.Ground.A.bond(self.ActuatorFC.A)

        self.FC.M2.Z.bond(self.ActuatorFC.B)
        self.FC.M2.Z.bond(self.FC_Pend_k.B)
        self.FC.M2.Z.bond(self.FC_Pend_d.B)
        self.FC.M2.Z.bond(self.FC_Pend_M.A)

        Q3 = -.1 + 1j
        self.my.ground_spec = signals.SRationalFilter(
            poles_c = (
                1*Q3,
                3*Q3,
                7*Q3,
                11*Q3
            ),
            poles_r = (-1, -1),
            gain = 2e-8,
        )
        self.my.noise = signals.WhiteNoise(
            port = self.ground_spec.In,
            sided = 'single',
            name_noise = 'Seismic Stack',
        )
        self.ground_spec.Out.bond(self.Ground.d)

        self.my.AC_FC_length = readouts.ACReadout(
            portN = self.FC.M2.Z.d.o,
            portD = self.ground_spec.Out.o,
        )

        self.my.AC_FC_force = readouts.ACReadout(
            portN = self.ActuatorFC.F.i,
            portD = self.ground_spec.Out.o,
        )

        self.my.AC_hdyne_dispI = readouts.ACReadout(
            portN = self.hdyne_backscatter.rtQuantumI.o,
            portD = self.ground_spec.In.i,
        )
        self.my.AC_hdyne_dispQ = readouts.ACReadout(
            portN = self.hdyne_backscatter.rtQuantumQ.o,
            portD = self.ground_spec.In.i,
        )

        self.my.AC_ground = readouts.ACReadout(
            portN = self.ground_spec.Out.o,
            portD = self.ground_spec.In.i,
        )

        self.my.AC_FM = readouts.ACReadout(
            portN = self.hdyne_backscatter.rtQuantumQ.o,
            #portD = self.PSL_SQZ.noise_mod.DrvPM.i,
            portD = self.PSL_SQZ.FM_SPEC.In.i,
        )

        self.my.AC_ELF2 = readouts.ACReadout(
            portN = self.Mix_ELF2.R_Q.o,
            portD = self.PSL_SQZ.FM_SPEC.In.i,
        )
        self.my.AC_ELF2_IFO= readouts.ACReadout(
            portN = self.Mix_ELF2.R_Q.o,
            portD = self.PSL_IFO.FM_SPEC.In.i,
        )

        self.my.AC_MZPD = readouts.ACReadout(
            portN = self.MZPD.Wpd.o,
            #portD = self.PSL_SQZ.noise_mod.DrvPM.i,
            portD = self.PSL_SQZ.FM_SPEC.In.i,
        )

        self.my.AC_MZPD2 = readouts.ACReadout(
            portN = self.MZPD.Wpd.o,
            #portD = self.PSL_SQZ.noise_mod.DrvPM.i,
            portD = self.PSL_SQZ.FM_SPEC.In.i,
        )

        self.my.AC_backscatter = readouts.ACReadout(
            portN = self.pd_backscatter.Wpd.o,
            #portD = self.PSL_SQZ.noise_mod.DrvPM.i,
            portD = self.PSL_SQZ.FM_SPEC.In.i,
        )






#seismic = 2e-8 / F**2
