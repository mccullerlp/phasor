# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from numpy import testing as np_test

import numpy as np
import declarative

from phasor import system
from phasor import optics
from phasor import readouts

#from phasor.utilities.np import logspaced


def gensys(
        F_AC_Hz,
        loss_EM = 0,
        loss_BS = 0,
        detune_frac = .0001,
):
    db = declarative.DeepBunch()
    db.environment.F_AC.order = 1
    sys = system.BGSystem(
        ctree = db
    )
    sys = sys
    sys.own.PSL = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
    )

    sys.own.mX = optics.Mirror(
        T_hr = 0,
        L_hr = loss_EM,
    )
    sys.own.mY = optics.Mirror(
        T_hr = 0,
        L_hr = loss_EM,
    )
    #T_hr = sys.optical_harmonic_value(.3),
    sys.own.mBS = optics.Mirror(
        T_hr = .5,
        L_hr = loss_BS,
        AOI_deg = 45,
    )

    sys.own.sX = optics.Space(
        L_m = 1,
        L_detune_m = 1064e-9 / 4 * detune_frac,
    )
    sys.own.sY = optics.Space(
        L_m = 1,
        L_detune_m = 0,
    )

    sys.own.symPD = optics.MagicPD()
    sys.own.ASPDHD = optics.HiddenVariableHomodynePD(
        source_port     = sys.PSL.po_Fr.o,
        phase_deg       = 90,
        #include_quanta  = True,
        #facing_cardinal = 'N',
    )
    sys.own.asymPD = optics.PD()

    sys.bond_sequence(
        sys.PSL.po_Fr,
        sys.symPD.po_Bk,
        sys.mBS.po_FrA,
        sys.sX.po_Fr,
        sys.mX.po_Fr,
    )
    sys.bond_sequence(
        sys.asymPD.po_Fr,
        sys.ASPDHD.po_Bk,
        sys.mBS.po_BkB,
        sys.sY.po_Fr,
        sys.mY.po_Fr,
    )

    sys.own.sym_DC = readouts.DCReadout(
        port = sys.symPD.Wpd.o,
    )
    sys.own.asym_DC = readouts.DCReadout(
        port = sys.asymPD.Wpd.o,
    )
    sys.own.asym_drive = readouts.ACReadout(
        portD = sys.mX.Z.d.o,
        portN = sys.asymPD.Wpd.o,
    )
    sys.own.asymHD_drive = readouts.ACReadout(
        portD = sys.mX.Z.d.o,
        portN = sys.ASPDHD.rtWpdI.o,
    )
    sys.own.asymHDHD_drive = readouts.HomodyneACReadout(
        portD = sys.mX.Z.d.o,
        portNI = sys.ASPDHD.rtWpdI.o,
        portNQ = sys.ASPDHD.rtWpdI.o,
    )
    return declarative.Bunch(locals())


def test_mich():
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
    print("pfrac", pfrac)
    sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

    AC = sys.asym_drive.AC_sensitivity
    print("sense", sense)
    print("AC mag rel expect:", abs(AC) / sense)
    np_test.assert_almost_equal(abs(AC) / sense, 1, 5)
    print("AC phase :", np.angle(AC, deg = True))

    E1064_J = 1.2398 / 1.064 / 6.24e18
    N_expect = (2 * sys.asym_DC.DC_readout * E1064_J)**.5
    AC_noise = sys.asym_drive.AC_ASD
    print("ACnoise", AC_noise)
    print("ACnoise_rel", (AC_noise / N_expect)**2)

    for source, psd in sys.asym_drive.AC_PSD_by_source.items():
        print(source, psd)

    np_test.assert_almost_equal(N_expect / AC_noise, 1, 3)

    print("ACnoise m_rtHz", sys.asym_drive.AC_noise_limited_sensitivity)

    print("ACnoise m_rtHz", sys.asymHD_drive.AC_noise_limited_sensitivity)
    srel = 4 * np.pi * sys.F_carrier_1064.iwavelen_m / (2 * ptot * E1064_J)**.5
    np_test.assert_almost_equal(sys.asymHD_drive.AC_noise_limited_sensitivity * srel, 1, 3)

    srel = 4 * np.pi * sys.F_carrier_1064.iwavelen_m / (2 * ptot * E1064_J)**.5
    print("ACnoise m_rtHz", sys.asymHDHD_drive.AC_noise_limited_sensitivity)
    np_test.assert_almost_equal(sys.asymHDHD_drive.AC_noise_limited_sensitivity * srel, 1, 3)
    #sys.port_set_print(b.mBS.po_BkB.i)
    #sys.port_set_print(b.vterm.po_Fr.o)
    #sys.coupling_matrix_inv_print(select_to = b.asymPD.Wpd.o)

    #from phasor.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
    #F.save('trans_xfer_mich')

def test_mich_lossy():
    b = gensys(
        #F_AC_Hz = logspaced(.001, 1e6, 10),
        F_AC_Hz = np.array([0, 10, 100]),
        loss_EM = .2,
        detune_frac = np.array([0.001, 0.01, 0.1, .5, .9]),
        #loss_BS = .2,
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
    N_expect = (2 * sys.asym_DC.DC_readout * E1064_J)**.5
    AC_noise = sys.asym_drive.AC_ASD
    print("ACnoise", AC_noise)
    print("ACnoise_rel", (N_expect / AC_noise)**2)
    np_test.assert_almost_equal(N_expect / AC_noise, 1, 3)

    print("ACnoise m_rtHz", sys.asym_drive.AC_noise_limited_sensitivity)
    #sys.port_set_print(b.mBS.po_BkB.i)
    #sys.port_set_print(b.vterm.po_Fr.o)
    #sys.coupling_matrix_inv_print(select_to = b.asymPD.Wpd.o)

    #from phasor.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
    #F.save('trans_xfer_mich')


if __name__ == '__main__':
    test_mich_lossy()
