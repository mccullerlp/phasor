"""
"""
from __future__ import division, print_function
import numpy as np
import declarative

from ... import optics
#from ... import base
#from ... import signals
from ... import readouts
#from ... import system


#FROM dcc E0900492
class SHGaLIGO(optics.OpticalCouplerBase):
    @declarative.dproperty
    def M1(self, val = None):
        val = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = .10,
                #flip_sign = True,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 1,
            ),
            AOI_deg = 0,
        )
        return val

    @declarative.dproperty
    def S1(self, val = None):
        val = optics.Space(L_m = (.033)/2)
        return val

    @declarative.dproperty
    def ktp(self, val = None):
        val = optics.NonlinearCrystal(
            nlg = .0024,
            length_mm = 10,
            N_ode = 20,
        )
        return val

    @declarative.dproperty
    def S2(self, val = None):
        val = optics.Space(L_m = (.033)/2)
        return val

    @declarative.dproperty
    def M2(self, val = None):
        val = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 0,
                L_hr = .001,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 0,
        )
        return val

    def __build__(self):
        super(SHGaLIGO, self).__build__()
        self.M1.FrA.bond_sequence(
            self.S1.Fr,
            self.ktp.Fr,
            self.S2.Fr,
            self.M2.FrA,
        )


class SHGTestStand(optics.OpticalCouplerBase):
    @declarative.dproperty
    def shg(self, val = None):
        val = SHGaLIGO()
        return val

    @declarative.dproperty
    def PSLR(self, val = None):
        val = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        return val

    @declarative.dproperty
    def PSLGs(self, val = None):
        val = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            multiple = 2,
            phase_deg = 90,
        )
        return val

    @declarative.dproperty
    def PSLRs(self, val = None):
        val = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        return val

    @declarative.dproperty
    def PD_R(self, val = None):
        val = optics.MagicPD()
        return val

    @declarative.dproperty
    def PD_G(self, val = None):
        val = optics.MagicPD()
        return val

    @declarative.dproperty
    def ditherPM(self, val = None):
        val = optics.PM()
        return val

    @declarative.dproperty
    def faraday(self, val = None):
        val = optics.OpticalCirculator(
            N_ports = 3,
        )
        return val

    @declarative.dproperty
    def mDC_readout(self, val = None):
        val = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
                L_hr = 0,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )
        return val

    @declarative.dproperty
    def hPD_R(self, val = None):
        val = optics.HiddenVariableHomodynePD(
            source_port = self.PSLRs.Fr.o,
            include_quanta = True,
        )
        return val

    @declarative.dproperty
    def hPD_G(self, val = None):
        val = optics.HiddenVariableHomodynePD(
            source_port = self.PSLGs.Fr.o,
            include_quanta = True,
        )
        return val

    @declarative.dproperty
    def DC_R(self, val = None):
        val = readouts.DCReadout(
            port = self.PD_R.Wpd.o,
        )
        return val

    @declarative.dproperty
    def DC_G(self, val = None):
        val = readouts.DCReadout(
            port = self.PD_G.Wpd.o,
        )
        return val

    @declarative.dproperty
    def AC_G(self, val = None):
        val = readouts.HomodyneACReadout(
            portNI = self.hPD_G.rtQuantumI.o,
            portNQ = self.hPD_G.rtQuantumQ.o,
            portD  = self.ditherPM.Drv.i,
        )
        return val

    @declarative.dproperty
    def AC_R(self, val = None):
        val = readouts.HomodyneACReadout(
            portNI = self.hPD_R.rtQuantumI.o,
            portNQ = self.hPD_R.rtQuantumQ.o,
            portD  = self.ditherPM.Drv.i,
        )
        return val

    @declarative.dproperty
    def AC_RGI(self, val = None):
        val = readouts.HomodyneACReadout(
            portNI = self.hPD_R.rtQuantumI.o,
            portNQ = self.hPD_G.rtQuantumI.o,
            portD  = self.ditherPM.Drv.i,
        )
        return val

    @declarative.dproperty
    def AC_RGQ(self, val = None):
        val = readouts.HomodyneACReadout(
            portNI = self.hPD_R.rtQuantumQ.o,
            portNQ = self.hPD_G.rtQuantumQ.o,
            portD  = self.ditherPM.Drv.i,
        )
        return val

    @declarative.dproperty
    def AC_N(self, val = None):
        val = readouts.NoiseReadout(
            port_map = dict(
                RI = self.hPD_R.rtQuantumI.o,
                RQ = self.hPD_R.rtQuantumQ.o,
                GI = self.hPD_G.rtQuantumI.o,
                GQ = self.hPD_G.rtQuantumQ.o,
            )
        )
        return val

    def __build__(self):
        super(SHGTestStand, self).__build__()

        self.PSLR.Fr.bond_sequence(
            self.ditherPM.Fr,
            self.faraday.P0,
        )
        self.faraday.P1.bond(
            self.shg.M1.Bk,
        )
        self.faraday.P2.bond_sequence(
            self.mDC_readout.FrA,
            self.PD_R.Fr,
            self.hPD_R.Fr,
        )
        self.mDC_readout.FrB.bond_sequence(
            self.PD_G.Fr,
            self.hPD_G.Fr,
        )
        return

    def full_noise_matrix(
            self,
            lst = [
                'RI',
                'RQ',
                'GI',
                'GQ',
            ],
            display = True
    ):
        arr = np.zeros((len(lst), len(lst)))
        for idx_L, NL in enumerate(lst):
            for idx_R, NR in enumerate(lst):
                val = self.AC_N.CSD[(NL, NR)].real
                arr[idx_L, idx_R] = val
                #clean up the presentation
        arr[abs(arr) < 1e-10] = 0
        if display:
            try:
                import tabulate
                tabular_data = [[label] + list(str(t) for t in td) for label, td in zip(lst, arr)]
                print(tabulate.tabulate(tabular_data, headers = lst))
            except ImportError:
                print(lst, arr)
        return lst, arr

