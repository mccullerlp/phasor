"""
"""
from __future__ import division, print_function
import numpy as np
from ... import optics
from ... import readouts
#from ... import system


class KTPTestStand(optics.OpticalCouplerBase):
    def __build__(self):
        super(KTPTestStand, self).__build__()
        self.my.PSLG = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 0.,
            multiple = 2,
        )
        self.my.PSLR = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        self.my.PSLGs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            multiple = 2,
        )
        self.my.PSLRs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )

        self.my.PD_R = optics.MagicPD()
        self.my.PD_G = optics.MagicPD()
        self.my.ditherAM = optics.AM()

        self.my.ktp = optics.NonlinearCrystal(
            nlg = .1,
            length_mm = 10,
            N_ode = 20,
        )

        self.my.mDC1 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )
        self.my.mDC2 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )
        self.my.hPD_R = optics.HiddenVariableHomodynePD(
            source_port = self.PSLRs.Fr.o,
            include_quanta = True,
        )
        self.my.hPD_G = optics.HiddenVariableHomodynePD(
            #source_port = self.PSLGs.Fr.o,
            include_quanta = True,
        )

        self.PSLR.Fr.bond_sequence(
            self.mDC1.FrA,
            self.ditherAM.Fr,
            self.ktp.Fr,
            self.mDC2.FrA,
            self.PD_R.Fr,
            self.hPD_R.Fr,
        )
        self.PSLG.Fr.bond_sequence(
            self.mDC1.BkB,
        )
        self.mDC2.FrB.bond_sequence(
            self.PD_G.Fr,
            self.hPD_G.Fr,
        )

        self.my.DC_R = readouts.DCReadout(
            port = self.PD_R.Wpd.o,
        )
        self.my.DC_G = readouts.DCReadout(
            port = self.PD_G.Wpd.o,
        )
        self.my.AC_G = readouts.HomodyneACReadout(
            portNI = self.hPD_G.rtQuantumI.o,
            portNQ = self.hPD_G.rtQuantumQ.o,
            portD  = self.ditherAM.Drv.i,
        )
        self.my.AC_R = readouts.HomodyneACReadout(
            portNI = self.hPD_R.rtQuantumI.o,
            portNQ = self.hPD_R.rtQuantumQ.o,
            portD  = self.ditherAM.Drv.i,
        )
        self.my.AC_RGI = readouts.HomodyneACReadout(
            portNI = self.hPD_R.rtQuantumI.o,
            portNQ = self.hPD_G.rtQuantumI.o,
            portD  = self.ditherAM.Drv.i,
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
                arr[idx_L, idx_R] = self.AC_N.CSD[(NL, NR)].real
        if display:
            try:
                import tabulate
                tabular_data = [[label] + list(td) for label, td in zip(lst, arr)]
                print(tabulate.tabulate(tabular_data, headers = lst))
            except ImportError:
                print(lst, arr)
        return lst, arr
#print("A")
#pprint(self.ooa_params.test.PSL)
#print("self.DC_R.DC_readout", self.DC_R.DC_readout, 2)
#print("self.DC_G.DC_readout", self.DC_G.DC_readout, 1)
