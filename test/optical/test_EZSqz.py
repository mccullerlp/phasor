# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import declarative

from phasor import system
from phasor import optics

import pytest
pytestmark = pytest.mark.skip('optics.EZSqz still WIP')
#pytest.skip("Want to skip!")

#from phasor.utilities.np import logspaced


def gensys(
        F_AC_Hz,
        loss_EM = 0,
        loss_BS = 0,
):
    sys = system.BGSystem()
    sled = sys
    sled.own.sqz = optics.EZSqz(
        rel_variance_1 = .1,
        rel_variance_2 = 12,
    )
    #sled.own.sqz = optics.EZSqz(
    #    nonlinear_power_gain = 10,
    #    loss = .1,
    #)

    sled.own.PSL = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
    )

    sled.own.mX = optics.Mirror(
        T_hr = 0,
        L_hr = loss_EM,
    )
    sled.own.mY = optics.Mirror(
        T_hr = 0,
        L_hr = loss_EM,
    )
    #T_hr = sys.optical_harmonic_value(.3),
    sled.own.mBS = optics.Mirror(
        T_hr = .5,
        L_hr = loss_BS,
        AOI_deg = 45,
    )

    sled.own.sX = optics.Space(
        1,
        L_detune_m = 1064e-9 / 8,
    )
    sled.own.sY = optics.Space(
        1,
        L_detune_m = 0,
    )

    sled.own.symPD = optics.MagicPD()
    sled.own.asymPD = optics.PD()

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

    #vterm = VacuumTerminator(name = 'vterm')
    #sys.optical_link_sequence_StoN(
    #    vterm, mBS,
    #)

    sys.AC_freq(F_AC_Hz)
    sys.DC_readout_add('sym_DC', sled.symPD.Wpd.o)
    sys.DC_readout_add('asym_DC', sled.asymPD.Wpd.o)
    sys.AC_sensitivity_add('asym_Drive', sled.mX.posZ.i, sled.asymPD.Wpd.o)
    return declarative.Bunch(locals())

def test_mich():
    b = gensys(
        #F_AC_Hz = logspaced(.001, 1e6, 10),
        F_AC_Hz = np.array([0]),
    )
    sys = b.sys
    sys.solve_to_order(1, no_AC = True)
    print()
    sys.solve_to_order(2)
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution_vector_print()
    print("sym_DC",  sys.DC_readout('sym_DC'))
    print("asym_DC", sys.DC_readout('asym_DC'))

    ptot = sys.DC_readout('sym_DC') + sys.DC_readout('asym_DC')
    pfrac = sys.DC_readout('asym_DC') / ptot
    sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

    AC = sys.AC_sensitivity('asym_Drive')
    print("ACmag:", abs(AC) / sense)
    print("ACdeg:", np.angle(AC, deg = True))

    E1064_J = 1.2398 / 1.064 / 6.24e18
    N_expect = (sys.DC_readout('asym_DC') * E1064_J)**.5
    AC_noise = sys.AC_noise('asym_Drive')
    print("ACnoise", AC_noise)
    print("ACnoise_rel", (N_expect / AC_noise)**2)

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
        F_AC_Hz = np.array([0]),
        #loss_EM = .2,
        loss_BS = .2,
    )
    sys = b.sys
    sys.solve_to_order(1, no_AC = True)
    print()
    sys.solve_to_order(2)
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution_vector_print()
    print("sym_DC",  sys.DC_readout('sym_DC'))
    print("asym_DC", sys.DC_readout('asym_DC'))

    ptot = sys.DC_readout('sym_DC') + sys.DC_readout('asym_DC')
    pfrac = sys.DC_readout('asym_DC') / ptot
    sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

    AC = sys.AC_sensitivity('asym_Drive')
    print("ACmag:", abs(AC) / sense)
    print("ACdeg:", np.angle(AC, deg = True))

    E1064_J = 1.2398 / 1.064 / 6.24e18
    N_expect = (sys.DC_readout('asym_DC') * E1064_J)**.5
    AC_noise = sys.AC_noise('asym_Drive')
    print("ACnoise", AC_noise)
    print("ACnoise_rel", (N_expect / AC_noise)**2)

    sys.port_set_print(b.mX._LFr.i)
    #print("X")
    #sys.coupling_matrix_inv_print(select_from = b.mBS._LBkB.i)

    #print("X")
    #sys.coupling_matrix_print(select_to = b.mBS._LFrB.i)

    #from phasor.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
    #F.save('trans_xfer_mich')

if __name__ == '__main__':
    test_mich()
