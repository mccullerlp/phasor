"""
"""
from __future__ import division, print_function
import numpy as np
from ... import optics
from ... import base
from ... import signals
from ... import readouts
from ...utilities.mpl.autoniceplot import mplfigB
#from ... import system


class KTPTestStand(optics.OpticalCouplerBase):
    def __build__(self):
        super(KTPTestStand, self).__build__()
        self.my.PSLG = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 0.,
            multiple = 2,
            phase_deg = 90,
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
            phase_deg = 90,
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
            source_port = self.PSLGs.Fr.o,
            include_quanta = True,
        )

        self.PSLR.Fr.bond_sequence(
            self.mDC1.BkA,
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
        if self.ooa_params.setdefault('include_AC', True):
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
#print("A")
#pprint(self.ooa_params.test.PSL)
#print("self.DC_R.DC_readout", self.DC_R.DC_readout, 2)
#print("self.DC_G.DC_readout", self.DC_G.DC_readout, 1)

class SHGTestStandResonant(optics.OpticalCouplerBase):
    def __build__(self):
        super(SHGTestStandResonant, self).__build__()
        self.my.PSLR = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
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
        )

        self.my.PD_R = optics.MagicPD()
        self.my.PD_G = optics.MagicPD()
        self.my.ditherPM = optics.PM()
        self.my.faraday = optics.OpticalCirculator(
            N_ports = 3,
        )

        self.my.mDC1 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = .10,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
                flip_sign = True,
            ),
            AOI_deg = 0,
        )
        self.my.S1 = optics.Space(L_m = 0, L_detune_m = 1064e-9 / 4)
        self.my.ktp = optics.NonlinearCrystal(
            nlg = .1,
            length_mm = 10,
            N_ode = 100,
        )
        self.my.S2 = optics.Space(L_m = 0, L_detune_m = -1064e-9 / 4)
        self.my.mDC2 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 0,
                L_hr = .001,
                flip_sign = True,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 1,
            ),
            AOI_deg = 0,
        )
        self.my.Sg = optics.Space(L_m = 0, L_detune_m = 0)
        self.my.mirror_gres = optics.Mirror(
            T_hr      = 1,
            L_hr      = .000,
            flip_sign = False,
            AOI_deg   = 0,
        )
        self.my.hPD_R = optics.HiddenVariableHomodynePD(
            source_port = self.PSLRs.Fr.o,
            include_quanta = True,
        )
        self.my.hPD_G = optics.HiddenVariableHomodynePD(
            source_port = self.PSLGs.Fr.o,
            include_quanta = True,
        )

        self.PSLR.Fr.bond_sequence(
            self.ditherPM.Fr,
            self.faraday.P0,
        )
        self.faraday.P1.bond_sequence(
            self.mDC1.FrA,
            self.S1.Fr,
            self.ktp.Fr,
            self.S2.Fr,
            self.mDC2.FrA,
            self.Sg.Fr,
            self.mirror_gres.Fr,
            self.PD_G.Fr,
            self.hPD_G.Fr,
        )
        self.faraday.P2.bond_sequence(
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


class OPOTestStandResonant(optics.OpticalCouplerBase):
    def __build__(self):
        super(OPOTestStandResonant, self).__build__()
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

        self.my.F_PM = base.Frequency(
            F_Hz  = 1e6,
            order = 1,
        )
        self.my.generateF_PM = signals.SignalGenerator(
            F = self.F_PM,
            amplitude = .1,
        )

        self.my.generateF_PMRead = signals.SignalGenerator(
            F = self.F_PM,
            amplitude = 0,
        )

        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 200,
            name = "PSL",
        )

        self.my.EOM = optics.PM()

        self.my.ditherPM = optics.PM()
        self.ditherPM.Drv.bond(self.generateF_PM.Out)

        self.my.ditherPMRead = optics.PM()
        self.ditherPMRead.Drv.bond(self.generateF_PMRead.Out)

        self.my.faraday = optics.OpticalCirculator(
            N_ports = 3,
        )

        self.my.mDC1 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 0,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = .1,
                flip_sign = True,
            ),
            AOI_deg = 0,
        )
        self.my.S1 = optics.Space(L_m = 0, L_detune_m = 1064e-9 / 4)
        self.my.ktp = optics.NonlinearCrystal(
            nlg = .1,
            length_mm = 10,
            N_ode = 100,
        )
        self.my.S2 = optics.Space(L_m = 0, L_detune_m = -1064e-9 / 4)
        self.my.mDC2 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = .1,
                flip_sign = True,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
                L_hr = .01,
            ),
            AOI_deg = 0,
        )
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
            self.faraday.P0,
        )
        self.faraday.P1.bond_sequence(
            self.mDC1.FrA,
            self.S1.Fr,
            self.ktp.Fr,
            self.S2.Fr,
            self.mDC2.FrA,
            self.PD_R.Fr,
            self.hPD_R.Fr,
        )
        self.faraday.P2.bond_sequence(
            self.PD_G.Fr,
            self.hPD_G.Fr,
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


def plot_power_and_noise(test, X_NLG = None):
    axB = mplfigB(Nrows=3)
    if X_NLG is None:
        X_NLG = test.ktp.length_mm.val
    axB.ax0.plot(
        X_NLG,
        test.DC_R.DC_readout,
        color = 'red',
        label = '1064 power',
    )
    axB.ax0.plot(
        X_NLG,
        test.DC_G.DC_readout,
        color = 'green',
        label = '532 power',
    )
    axB.ax0.plot(
        X_NLG,
        test.DC_R.DC_readout + test.DC_G.DC_readout,
        color = 'black',
        label = 'total power [W]',
    )
    #axB.ax0.set_ylim(0, .5)
    axB.ax0.set_ylabel('Readout Power [W]')
    axB.ax0.legend(
        fontsize = 8,
        loc = 'center left'
    )
    axB.ax1.plot(
        X_NLG,
        test.AC_R.AC_CSD_IQ[0, 0],
        color = 'red',
        label = 'amplitude quadrature',
    )
    axB.ax1.plot(
        X_NLG,
        test.AC_R.AC_CSD_IQ[1, 1],
        color = 'orange',
        label = 'phase quadrature',
    )
    axB.ax1.plot(
        X_NLG,
        test.AC_R.AC_CSD_ellipse.max,
        color = 'blue',
        label = 'ellipse max',
        ls = '--'
    )
    axB.ax1.plot(
        X_NLG,
        test.AC_R.AC_CSD_ellipse.min,
        color = 'purple',
        label = 'ellipse min',
        ls = '--',
    )
    axB.ax1.plot(
        X_NLG,
        test.AC_R.AC_CSD_ellipse.min**.25 * test.AC_R.AC_CSD_ellipse.max**.25,
        color = 'black',
        ls = '--',
        label = 'geometric mean',
    )
    axB.ax1.set_ylabel('1064 PSD/ShotN\n[quanta/Hz]')
    #axB.ax1.set_yscale('log')
    axB.ax1.legend(
        fontsize = 8,
        loc = 'center left'
    )
    axB.ax2.set_ylabel('532  PSD/ShotN\n[quanta/Hz]')
    axB.ax2.plot(
        X_NLG,
        test.AC_G.AC_CSD_IQ[0, 0],
        color = 'green',
        label = 'amplitude quadrature',
    )
    axB.ax2.plot(
        X_NLG,
        test.AC_G.AC_CSD_IQ[1, 1],
        color = 'blue',
        label = 'phase quadrature',
    )
    axB.ax2.plot(
        X_NLG,
        test.AC_G.AC_CSD_ellipse.max,
        color = 'cyan',
        label = 'ellipse max',
        ls = '--',
    )
    axB.ax2.plot(
        X_NLG,
        test.AC_G.AC_CSD_ellipse.min,
        color = 'purple',
        label = 'ellipse min',
        ls = '--',
    )
    axB.ax2.plot(
        X_NLG,
        test.AC_G.AC_CSD_ellipse.min**.5 * test.AC_G.AC_CSD_ellipse.max**.5,
        color = 'black',
        label = 'geometric mean',
        ls = '--',
    )
    axB.ax2.set_xlabel('Crystal Total Nonlinear Gain [rtW / W]')
    axB.ax2.legend(
        fontsize = 8,
        loc = 'center left'
    )
    return axB
