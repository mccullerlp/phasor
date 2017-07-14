# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
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
        self.own.PSLG = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 0.,
            multiple = 2,
            phase_deg = 90,
        )
        self.own.PSLR = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        self.own.PSLGs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            multiple = 2,
            phase_deg = 90,
        )
        self.own.PSLRs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )

        self.own.PD_R = optics.MagicPD()
        self.own.PD_G = optics.MagicPD()
        self.own.ditherAM = optics.AM()

        self.own.ktp = optics.NonlinearCrystal(
            nlg = .1,
            length_mm = 10,
            N_ode = 20,
        )

        self.own.mDC1 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )
        self.own.mDC2 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )
        self.own.hPD_R = optics.HiddenVariableHomodynePD(
            source_port = self.PSLRs.po_Fr.o,
            include_quanta = True,
        )
        self.own.hPD_G = optics.HiddenVariableHomodynePD(
            source_port = self.PSLGs.po_Fr.o,
            include_quanta = True,
        )

        self.PSLR.po_Fr.bond_sequence(
            self.mDC1.po_BkA,
            self.ditherAM.po_Fr,
            self.ktp.po_Fr,
            self.mDC2.po_FrA,
            self.PD_R.po_Fr,
            self.hPD_R.po_Fr,
        )
        self.PSLG.po_Fr.bond_sequence(
            self.mDC1.po_BkB,
        )
        self.mDC2.po_FrB.bond_sequence(
            self.PD_G.po_Fr,
            self.hPD_G.po_Fr,
        )

        self.own.DC_R = readouts.DCReadout(
            port = self.PD_R.Wpd.o,
        )
        self.own.DC_G = readouts.DCReadout(
            port = self.PD_G.Wpd.o,
        )
        if self.ctree.setdefault('include_AC', True):
            self.own.AC_G = readouts.HomodyneACReadout(
                portNI = self.hPD_G.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherAM.Drv.i,
            )
            self.own.AC_R = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_R.rtQuantumQ.o,
                portD  = self.ditherAM.Drv.i,
            )
            self.own.AC_RGI = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumI.o,
                portD  = self.ditherAM.Drv.i,
            )
            self.own.AC_RGQ = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumQ.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherAM.Drv.i,
            )
            self.own.AC_N = readouts.NoiseReadout(
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
#print("pe_A")
#pprint(self.ctree.test.PSL)
#print("self.DC_R.DC_readout", self.DC_R.DC_readout, 2)
#print("self.DC_G.DC_readout", self.DC_G.DC_readout, 1)

class SHGTestStandResonant(optics.OpticalCouplerBase):
    def __build__(self):
        super(SHGTestStandResonant, self).__build__()
        self.own.PSLR = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        self.own.PSLGs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            multiple = 2,
            phase_deg = 90,
        )
        self.own.PSLRs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )

        self.own.PD_R = optics.MagicPD()
        self.own.PD_G = optics.MagicPD()
        self.own.ditherPM = optics.PM()
        self.own.faraday = optics.OpticalCirculator(
            N_ports = 3,
        )

        self.own.mDC1 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = .10,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
                flip_sign = True,
            ),
            AOI_deg = 0,
        )
        self.own.S1 = optics.Space(L_m = 0, L_detune_m = 1064e-9 / 4)
        self.own.ktp = optics.NonlinearCrystal(
            nlg = .1,
            length_mm = 10,
            N_ode = 100,
        )
        self.own.S2 = optics.Space(L_m = 0, L_detune_m = -1064e-9 / 4)
        self.own.mDC2 = optics.HarmonicMirror(
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
        self.own.Sg = optics.Space(L_m = 0, L_detune_m = 0)
        self.own.mirror_gres = optics.Mirror(
            T_hr      = 1,
            L_hr      = .000,
            flip_sign = False,
            AOI_deg   = 0,
        )
        self.own.hPD_R = optics.HiddenVariableHomodynePD(
            source_port = self.PSLRs.po_Fr.o,
            include_quanta = True,
        )
        self.own.hPD_G = optics.HiddenVariableHomodynePD(
            source_port = self.PSLGs.po_Fr.o,
            include_quanta = True,
        )

        self.PSLR.po_Fr.bond_sequence(
            self.ditherPM.po_Fr,
            self.faraday.P0,
        )
        self.faraday.P1.bond_sequence(
            self.mDC1.po_FrA,
            self.S1.po_Fr,
            self.ktp.po_Fr,
            self.S2.po_Fr,
            self.mDC2.po_FrA,
            self.Sg.po_Fr,
            self.mirror_gres.po_Fr,
            self.PD_G.po_Fr,
            self.hPD_G.po_Fr,
        )
        self.faraday.P2.bond_sequence(
            self.PD_R.po_Fr,
            self.hPD_R.po_Fr,
        )

        self.own.DC_R = readouts.DCReadout(
            port = self.PD_R.Wpd.o,
        )
        self.own.DC_G = readouts.DCReadout(
            port = self.PD_G.Wpd.o,
        )
        if self.ctree.setdefault('include_AC', True):
            self.own.AC_G = readouts.HomodyneACReadout(
                portNI = self.hPD_G.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.own.AC_R = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_R.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.own.AC_RGI = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumI.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.own.AC_RGQ = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumQ.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.own.AC_N = readouts.NoiseReadout(
                port_map = dict(
                    RI = self.hPD_R.rtQuantumI.o,
                    RQ = self.hPD_R.rtQuantumQ.o,
                    GI = self.hPD_G.rtQuantumI.o,
                    GQ = self.hPD_G.rtQuantumQ.o,
                )
            )

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


class OPOTestStandResonant(optics.OpticalCouplerBase):
    def __build__(self):
        super(OPOTestStandResonant, self).__build__()
        self.own.PSLG = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = .02,
            multiple = 2,
            phase_deg = 0,
        )
        self.own.PSLGs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            multiple = 2,
            phase_deg = 90,
        )
        self.own.PSLRs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
            phase_deg = 45,
        )

        self.own.PD_R = optics.MagicPD()
        self.own.PD_G = optics.MagicPD()

        self.own.F_PM = base.Frequency(
            F_Hz  = 1e6,
            order = 1,
        )
        self.own.generateF_PM = signals.SignalGenerator(
            F = self.F_PM,
            amplitude = .1,
        )

        self.own.generateF_PMRead = signals.SignalGenerator(
            F = self.F_PM,
            amplitude = 0,
        )

        self.own.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 200,
            name = "PSL",
        )

        self.own.EOM = optics.PM()

        self.own.ditherPM = optics.PM()
        self.ditherPM.Drv.bond(self.generateF_PM.ps_Out)

        self.own.ditherPMRead = optics.PM()
        self.ditherPMRead.Drv.bond(self.generateF_PMRead.ps_Out)

        self.own.faraday = optics.OpticalCirculator(
            N_ports = 3,
        )

        self.own.mDC1 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 0,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = .1,
                flip_sign = True,
            ),
            AOI_deg = 0,
        )
        self.own.S1 = optics.Space(L_m = 0, L_detune_m = 1064e-9 / 4)
        self.own.ktp = optics.NonlinearCrystal(
            nlg = .1,
            length_mm = 10,
            N_ode = 100,
        )
        self.own.S2 = optics.Space(L_m = 0, L_detune_m = -1064e-9 / 4)
        self.own.mDC2 = optics.HarmonicMirror(
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
        self.PSLRs.po_Fr.bond(self.own.ditherPMRead.po_Fr)
        self.own.hPD_R = optics.HiddenVariableHomodynePD(
            source_port = self.ditherPMRead.po_Bk.o,
            include_quanta = True,
        )
        self.own.hPD_G = optics.HiddenVariableHomodynePD(
            source_port = self.PSLGs.po_Fr.o,
            include_quanta = True,
        )

        self.PSLG.po_Fr.bond_sequence(
            self.ditherPM.po_Fr,
            self.faraday.P0,
        )
        self.faraday.P1.bond_sequence(
            self.mDC1.po_FrA,
            self.S1.po_Fr,
            self.ktp.po_Fr,
            self.S2.po_Fr,
            self.mDC2.po_FrA,
            self.PD_R.po_Fr,
            self.hPD_R.po_Fr,
        )
        self.faraday.P2.bond_sequence(
            self.PD_G.po_Fr,
            self.hPD_G.po_Fr,
        )

        self.own.DC_R = readouts.DCReadout(
            port = self.PD_R.Wpd.o,
        )
        self.own.DC_G = readouts.DCReadout(
            port = self.PD_G.Wpd.o,
        )
        if self.ctree.setdefault('include_AC', True):
            self.own.AC_G = readouts.HomodyneACReadout(
                portNI = self.hPD_G.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.own.AC_R = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_R.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.own.AC_RGI = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumI.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.own.AC_RGQ = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumQ.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.own.AC_N = readouts.NoiseReadout(
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
