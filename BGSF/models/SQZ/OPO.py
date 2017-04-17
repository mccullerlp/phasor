"""
"""
from __future__ import division, print_function
import declarative
import numpy as np
from ... import optics
from ... import base
from ... import signals
from ... import readouts
#from ... import system


def dist_m_from_XY_mm(A, B):
    V = A - B
    return 1e-3 * np.dot(V, V)**.5


#FROM dcc E1600051, and T1700104
class OPOaLIGO(optics.OpticalCouplerBase):

    @declarative.dproperty
    def M1_loc_XY_mm(self, val = (21.104, 18.258)):
        return np.array(val)

    @declarative.dproperty
    def M2_loc_XY_mm(self, val = (-85.897, 18.258)):
        return np.array(val)

    @declarative.dproperty
    def M3_loc_XY_mm(self, val = (0, 0)):
        return np.array(val)

    @declarative.dproperty
    def KTP_loc_XY_mm(self, val = (-24.406, 0.0)):
        return np.array(val)

    @declarative.dproperty
    def M4_loc_XY_mm(self, val = (-59.359, .517)):
        return np.array(val)

    @declarative.dproperty
    def M1(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = 1 - .875,
                    flip_sign = True,
                    L_hr = .001
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1 - .875,
                    L_hr = .001,
                ),
                AOI_deg = -6,
            )
        return val

    @declarative.dproperty
    def S_1_2(self, val = None):
        if val is None:
            val = optics.Space(
                L_m = dist_m_from_XY_mm(
                    self.M1_loc_XY_mm,
                    self.M2_loc_XY_mm,
                ),
                L_detune_m = 0
            )
        return val

    @declarative.dproperty
    def M2(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = 0,#1 - .9985,
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1 - .999,
                ),
                AOI_deg = -174,
            )
        return val

    @declarative.dproperty
    def S_2_3(self, val = None):
        if val is None:
            val = optics.Space(
                L_m = dist_m_from_XY_mm(
                    self.M2_loc_XY_mm,
                    self.M3_loc_XY_mm,
                ),
                L_detune_m = 0
            )
        return val

    @declarative.dproperty
    def M3(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = 0,#1 - .9985,
                    flip_sign = True,
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1 - .999,
                ),
                AOI_deg = 6,
            )
        return val

    @declarative.dproperty
    def S_3_KTP(self, val = None):
        if val is None:
            val = optics.Space(
                L_m = dist_m_from_XY_mm(
                    self.M3_loc_XY_mm,
                    self.KTP_loc_XY_mm,
                ),
                L_detune_m = 0
            )
        return val

    @declarative.dproperty
    def ktp(self, val = None):
        if val is None:
            val = optics.NonlinearCrystal(
                nlg = .0015,
                length_mm = 10,
                N_ode = 10,
                symplectify = False,
                solution_order = 2,
            )
        return val

    @declarative.dproperty
    def S_KTP_4(self, val = None):
        if val is None:
            val = optics.Space(
                L_m = dist_m_from_XY_mm(
                    self.KTP_loc_XY_mm,
                    self.M4_loc_XY_mm,
                ),
                L_detune_m = 0
            )
        return val

    @declarative.dproperty
    def M4(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = 0,#1 - .9985,
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1 - .999,
                ),
                AOI_deg = 174,
            )
        return val

    @declarative.dproperty
    def S_4_1(self, val = None):
        if val is None:
            val = optics.Space(
                L_m = dist_m_from_XY_mm(
                    self.M3_loc_XY_mm,
                    self.M4_loc_XY_mm,
                ),
                L_detune_m = 0
            )
        return val

    def __build__(self):
        super(OPOaLIGO, self).__build__()

        self.my.PD = optics.MagicPD()

        self.M1.FrB.bond_sequence(self.PD.Bk, self.S_1_2.Fr)
        self.M2.FrA.bond(self.S_1_2.Bk)
        self.M2.FrB.bond(self.S_2_3.Fr)
        self.M3.FrA.bond(self.S_2_3.Bk)
        self.M3.FrB.bond(self.S_3_KTP.Fr)
        self.ktp.Fr.bond(self.S_3_KTP.Bk)
        self.ktp.Bk.bond(self.S_KTP_4.Fr)
        self.M4.FrA.bond(self.S_KTP_4.Bk)
        self.M4.FrB.bond(self.S_4_1.Fr)
        self.M1.FrA.bond(self.S_4_1.Bk)

        self.my.DC = readouts.DCReadout(
            port = self.PD.Wpd.o,
        )
        return


class OPOTestStand(optics.OpticalCouplerBase):
    """
    Shows the Squeezing performance
    """

    @declarative.dproperty
    def include_PM(self, val = True):
        """
        Number of iterations to use in the ODE solution
        """
        val = self.ooa_params.setdefault('include_PM', val)
        return val

    def __build__(self):
        super(OPOTestStand, self).__build__()
        self.my.PSLG = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = .02,
            multiple = 2,
            phase_deg = 0,
        )
        self.my.PSLGs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            multiple = 2,
            phase_deg = 90,
        )
        self.my.PSLRs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
            phase_deg = 45,
        )

        self.my.PD_R = optics.MagicPD()
        self.my.PD_G = optics.MagicPD()

        self.my.opo = OPOaLIGO()

        if self.include_PM:
            self.my.F_PM = base.Frequency(
                F_Hz  = 1e6,
                order = 1,
            )
            self.my.generateF_PM = signals.SignalGenerator(
                F = self.F_PM,
                amplitude = 0,
            )

            self.my.generateF_PMRead = signals.SignalGenerator(
                F = self.F_PM,
                amplitude = 0,
            )

        self.my.ditherPM = optics.PM()
        if self.include_PM:
            self.ditherPM.Drv.bond(self.generateF_PM.Out)

        self.my.ditherPMRead = optics.PM()
        if self.include_PM:
            self.ditherPMRead.Drv.bond(self.generateF_PMRead.Out)

        self.PSLRs.Fr.bond(self.my.ditherPMRead.Fr)
        self.my.hPD_R = optics.HiddenVariableHomodynePD(
            source_port = self.ditherPMRead.Bk.o,
            include_quanta = True,
        )
        self.my.hPD_G = optics.HiddenVariableHomodynePD(
            source_port = self.PSLGs.Fr.o,
            include_quanta = True,
        )

        self.PSLG.Fr.bond_sequence(
            self.ditherPM.Fr,
            self.opo.M1.BkA,
        )

        self.my.mDC_readout = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )

        self.opo.M1.BkB.bond_sequence(
            self.my.mDC_readout.FrA,
        )
        self.my.mDC_readout.FrB.bond_sequence(
            self.PD_G.Fr,
            self.hPD_G.Fr,
        )
        self.my.mDC_readout.BkA.bond_sequence(
            self.PD_R.Fr,
            self.hPD_R.Fr,
        )

        self.my.DC_R = readouts.DCReadout(
            port = self.PD_R.Wpd.o,
        )
        self.my.DC_G = readouts.DCReadout(
            port = self.PD_G.Wpd.o,
        )
        if self.ooa_params.setdefault('include_AC', True):
            self.my.AC_G = readouts.HomodyneACReadout(
                portNI = self.hPD_G.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.my.AC_R = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_R.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.my.AC_RGI = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumI.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.my.AC_RGQ = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumQ.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.my.AC_N = readouts.NoiseReadout(
                port_map = dict(
                    RI = self.hPD_R.rtQuantumI.o,
                    RQ = self.hPD_R.rtQuantumQ.o,
                    GI = self.hPD_G.rtQuantumI.o,
                    GQ = self.hPD_G.rtQuantumQ.o,
                )
            )

    def full_noise_matrix(self, lst = ['RI', 'RQ', 'GI', 'GQ'], display = True):
        arr = np.zeros((len(lst), len(lst)))
        for idx_L, NL in enumerate(lst):
            for idx_R, NR in enumerate(lst):
                val = self.AC_N.CSD[(NL, NR)].real
                print(NL, NR, val)
                arr[idx_L, idx_R] = val
        #clean up the presentation
        arr[arr < 1e-10] = 0
        if display:
            try:
                import tabulate
                tabular_data = [[label] + list(td) for label, td in zip(lst, arr)]
                print(tabulate.tabulate(tabular_data, headers = lst))
            except ImportError:
                print(lst, arr)
        return lst, arr


class OPOTestStandBackScatter(optics.OpticalCouplerBase):
    """
    Shows the backscatter performance, also with AC drive
    """




