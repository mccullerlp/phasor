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

class ELFTestStand(optics.OpticalCouplerBase):

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
    def F_RELF(self):
        val = base.Frequency(
            F_Hz  = self.symbols.c_m_s / (2*16)  * 3/4,
            order = 1,
        )
        return val

    @declarative.dproperty
    def PSL_IFO(self):
        return optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
            phase_deg = 0,
        )

    @declarative.dproperty
    def BS_backscatter(self):
        return optics.Mirror(
            T_hr = 1e-6,
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
        return optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 5e-3,
            multiple = 1,
            phase_deg = 0,
            polarization = 'P',
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
    def VCO_RELF(self):
        return VCO(
            f_dict = {self.F_RELF : 1}
        )

    @declarative.dproperty
    def AOM_GEN_CLF(self):
        val = optics.AOMBasic()
        return val

    @declarative.dproperty
    def BS_Beat(self):
        return optics.Mirror(
            T_hr = .5,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def BS_PSL_Beat(self):
        return optics.Mirror(
            T_hr = 10e-3,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def BeatPD(self):
        return optics.MagicPD()

    @declarative.dproperty
    def Mix_ELF(self):
        return signals.Mixer()

    @declarative.dproperty
    def Mix_RELF(self):
        return signals.Mixer()

    @declarative.dproperty
    def ActuatorFC(self):
        return mechanical.ForceSourceBalanced()

    @declarative.dproperty
    def FC_Pend_M(self):
        return mechanical.Mass(
            mass_kg = .0885
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
            resistance_Ns_m = 1e-3
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
            gain    = -2 / 2e4 / 4.85075673233e-5,
            no_DC   = True,
            F_cutoff = 1e6,
        )

    def __build__(self):
        super(ELFTestStand, self).__build__()

        self.FC_pol_inj.Fr.bond_sequence(
            self.FC.Fr,
        )

        self.AOM_GEN_CLF.Drv.bond(
            self.VCO_ELF.Out,
        )

        #self.AOM_GEN_CLF.Drv.bond(
        #    self.VCO_RELF.Out,
        #)

        self.PSL_SQZ.Fr.bond_sequence(
            #self.faraday_elfs.P0,
            self.AOM_GEN_CLF.Fr,
        )
        self.AOM_GEN_CLF.Bk.bond_sequence(
            self.faraday_elfs.P0,
        )

        self.faraday_elfs.P1.bond_sequence(
            self.FC_pol_inj.Bk_P,
        )
        self.faraday_elfs.P2.bond_sequence(
            self.BS_Beat.FrA,
            self.BeatPD.Fr,
        )

        self.BS_backscatter.FrB.bond_sequence(
            self.BS_PSL_Beat.FrA,
            self.beat_rotator.Fr,
            self.BS_Beat.BkB,
        )

        self.PSL_IFO.Fr.bond_sequence(
            self.BS_backscatter.FrA,
            self.faraday_backscatter.P0,
        )

        self.faraday_backscatter.P1.bond_sequence(
            self.FC_pol_inj.Bk_S,
        )
        self.faraday_backscatter.P2.bond_sequence(
            self.hdyne_backscatter.Fr,
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

        self.Mix_RELF.LO.bond(
            self.VCO_RELF.Out,
        )
        self.Mix_RELF.I.bond(
            self.BeatPD.Wpd,
        )
        self.my.DC_RELF_I = readouts.DCReadout(
            port = self.Mix_RELF.R_I.o
        )
        self.my.DC_RELF_Q = readouts.DCReadout(
            port = self.Mix_RELF.R_Q.o
        )

        self.Mix_ELF.R_Q.bond_sequence(
            self.FeedbackFC.In,
            self.ActuatorFC.F,
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






#seismic = 2e-8 / F**2
