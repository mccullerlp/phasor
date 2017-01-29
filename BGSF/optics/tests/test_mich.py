"""
"""
from __future__ import (division, print_function)

from unittest import TestCase, main

import numpy as np

from declarative.bunch import (
    Bunch,
)

from BGSF import system
from BGSF import optics
from BGSF import readouts

#from BGSF.utilities.np import logspaced


def gensys(
        F_AC_Hz,
        loss_EM = 0,
        loss_BS = 0,
):
    sys = system.BGSystem()
    sys = sys
    sys.my.PSL = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
    )

    sys.my.mX = optics.Mirror(
        T_hr = 0,
        L_hr = loss_EM,
    )
    sys.my.mY = optics.Mirror(
        T_hr = 0,
        L_hr = loss_EM,
    )
    #T_hr = sys.optical_harmonic_value(.3),
    sys.my.mBS = optics.Mirror(
        T_hr = .5,
        L_hr = loss_BS,
        AOI_deg = 45,
    )

    sys.my.sX = optics.Space(
        L_m = 1,
        L_detune_m = 1064e-9 / 8 * .01,
    )
    sys.my.sY = optics.Space(
        L_m = 1,
        L_detune_m = 0,
    )

    sys.my.symPD = optics.MagicPD()
    sys.my.asymPD = optics.PD()

    sys.bond_sequence(
        sys.PSL.Fr,
        sys.symPD.Bk,
        sys.mBS.FrA,
        sys.sX.Fr,
        sys.mX.Fr,
    )
    sys.bond_sequence(
        sys.asymPD.Fr,
        sys.mBS.BkB,
        sys.sY.Fr,
        sys.mY.Fr,
    )

    sys.my.sym_DC = readouts.DCReadout(
        port = sys.symPD.Wpd.o,
    )
    sys.my.asym_DC = readouts.DCReadout(
        port = sys.asymPD.Wpd.o,
    )
    sys.my.asym_drive = readouts.ACReadout(
        portD = sys.mX.posZ.i,
        portN = sys.asymPD.Wpd.o,
    )
    return Bunch(locals())


class TestMichelson(TestCase):
    def test_mich(self):
        b = gensys(
            #F_AC_Hz = logspaced(.001, 1e6, 10),
            F_AC_Hz = np.array([0]),
        )
        sys = b.sys
        #sys.solve_to_order(1)
        #print()
        #sys.coupling_matrix_print()
        #sys.source_vector_print()
        #sys.solution_vector_print()
        print("sym_DC",  sys.sym_DC.DC_readout)
        print("asym_DC", sys.asym_DC.DC_readout)

        ptot = sys.sym_DC.DC_readout + sys.asym_DC.DC_readout
        pfrac = sys.asym_DC.DC_readout / ptot
        sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

        AC = sys.asym_drive.AC_sensitivity
        print("AC mag rel expect:", abs(AC) / sense)
        self.assertAlmostEqual(abs(AC), sense, 5)
        print("AC phase :", np.angle(AC, deg = True))

        E1064_J = 1.2398 / 1.064 / 6.24e18
        N_expect = (2 * sys.asym_DC.DC_readout * E1064_J)**.5
        AC_noise = sys.asym_drive.AC_ASD
        print("ACnoise", AC_noise)
        print("ACnoise_rel", (N_expect / AC_noise)**2)
        self.assertAlmostEqual(N_expect, AC_noise, 5)

        print("ACnoise m_rtHz", sys.asym_drive.AC_noise_limited_sensitivity)
        #sys.port_set_print(b.mBS.BkB.i)
        #sys.port_set_print(b.vterm.Fr.o)
        #sys.coupling_matrix_inv_print(select_to = b.asymPD.Wpd.o)

        #from BGSF.utilities.mpl.autoniceplot import (mplfigB)
        #F = mplfigB(Nrows = 2)
        #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
        #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
        #F.save('trans_xfer_mich')

    def test_mich_lossy(self):
        b = gensys(
            #F_AC_Hz = logspaced(.001, 1e6, 10),
            F_AC_Hz = np.array([0]),
            #loss_EM = .2,
            loss_BS = .2,
        )
        sys = b.sys
        #sys.coupling_matrix_print()
        #sys.source_vector_print()
        #sys.solution_vector_print()
        print("sym_DC",  sys.sym_DC.DC_readout)
        print("asym_DC", sys.asym_DC.DC_readout)

        ptot = sys.sym_DC.DC_readout + sys.asym_DC.DC_readout
        pfrac = sys.asym_DC.DC_readout / ptot
        sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

        AC = sys.asym_drive.AC_sensitivity
        print("AC mag rel expect:", abs(AC) / sense)

        #TODO account for the sensitivity loss from the loss here
        #self.assertAlmostEqual(abs(AC), sense, 5)
        print("AC phase :", np.angle(AC, deg = True))

        E1064_J = 1.2398 / 1.064 / 6.24e18
        N_expect = (sys.asym_DC.DC_readout * E1064_J)**.5
        AC_noise = sys.asym_drive.AC_ASD
        print("ACnoise", AC_noise)
        print("ACnoise_rel", (N_expect / AC_noise)**2)
        self.assertAlmostEqual(N_expect, AC_noise, 5)

        print("ACnoise m_rtHz", sys.asym_drive.AC_noise_limited_sensitivity)
        #sys.port_set_print(b.mBS.BkB.i)
        #sys.port_set_print(b.vterm.Fr.o)
        #sys.coupling_matrix_inv_print(select_to = b.asymPD.Wpd.o)

        #from BGSF.utilities.mpl.autoniceplot import (mplfigB)
        #F = mplfigB(Nrows = 2)
        #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
        #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
        #F.save('trans_xfer_mich')


if __name__ == '__main__':
    main()
